"""
Update pages with ALL games and 4-region comparison
Creates: data/all-games-4regions.json with full price comparison
"""
import json
import os

print("="*60)
print("UPDATING ALL GAMES WITH 4-REGION COMPARISON")
print("="*60)

# Load multi-region data
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"\n[OK] Loaded {len(games)} games")

# Process all games with full regional data
all_games_data = []

for game in games:
    if not game.get('prices'):
        continue

    # Organize prices by region
    prices_by_region = {}
    for price in game['prices']:
        region = price['region']
        # Keep best price per region (in case of duplicates)
        if region not in prices_by_region or price['price_brl'] < prices_by_region[region]['price_brl']:
            prices_by_region[region] = {
                'currency': price['currency'],
                'msrp': price['msrp'],
                'sale_price': price['sale_price'],
                'msrp_brl': price['msrp_brl'],
                'price_brl': price['price_brl'],
                'discount_percent': price.get('discount_percent', 0),
                'on_sale': price.get('on_sale', price.get('discount_percent', 0) > 0)
            }

    if not prices_by_region:
        continue

    # Find cheapest overall
    cheapest_region = min(prices_by_region.keys(), key=lambda r: prices_by_region[r]['price_brl'])
    cheapest_price = prices_by_region[cheapest_region]

    # Find best discount
    max_discount = max((p['discount_percent'] for p in prices_by_region.values()), default=0)

    game_data = {
        'title': game['title'],
        'slug': game.get('slug', ''),
        'nsuid': game.get('nsuid', ''),
        'cheapest_region': cheapest_region,
        'cheapest_price_brl': cheapest_price['price_brl'],
        'max_discount': max_discount,
        'num_regions': len(prices_by_region),
        'prices': {}
    }

    # Add each region's price
    for region in ['BR', 'US', 'CA', 'MX']:
        if region in prices_by_region:
            p = prices_by_region[region]
            game_data['prices'][region] = {
                'currency': p['currency'],
                'msrp': round(p['msrp'], 2),
                'sale': round(p['sale_price'], 2),
                'brl': round(p['price_brl'], 2),
                'discount': p['discount_percent'],
                'on_sale': p.get('on_sale', p['discount_percent'] > 0)
            }

    all_games_data.append(game_data)

# Sort by best deals (highest discount first, then lowest price)
all_games_data.sort(key=lambda x: (-x['max_discount'], x['cheapest_price_brl']))

print(f"[OK] Processed {len(all_games_data)} games with prices")

# Statistics
region_count = {}
for game in all_games_data:
    count = game['num_regions']
    region_count[count] = region_count.get(count, 0) + 1

print("\nGames by region count:")
for count in sorted(region_count.keys(), reverse=True):
    print(f"  {count} regions: {region_count[count]} games")

# Save to JSON file
output_path = os.path.join('..', 'data', 'all-games-4regions.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_games_data, f, ensure_ascii=False, indent=None, separators=(',', ':'))

file_size = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n[OK] Saved to: {output_path}")
print(f"[OK] File size: {file_size:.2f} MB")

# Show examples
print("\n" + "="*60)
print("EXAMPLES (Games with 4 regions):")
print("="*60)

for game in all_games_data[:5]:
    if game['num_regions'] >= 4:
        print(f"\n{game['title']}")
        print(f"  Best: {game['cheapest_region']} @ R$ {game['cheapest_price_brl']:.2f}")
        for region, price in game['prices'].items():
            discount_str = f" (-{price['discount']}%)" if price['discount'] > 0 else ""
            print(f"  {region}: {price['currency']} {price['sale']:.2f} = R$ {price['brl']:.2f}{discount_str}")

print("\n" + "="*60)
print("DONE!")
print("="*60)
