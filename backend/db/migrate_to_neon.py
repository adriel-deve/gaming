"""
Migrate game images and prices to Neon PostgreSQL
Only stores: images + price history (for future charts)
Game metadata comes from Git/JSON
"""
import json
import os
import psycopg2
from psycopg2.extras import execute_values
from datetime import date

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found!")
    print("Create a .env file with: DATABASE_URL=your_connection_string")
    exit(1)

print("="*60)
print("MIGRATING TO NEON POSTGRESQL")
print("Images + Price History only")
print("="*60)

# Connect
print("\n[1/4] Connecting to Neon...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cursor = conn.cursor()
    print("[OK] Connected!")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    exit(1)

# Create schema
print("\n[2/4] Creating schema...")
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
with open(schema_path, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

try:
    cursor.execute(schema_sql)
    conn.commit()
    print("[OK] Schema created")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] Schema failed: {e}")
    exit(1)

# Load JSON data
print("\n[3/4] Loading JSON data...")
json_path = os.path.join(os.path.dirname(__file__), '..', 'multi_region_enriched.json')
with open(json_path, 'r', encoding='utf-8') as f:
    games_data = json.load(f)
print(f"[OK] Loaded {len(games_data)} games")

# Insert images
print("\n[4/4] Inserting data...")

# A) Game images
images_data = []
for game in games_data:
    slug = game.get('slug', '')
    image = game.get('image', '')
    if slug and image:
        images_data.append((slug, image))

print(f"  Inserting {len(images_data)} game images...")
try:
    execute_values(
        cursor,
        """
        INSERT INTO game_images (slug, image_url)
        VALUES %s
        ON CONFLICT (slug) DO UPDATE SET
            image_url = EXCLUDED.image_url,
            updated_at = CURRENT_TIMESTAMP
        """,
        images_data,
        template="(%s, %s)"
    )
    conn.commit()
    print(f"  [OK] {len(images_data)} images inserted")
except Exception as e:
    conn.rollback()
    print(f"  [ERROR] Images failed: {e}")

# B) Price history (today's snapshot)
print(f"  Inserting price history...")
prices_dict = {}  # Use dict to deduplicate by (slug, region, date)
today = date.today()
supported_regions = ['BR', 'US', 'CA', 'MX', 'AR', 'CL', 'CO', 'PE', 'GB', 'DE', 'FR', 'ES', 'IT', 'PT', 'AU', 'ZA']

for game in games_data:
    slug = game.get('slug', '')
    if not slug:
        continue

    for price in game.get('prices', []):
        region = price.get('region')
        if region not in supported_regions:
            continue

        price_brl = price.get('price_brl', 0)
        if price_brl <= 0:
            continue

        key = (slug, region, today)
        # Keep best price if duplicate
        if key not in prices_dict or price_brl < prices_dict[key][5]:
            prices_dict[key] = (
                slug,
                region,
                price.get('currency', 'USD'),
                round(price.get('msrp', 0), 2),
                round(price.get('sale_price', price.get('msrp', 0)), 2),
                round(price_brl, 2),
                price.get('discount_percent', 0),
                price.get('on_sale', False),
                today
            )

prices_data = list(prices_dict.values())

print(f"  Inserting {len(prices_data)} price records...")
try:
    # Insert in batches
    batch_size = 5000
    total = 0

    for i in range(0, len(prices_data), batch_size):
        batch = prices_data[i:i + batch_size]
        execute_values(
            cursor,
            """
            INSERT INTO price_history (slug, region_code, currency, msrp, sale_price, price_brl, discount_percent, on_sale, recorded_at)
            VALUES %s
            ON CONFLICT (slug, region_code, recorded_at) DO UPDATE SET
                msrp = EXCLUDED.msrp,
                sale_price = EXCLUDED.sale_price,
                price_brl = EXCLUDED.price_brl,
                discount_percent = EXCLUDED.discount_percent,
                on_sale = EXCLUDED.on_sale
            """,
            batch,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        total += len(batch)
        print(f"    {total}/{len(prices_data)}...")

    conn.commit()
    print(f"  [OK] {total} prices inserted")
except Exception as e:
    conn.rollback()
    print(f"  [ERROR] Prices failed: {e}")

# Verify
print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

cursor.execute("SELECT COUNT(*) FROM game_images")
images_count = cursor.fetchone()[0]
print(f"Game images: {images_count}")

cursor.execute("SELECT COUNT(*) FROM price_history")
prices_count = cursor.fetchone()[0]
print(f"Price records: {prices_count}")

cursor.execute("SELECT COUNT(DISTINCT slug) FROM price_history")
games_with_prices = cursor.fetchone()[0]
print(f"Games with prices: {games_with_prices}")

cursor.execute("""
    SELECT region_code, COUNT(*)
    FROM price_history
    GROUP BY region_code
    ORDER BY COUNT(*) DESC
""")
print("\nPrices by region:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Close
cursor.close()
conn.close()

print("\n" + "="*60)
print("MIGRATION COMPLETE!")
print("="*60)
print("\nDatabase stores:")
print("  - Game cover images (for display)")
print("  - Price history (for future charts)")
print("\nGame metadata (title, slug) comes from Git/JSON")
