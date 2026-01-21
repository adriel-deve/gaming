"""
Update data/multi-region-prices.json for the individual game comparison page (jogo-detalhes.html)
This file is used when you click on a game to see detailed price comparison across all regions.
"""
import json
import os

print("="*60)
print("UPDATING MULTI-REGION-PRICES.JSON (Individual Game Page)")
print("="*60)

# All supported regions with their info
REGIONS_INFO = {
    # Americas
    'BR': {'name': 'Brasil', 'flag': '🇧🇷'},
    'US': {'name': 'Estados Unidos', 'flag': '🇺🇸'},
    'CA': {'name': 'Canadá', 'flag': '🇨🇦'},
    'MX': {'name': 'México', 'flag': '🇲🇽'},
    'AR': {'name': 'Argentina', 'flag': '🇦🇷'},
    'CL': {'name': 'Chile', 'flag': '🇨🇱'},
    'CO': {'name': 'Colômbia', 'flag': '🇨🇴'},
    'PE': {'name': 'Peru', 'flag': '🇵🇪'},
    # Europe
    'GB': {'name': 'Reino Unido', 'flag': '🇬🇧'},
    'DE': {'name': 'Alemanha', 'flag': '🇩🇪'},
    'FR': {'name': 'França', 'flag': '🇫🇷'},
    'ES': {'name': 'Espanha', 'flag': '🇪🇸'},
    'IT': {'name': 'Itália', 'flag': '🇮🇹'},
    'PT': {'name': 'Portugal', 'flag': '🇵🇹'},
    'AU': {'name': 'Austrália', 'flag': '🇦🇺'},
    'ZA': {'name': 'África do Sul', 'flag': '🇿🇦'},
}

# Load enriched data
print("\n[1/3] Loading enriched data...")
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] {len(games)} games loaded")

# Convert to format expected by jogo-detalhes.html
print("\n[2/3] Converting to multi-region-prices format...")

output_games = []

for game in games:
    if not game.get('prices'):
        continue

    # Filter and format prices
    prices = []
    for price in game['prices']:
        region = price.get('region')
        if region not in REGIONS_INFO:
            continue

        price_brl = price.get('price_brl', 0)
        if price_brl <= 0:
            continue

        prices.append({
            'region': region,
            'currency': price.get('currency', 'USD'),
            'msrp': round(price.get('msrp', 0), 2),
            'sale_price': round(price.get('sale_price', price.get('msrp', 0)), 2),
            'discount_percent': price.get('discount_percent', 0),
            'price_brl': round(price_brl, 2),
            'msrp_brl': round(price.get('msrp_brl', price_brl), 2),
            'on_sale': price.get('on_sale', False)
        })

    if not prices:
        continue

    # Sort by price_brl (cheapest first)
    prices.sort(key=lambda x: x['price_brl'])

    output_games.append({
        'title': game['title'],
        'slug': game.get('slug', ''),
        'nsuid': game.get('nsuid', ''),
        'prices': prices
    })

print(f"[OK] {len(output_games)} games with prices")

# Count by region
region_count = {}
for game in output_games:
    for price in game['prices']:
        region = price['region']
        region_count[region] = region_count.get(region, 0) + 1

print("\nPrices by region:")
for region, count in sorted(region_count.items(), key=lambda x: -x[1]):
    name = REGIONS_INFO.get(region, {}).get('name', region)
    print(f"  {region} ({name}): {count}")

# Save
print("\n[3/3] Saving...")
output_path = os.path.join('..', 'data', 'multi-region-prices.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_games, f, ensure_ascii=False, separators=(',', ':'))

file_size = os.path.getsize(output_path) / (1024 * 1024)
print(f"[OK] Saved to: {output_path}")
print(f"[OK] File size: {file_size:.2f} MB")

# Show example
print("\n" + "="*60)
print("EXAMPLE: First game with multiple regions")
print("="*60)

for game in output_games:
    if len(game['prices']) >= 10:
        print(f"\n{game['title']} ({len(game['prices'])} regions)")
        for price in game['prices'][:8]:
            name = REGIONS_INFO.get(price['region'], {}).get('name', price['region'])
            discount_str = f" (-{price['discount_percent']}%)" if price['discount_percent'] > 0 else ""
            print(f"  {price['region']} ({name}): {price['currency']} {price['sale_price']:.2f} = R$ {price['price_brl']:.2f}{discount_str}")
        if len(game['prices']) > 8:
            print(f"  ... and {len(game['prices']) - 8} more regions")
        break

print("\n" + "="*60)
print("DONE!")
print("="*60)
