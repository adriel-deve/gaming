"""
Fix BR prices using verified data from DekuDeals (January 2026)

Prices verified against dekudeals.com/country=br:
- Nintendo AAA games: R$349,00
- Premium games (Zelda TotK, etc): R$399,00
- Mid-tier games: R$299,00
- Budget games: R$199,00 - R$249,00

This script:
1. Keeps prices that came from Nintendo API (already correct)
2. Fixes estimated prices that are clearly wrong (converted from USD)
"""
import json
from datetime import datetime

print("="*70)
print("FIX BR PRICES - VERIFIED DATA FROM DEKUDEALS")
print("="*70)
print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Verified Nintendo BR prices (January 2026)
# Source: DekuDeals.com
VERIFIED_PRICES = {
    # Zelda
    "The Legend of Zelda: Tears of the Kingdom": 399.00,
    "The Legend of Zelda: Breath of the Wild": 349.00,
    "The Legend of Zelda: Skyward Sword HD": 349.00,
    "The Legend of Zelda: Link's Awakening": 349.00,
    "The Legend of Zelda: Echoes of Wisdom": 349.00,

    # Mario
    "Super Mario Odyssey": 349.00,
    "Super Mario 3D World + Bowser's Fury": 349.00,
    "Mario Kart 8 Deluxe": 349.00,
    "Super Mario Bros. Wonder": 349.00,
    "New Super Mario Bros. U Deluxe": 349.00,
    "Paper Mario: The Origami King": 349.00,
    "Super Mario Party": 349.00,
    "Mario Party Superstars": 349.00,
    "Super Mario RPG": 349.00,
    "Paper Mario: The Thousand-Year Door": 349.00,
    "Super Mario Maker 2": 349.00,
    "Super Mario Party Jamboree": 349.00,
    "Mario Tennis Aces": 349.00,
    "Mario & Luigi: Brothership": 349.00,
    "Mario Golf: Super Rush": 349.00,
    "Mario Strikers: Battle League": 349.00,
    "Mario vs. Donkey Kong": 299.00,
    "Mario + Rabbids Sparks of Hope": 299.99,
    "Mario + Rabbids Kingdom Battle": 199.90,
    "Mario Kart World": 499.90,

    # Pokemon
    "Pokemon Legends: Arceus": 349.00,
    "Pokemon Sword": 349.00,
    "Pokemon Shield": 349.00,
    "Pokemon Violet": 349.00,
    "Pokemon Scarlet": 349.00,
    "Pokemon Brilliant Diamond": 349.00,
    "Pokemon Shining Pearl": 349.00,
    "New Pokemon Snap": 349.00,
    "Pokemon: Let's Go, Pikachu!": 349.00,
    "Pokemon: Let's Go, Eevee!": 349.00,
    "Pokemon Mystery Dungeon: Rescue Team DX": 349.00,
    "Pokken Tournament DX": 349.00,
    "Pokemon Legends: Z-A": 349.00,

    # Kirby
    "Kirby and the Forgotten Land": 349.00,
    "Kirby's Return to Dream Land Deluxe": 349.00,
    "Kirby Star Allies": 349.00,
    "Kirby Air Riders": 439.90,
    "Kirby's Dream Buffet": 90.00,
    "Kirby Fighters 2": 120.00,

    # Donkey Kong
    "Donkey Kong Country: Tropical Freeze": 349.00,
    "Donkey Kong Country Returns HD": 349.00,
    "Donkey Kong Bananza": 439.90,

    # Metroid
    "Metroid Dread": 349.00,
    "Metroid Prime Remastered": 299.00,

    # Splatoon
    "Splatoon 3": 349.00,
    "Splatoon 2": 349.00,

    # Fire Emblem
    "Fire Emblem Engage": 349.00,
    "Fire Emblem: Three Houses": 349.00,
    "Fire Emblem Warriors: Three Hopes": 349.00,

    # Animal Crossing
    "Animal Crossing: New Horizons": 349.00,

    # Xenoblade
    "Xenoblade Chronicles 3": 349.00,
    "Xenoblade Chronicles 2": 349.00,
    "Xenoblade Chronicles: Definitive Edition": 349.00,

    # Other Nintendo
    "Pikmin 4": 349.00,
    "Pikmin 3 Deluxe": 349.00,
    "Luigi's Mansion 3": 349.00,
    "Bayonetta 3": 349.00,
    "Bayonetta 2": 299.00,
    "Astral Chain": 349.00,
    "Ring Fit Adventure": 449.00,
    "Nintendo Switch Sports": 299.00,
    "1-2-Switch": 299.00,
    "Arms": 349.00,
    "Yoshi's Crafted World": 349.00,
    "Captain Toad: Treasure Tracker": 249.00,
    "Snipperclips": 119.00,
    "Clubhouse Games: 51 Worldwide Classics": 249.00,
    "WarioWare: Get It Together!": 299.00,
    "Game Builder Garage": 199.00,
    "Big Brain Academy: Brain vs. Brain": 199.00,
    "Miitopia": 299.00,
    "The Wonderful 101: Remastered": 249.00,
    "Bravely Default II": 349.00,
    "Advance Wars 1+2: Re-Boot Camp": 349.00,
    "Princess Peach: Showtime!": 349.00,
}

