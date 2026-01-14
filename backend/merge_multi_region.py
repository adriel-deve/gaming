"""
Merge existing US/BR data with new NoA (US, CA, MX) prices
"""
import json

print("="*60)
print("MERGING MULTI-REGION DATA")
print("="*60)

# Load existing US/BR data
with open('all_27_countries_prices.json', 'r', encoding='utf-8') as f:
    us_br_data = json.load(f)
print(f"\n[OK] Loaded {len(us_br_data)} games (US/BR)")

# Load NoA enriched data (US, CA, MX) - usar arquivo completo
import os
noa_file = 'noa_progress_all.json' if os.path.exists('noa_progress_all.json') else 'noa_progress.json'
with open(noa_file, 'r', encoding='utf-8') as f:
    noa_data = json.load(f)
print(f"[OK] Loaded {len(noa_data)} games from {noa_file}")

# Create map by title for matching
noa_map = {game['title'].lower(): game for game in noa_data}

# Merge data
merged_count = 0
new_prices_added = 0

for game in us_br_data:
    title_key = game['title'].lower()

    if title_key in noa_map:
        # Game found in NoA data - merge prices
        noa_game = noa_map[title_key]

        # Get existing regions
        existing_regions = {p['region'] for p in game['prices']}

        # Add new regions (CA, MX) - skip US as we already have it
        for price in noa_game['prices']:
            if price['region'] not in existing_regions:
                game['prices'].append(price)
                new_prices_added += 1

        merged_count += 1

print(f"\n[OK] Merged {merged_count} games")
print(f"[OK] Added {new_prices_added} new regional prices")

# Statistics
region_counts = {}
for game in us_br_data:
    count = len(game['prices'])
    region_counts[count] = region_counts.get(count, 0) + 1

print("\nGames by number of regions:")
for count in sorted(region_counts.keys(), reverse=True):
    print(f"  {count} regions: {region_counts[count]} games")

# Save merged data
output_file = 'multi_region_enriched.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(us_br_data, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Saved to: {output_file}")
print(f"[OK] Total: {len(us_br_data)} games")

# Show examples of games with most regions
print("\n" + "="*60)
print("TOP GAMES WITH MOST REGIONS:")
print("="*60)

multi_region_games = sorted(
    [g for g in us_br_data if len(g['prices']) >= 4],
    key=lambda x: len(x['prices']),
    reverse=True
)[:5]

for game in multi_region_games:
    print(f"\n{game['title']}")
    print(f"  Regions: {len(game['prices'])}")

    # Sort by price (cheapest first)
    sorted_prices = sorted(game['prices'], key=lambda x: x['price_brl'])

    for price in sorted_prices:
        discount_text = f" (SALE -{price['discount_percent']}%)" if price['discount_percent'] > 0 else ""
        print(f"    {price['region']:3s}: {price['currency']} {price['sale_price']:7.2f} = R$ {price['price_brl']:7.2f}{discount_text}")

print("\n" + "="*60)
print("DONE!")
print("="*60)
