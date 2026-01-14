"""
Update pages with multi-region data
Uses: multi_region_enriched.json (BR, US, CA, MX)
"""
import json
import os

print("="*60)
print("UPDATING PAGES WITH MULTI-REGION DATA")
print("="*60)

# Load multi-region data
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"\n[OK] Loaded {len(games)} games")

# Filter games that have prices and sort by best deal
games_with_prices = []

for game in games:
    if not game['prices']:
        continue

    # Find cheapest price in BRL
    cheapest = min(game['prices'], key=lambda x: x['price_brl'])

    # Calculate best discount
    max_discount = max((p['discount_percent'] for p in game['prices']), default=0)

    games_with_prices.append({
        'title': game['title'],
        'slug': game.get('slug', ''),
        'nsuid': game.get('nsuid', ''),
        'prices': game['prices'],
        'cheapest_price_brl': cheapest['price_brl'],
        'cheapest_region': cheapest['region'],
        'max_discount': max_discount,
        'num_regions': len(game['prices'])
    })

# Sort by best deals (highest discount first, then lowest price)
games_sorted = sorted(games_with_prices, key=lambda x: (-x['max_discount'], x['cheapest_price_brl']))

print(f"[OK] {len(games_with_prices)} games with prices")
print(f"[OK] Regions available: {len(set(p['region'] for g in games_with_prices for p in g['prices']))} (BR, US, CA, MX)")

# Statistics
region_count = {}
for game in games_with_prices:
    count = game['num_regions']
    region_count[count] = region_count.get(count, 0) + 1

print("\nGames by region count:")
for count in sorted(region_count.keys(), reverse=True):
    print(f"  {count} regions: {region_count[count]} games")

# Update nintendo.html to show multi-region games
print("\n" + "="*60)
print("UPDATING nintendo.html...")
print("="*60)

# Create games data for embedding
games_for_html = []

for game in games_sorted[:200]:  # First 200 games embedded
    # Get best price and original price
    cheapest = min(game['prices'], key=lambda x: x['price_brl'])

    # Find original price (MSRP) in same region
    original_price_brl = next(
        (p['msrp_brl'] for p in game['prices'] if p['region'] == cheapest['region']),
        cheapest['price_brl']
    )

    games_for_html.append({
        'title': game['title'].replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '').replace('\t', ' '),
        'discount_percent': game['max_discount'],
        'msrp': original_price_brl,
        'sale_price': cheapest['price_brl'],
        'currency': 'BRL',
        'region': cheapest['region'],
        'num_regions': game['num_regions'],
        'game_id': game.get('slug', '')
    })

# Generate JavaScript array
js_items = []
for g in games_for_html:
    js_item = f'{{ title: "{g["title"]}", discount_percent: {g["discount_percent"]}, msrp: {g["msrp"]:.2f}, sale_price: {g["sale_price"]:.2f}, currency: "{g["currency"]}", region: "{g["region"]}", num_regions: {g["num_regions"]}, game_id: "{g["game_id"]}" }}'
    js_items.append(js_item)

js_array = '[\n        ' + ',\n        '.join(js_items) + '\n    ]'

# Read template
template_path = os.path.join('..', 'nintendo.html')
with open(template_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Replace games array - find the return statement in getLocalGames function
import re
pattern = r'(function getLocalGames\(\) \{[\s\S]*?return \[)([\s\S]*?)(\];[\s\S]*?\})'

match = re.search(pattern, html_content)
if match:
    # Replace just the array content, keeping the function structure
    replacement = match.group(1) + '\n        ' + ',\n        '.join(js_items) + '\n      ' + match.group(3)
    html_content = re.sub(pattern, replacement, html_content)
    print("[OK] Updated getLocalGames array")
else:
    print("[WARNING] Could not find getLocalGames function to replace")

# Update stats in HTML
html_content = re.sub(
    r'Comparando: [^<]+',
    f'Comparando: BR, US, CA, MX ({len(games_with_prices):,} jogos)',
    html_content
)

# Save updated HTML
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[OK] nintendo.html updated with {len(games_for_html)} games")
print(f"[OK] Now showing 4 regions: BR, US, CA, MX")

# Also create external JSON file with ALL games
external_json_path = os.path.join('..', 'data', 'all-games.json')
with open(external_json_path, 'w', encoding='utf-8') as f:
    json.dump([{
        'title': g['title'].replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '').replace('\t', ' '),
        'discount_percent': g['max_discount'],
        'msrp': next((p['msrp_brl'] for p in g['prices'] if p['region'] == g['cheapest_region']), g['cheapest_price_brl']),
        'sale_price': g['cheapest_price_brl'],
        'currency': 'BRL',
        'region': g['cheapest_region'],
        'num_regions': g['num_regions'],
        'game_id': g.get('slug', '')
    } for g in games_sorted], f, ensure_ascii=False)

print(f"[OK] External JSON created with {len(games_sorted)} games")

print("\n" + "="*60)
print("DONE!")
print("="*60)
print("\nSummary:")
print(f"  Total games: {len(games_with_prices):,}")
print(f"  Regions: BR, US, CA, MX (4 countries)")
print(f"  Games with 4 regions: {region_count.get(4, 0)}")
print(f"  Games with 2+ regions: {sum(region_count.get(i, 0) for i in range(2, 10))}")