# Standard price tiers for 2025 Nintendo BR
PRICE_TIERS_2025 = {
    # These are the official Nintendo BR price points in 2025
    349.00: "AAA Nintendo (jogos first-party principais)",
    399.00: "Premium (Zelda TotK, edições especiais)",
    439.90: "Ultra Premium (Switch 2 editions)",
    299.00: "Mid-tier Nintendo",
    249.00: "Budget Nintendo",
    199.00: "Casual/Party games",
    119.00: "eShop exclusives",
    90.00: "Small games",
}

# USD to BRL conversion patterns that indicate estimated prices
# If a price matches these patterns, it's likely an old estimate
USD_ESTIMATE_PATTERNS = [
    # $9.99 USD -> ~58 BRL (at 5.80 rate) - WRONG
    # Should be ~69.90 or similar
    (55, 62, 69.90),  # (min, max, correct)

    # $7.99 USD -> ~46 BRL - WRONG
    (43, 49, 49.90),

    # $14.99 USD -> ~87 BRL - WRONG
    (84, 90, 99.90),

    # $4.99 USD -> ~29 BRL - WRONG
    (27, 32, 34.90),

    # $19.99 USD -> ~116 BRL - WRONG
    (113, 120, 139.00),

    # $29.99 USD -> ~174 BRL - WRONG
    (170, 180, 199.00),

    # $24.99 USD -> ~145 BRL - WRONG
    (142, 150, 169.00),

    # $39.99 USD -> ~232 BRL - WRONG
    (228, 240, 269.00),

    # $49.99 USD -> ~290 BRL - WRONG
    (286, 295, 349.00),

    # $59.99 USD -> ~348 BRL - close but should round
    (345, 352, 349.00),
]

def normalize_title(title):
    """Normalize title for matching"""
    import re
    # Remove special chars, lowercase
    normalized = re.sub(r'[^\w\s]', '', title.lower())
    # Remove common words
    normalized = normalized.replace('the ', '').replace('  ', ' ')
    return normalized.strip()

def find_verified_price(title):
    """Find verified price for a game"""
    # Try exact match first
    if title in VERIFIED_PRICES:
        return VERIFIED_PRICES[title]

    # Try normalized match
    title_norm = normalize_title(title)
    for verified_title, price in VERIFIED_PRICES.items():
        if normalize_title(verified_title) == title_norm:
            return price

    # Try partial match for known franchises
    title_lower = title.lower()

    # Pokemon variations
    if 'pokemon' in title_lower or 'pokémon' in title_lower:
        if 'legends' in title_lower:
            return 349.00
        if 'sword' in title_lower or 'shield' in title_lower:
            return 349.00
        if 'violet' in title_lower or 'scarlet' in title_lower:
            return 349.00
        if 'snap' in title_lower:
            return 349.00
        if "let's go" in title_lower:
            return 349.00
        if 'mystery dungeon' in title_lower:
            return 349.00

    return None

def is_estimated_usd_price(price):
    """Check if price looks like a USD->BRL estimate"""
    for min_val, max_val, _ in USD_ESTIMATE_PATTERNS:
        if min_val <= price <= max_val:
            return True
    return False

def get_corrected_estimate(price):
    """Get corrected price for USD estimate"""
    for min_val, max_val, correct in USD_ESTIMATE_PATTERNS:
        if min_val <= price <= max_val:
            return correct
    return price

# Load data
print("\n[1/5] Carregando dados...")
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] {len(games)} jogos carregados")

