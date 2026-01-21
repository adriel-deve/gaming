"""
Update nintendo.html with latest game prices from all-games-4regions.json
"""
import json

print("="*60)
print("UPDATING NINTENDO.HTML WITH LATEST PRICES")
print("="*60)

# Load price data
print("\n[1/4] Loading price data...")
with open('../data/all-games-4regions.json', 'r', encoding='utf-8') as f:
    games_data = json.load(f)

print(f"[OK] {len(games_data)} games loaded")

# Convert to compact JS format
print("\n[2/4] Converting to JS format...")

def to_js_object(game):
    """Convert game to compact JS object string"""
    prices_js = {}
    for region, price in game.get('prices', {}).items():
        prices_js[region] = {
            "currency": price['currency'],
            "msrp": price['msrp'],
            "sale": price['sale'],
            "brl": price['brl'],
            "discount": price['discount']
        }

    # Compact format: t=title, s=slug, d=discount, p=price_brl, r=region, n=num_regions, i=image
    obj = {
        "t": game['title'],
        "s": game.get('slug', ''),
        "i": game.get('image', ''),
        "d": game.get('max_discount', 0),
        "p": round(game.get('cheapest_price_brl', 0), 2),
        "r": game.get('cheapest_region', 'BR'),
        "n": game.get('num_regions', 1),
        "prices": prices_js
    }

    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

js_objects = []
for game in games_data:
    js_objects.append(to_js_object(game))

js_array_content = ',\n'.join(js_objects)

print(f"[OK] Converted {len(js_objects)} games")

# Read HTML file
print("\n[3/4] Updating nintendo.html...")
with open('../nintendo.html', 'r', encoding='utf-8') as f:
    html_lines = f.readlines()

# Find the start and end of allGames array
start_line = None
end_line = None

for i, line in enumerate(html_lines):
    if 'const allGames = [' in line:
        start_line = i
    if start_line is not None and '];' in line and 'allGames' not in line:
        end_line = i
        break

if start_line is None or end_line is None:
    print("[ERROR] Could not find allGames array boundaries!")
    print(f"  Start line: {start_line}")
    print(f"  End line: {end_line}")
    exit(1)

print(f"  Found array from line {start_line + 1} to {end_line + 1}")

# Build new content
new_lines = html_lines[:start_line]
new_lines.append('    const allGames = [\n')
new_lines.append(js_array_content + '\n')
new_lines.append('    ];\n')
new_lines.extend(html_lines[end_line + 1:])

# Write back
with open('../nintendo.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[OK] nintendo.html updated!")

# Statistics
print("\n[4/4] Statistics...")
on_sale = sum(1 for g in games_data if g.get('max_discount', 0) > 0)
br_cheapest = sum(1 for g in games_data if g.get('cheapest_region') == 'BR')

print(f"  Total games: {len(games_data)}")
print(f"  On sale: {on_sale}")
print(f"  BR is cheapest: {br_cheapest}")

# Show Nintendo first-party examples
print("\n" + "="*60)
print("NINTENDO FIRST-PARTY GAMES:")
print("="*60)

nintendo_keywords = ['mario', 'zelda', 'pokemon', 'kirby', 'metroid',
                     'splatoon', 'animal crossing', 'donkey kong']
count = 0
for game in games_data:
    title_lower = game['title'].lower()
    if any(kw in title_lower for kw in nintendo_keywords):
        br_price = game.get('prices', {}).get('BR', {})
        if br_price:
            discount_str = f" (-{br_price.get('discount', 0)}%)" if br_price.get('discount', 0) > 0 else ""
            print(f"{game['title']}: R$ {br_price.get('msrp', 0):.2f}{discount_str}")
            count += 1
            if count >= 20:
                break

print("\n" + "="*60)
print("DONE!")
print("="*60)
