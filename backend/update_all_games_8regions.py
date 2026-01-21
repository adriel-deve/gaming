"""
Update pages with ALL games and 8-region comparison (Americas)
Creates: data/all-games-8regions.json with full price comparison
Regions: BR, US, CA, MX, AR, CL, CO, PE
"""
import json
import os

print("="*60)
print("UPDATING ALL GAMES WITH 8-REGION COMPARISON (AMERICAS)")
print("="*60)

# All Americas regions
REGIONS = ['BR', 'US', 'CA', 'MX', 'AR', 'CL', 'CO', 'PE']

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
        if region not in REGIONS:
            continue

        price_brl = price.get('price_brl', 0)
        if price_brl <= 0:
            continue

        # Keep best price per region (in case of duplicates)
        if region not in prices_by_region or price_brl < prices_by_region[region]['price_brl']:
            prices_by_region[region] = {
                'currency': price['currency'],
                'msrp': price['msrp'],
                'sale_price': price['sale_price'],
                'msrp_brl': price.get('msrp_brl', price['msrp']),
                'price_brl': price_brl,
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
        'cheapest_price_brl': round(cheapest_price['price_brl'], 2),
        'max_discount': max_discount,
        'num_regions': len(prices_by_region),
        'prices': {}
    }

    # Add each region's price
    for region in REGIONS:
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

# Cheapest region stats
cheapest_stats = {}
for game in all_games_data:
    r = game['cheapest_region']
    cheapest_stats[r] = cheapest_stats.get(r, 0) + 1

print("\nCheapest region distribution:")
for region, count in sorted(cheapest_stats.items(), key=lambda x: -x[1]):
    print(f"  {region}: {count} games")

# Save to JSON file (8 regions)
output_path = os.path.join('..', 'data', 'all-games-8regions.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_games_data, f, ensure_ascii=False, indent=None, separators=(',', ':'))

file_size = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n[OK] Saved to: {output_path}")
print(f"[OK] File size: {file_size:.2f} MB")

# Also update the 4-regions file for backwards compatibility
output_path_4 = os.path.join('..', 'data', 'all-games-4regions.json')

# Create 4-region version (BR, US, CA, MX only)
games_4regions = []
for game in all_games_data:
    game_4 = {
        'title': game['title'],
        'slug': game['slug'],
        'nsuid': game['nsuid'],
        'max_discount': game['max_discount'],
        'prices': {}
    }

    # Only include 4 main regions
    for region in ['BR', 'US', 'CA', 'MX']:
        if region in game['prices']:
            game_4['prices'][region] = game['prices'][region]

    if game_4['prices']:
        # Recalculate cheapest for 4 regions
        cheapest = min(game_4['prices'].items(), key=lambda x: x[1]['brl'])
        game_4['cheapest_region'] = cheapest[0]
        game_4['cheapest_price_brl'] = cheapest[1]['brl']
        game_4['num_regions'] = len(game_4['prices'])
        games_4regions.append(game_4)

with open(output_path_4, 'w', encoding='utf-8') as f:
    json.dump(games_4regions, f, ensure_ascii=False, indent=None, separators=(',', ':'))

print(f"[OK] Also saved 4-region version: {output_path_4}")

# Show examples
print("\n" + "="*60)
print("EXAMPLES (Games with 8 regions):")
print("="*60)

shown = 0
for game in all_games_data:
    if game['num_regions'] >= 8:
        print(f"\n{game['title']}")
        print(f"  CHEAPEST: {game['cheapest_region']} @ R$ {game['cheapest_price_brl']:.2f}")
        for region in REGIONS:
            if region in game['prices']:
                price = game['prices'][region]
                discount_str = f" (-{price['discount']}%)" if price['discount'] > 0 else ""
                cheapest_marker = " <-- BEST" if region == game['cheapest_region'] else ""
                print(f"  {region}: {price['currency']} {price['sale']:.2f} = R$ {price['brl']:.2f}{discount_str}{cheapest_marker}")
        shown += 1
        if shown >= 3:
            break

print("\n" + "="*60)
print("DONE!")
print("="*60)