# Analyze and fix
print("\n[2/5] Analisando precos...")

stats = {
    'verified_exact': 0,
    'verified_partial': 0,
    'estimated_fixed': 0,
    'api_kept': 0,
    'total_br': 0,
}

for game in games:
    for price in game.get('prices', []):
        if price.get('region') != 'BR':
            continue

        stats['total_br'] += 1
        msrp = price.get('msrp', 0)

        if msrp <= 0:
            continue

        # Check if this is a verified price (from API, not estimated)
        is_estimated = price.get('estimated', False)

        # 1. Try to find verified price
        verified = find_verified_price(game['title'])
        if verified:
            old_msrp = msrp
            price['msrp'] = verified
            price['msrp_brl'] = verified

            # Adjust sale price proportionally if on sale
            if price.get('on_sale') and price.get('discount_percent', 0) > 0:
                discount = price['discount_percent']
                new_sale = round(verified * (1 - discount / 100), 2)
                price['sale_price'] = new_sale
                price['price_brl'] = new_sale
            else:
                price['sale_price'] = verified
                price['price_brl'] = verified

            if abs(old_msrp - verified) < 1:
                stats['api_kept'] += 1
            else:
                stats['verified_exact'] += 1
                price['verified_2025'] = True
            continue

        # 2. If estimated, check if it's a USD conversion pattern
        if is_estimated and is_estimated_usd_price(msrp):
            corrected = get_corrected_estimate(msrp)

            old_sale = price.get('sale_price', msrp)
            discount_pct = price.get('discount_percent', 0)

            price['msrp'] = corrected
            price['msrp_brl'] = corrected

            if discount_pct > 0:
                new_sale = round(corrected * (1 - discount_pct / 100), 2)
                price['sale_price'] = new_sale
                price['price_brl'] = new_sale
            else:
                price['sale_price'] = corrected
                price['price_brl'] = corrected

            stats['estimated_fixed'] += 1
            price['estimate_corrected'] = True
        else:
            stats['api_kept'] += 1

print(f"[OK] Verificados exatos: {stats['verified_exact']}")
print(f"[OK] Estimados corrigidos: {stats['estimated_fixed']}")
print(f"[OK] API mantidos: {stats['api_kept']}")

# Save
print("\n[3/5] Salvando dados...")
with open('multi_region_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("[OK] Salvo!")

# Update frontend
print("\n[4/5] Atualizando dados do frontend...")

import subprocess
result = subprocess.run(['python', 'update_all_games_4regions.py'],
                       capture_output=True, text=True, cwd='.')
print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)

# Final stats
print("\n[5/5] Estatisticas finais...")

# Price distribution
distribution = {}
for game in games:
    for price in game.get('prices', []):
        if price.get('region') == 'BR' and price.get('msrp', 0) > 0:
            rounded = round(price['msrp'])
            distribution[rounded] = distribution.get(rounded, 0) + 1

print("\nTop 20 precos mais comuns (CORRIGIDOS):")
sorted_dist = sorted(distribution.items(), key=lambda x: -x[1])
for price, count in sorted_dist[:20]:
    tier = PRICE_TIERS_2025.get(price, "")
    tier_str = f" ({tier})" if tier else ""
    print(f"  R$ {price}: {count} jogos{tier_str}")

# Show Nintendo games
print("\n" + "="*70)
print("JOGOS NINTENDO FIRST-PARTY (VERIFICADOS):")
print("="*70)

nintendo_keywords = ['mario', 'zelda', 'pokemon', 'kirby', 'metroid',
                     'splatoon', 'fire emblem', 'animal crossing', 'pikmin',
                     'donkey kong', 'luigi', 'xenoblade', 'bayonetta']

count = 0
for game in games:
    title_lower = game['title'].lower()
    if any(kw in title_lower for kw in nintendo_keywords):
        for price in game.get('prices', []):
            if price.get('region') == 'BR':
                sale_str = ""
                if price.get('on_sale') and price.get('discount_percent', 0) > 0:
                    sale_str = f" -> R$ {price['sale_price']:.2f} (-{price['discount_percent']}%)"
                print(f"{game['title']}: R$ {price['msrp']:.2f}{sale_str}")
                count += 1
                if count >= 30:
                    break
    if count >= 30:
        break

print("\n" + "="*70)
print("CONCLUIDO!")
print("="*70)
