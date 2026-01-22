"""
Save daily price snapshot to Neon PostgreSQL
Run this daily via GitHub Actions to build price history for charts
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
    exit(1)

print("="*60)
print("SAVING DAILY PRICE SNAPSHOT TO NEON")
print(f"Date: {date.today()}")
print("="*60)

# Connect
print("\n[1/3] Connecting to Neon...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cursor = conn.cursor()
    print("[OK] Connected!")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    exit(1)

# Load JSON data
print("\n[2/3] Loading JSON data...")
json_path = os.path.join(os.path.dirname(__file__), '..', 'multi_region_enriched.json')
with open(json_path, 'r', encoding='utf-8') as f:
    games_data = json.load(f)
print(f"[OK] Loaded {len(games_data)} games")

# Prepare data
print("\n[3/3] Saving prices...")
prices_dict = {}
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
print(f"  {len(prices_data)} prices to save...")

try:
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

    conn.commit()
    print(f"[OK] {total} prices saved")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] Failed: {e}")
    exit(1)

# Also update images (in case new games were added)
print("\n  Updating images...")
images_data = []
for game in games_data:
    slug = game.get('slug', '')
    image = game.get('image', '')
    if slug and image:
        images_data.append((slug, image))

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
    print(f"[OK] {len(images_data)} images updated")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] Images failed: {e}")

# Stats
cursor.execute("SELECT COUNT(*) FROM price_history")
total_records = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(DISTINCT recorded_at) FROM price_history")
total_days = cursor.fetchone()[0]

print("\n" + "="*60)
print(f"Total price records: {total_records}")
print(f"Days of history: {total_days}")
print("="*60)

cursor.close()
conn.close()
