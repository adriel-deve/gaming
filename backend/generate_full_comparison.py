"""
Gerar comparação de preços para TODOS os jogos
Mesmo os que existem em apenas uma região
"""
import json

# Ler dados da região US (6165 jogos)
with open('nintendo_sales_data.json', 'r', encoding='utf-8') as f:
    us_games = json.load(f)

# Ler dados de comparação multi-região (2197 jogos)
with open('multi_region_prices.json', 'r', encoding='utf-8') as f:
    multi_region = json.load(f)

# Criar dicionário de jogos com múltiplas regiões por game_id
multi_region_dict = {}
for game in multi_region:
    # Tentar múltiplas formas de identificação
    if game.get('slug'):
        multi_region_dict[game['slug']] = game
    if game.get('nsuid'):
        multi_region_dict[game['nsuid']] = game
    if game.get('title'):
        # Normalizar título para busca
        normalized = game['title'].lower().replace(' ', '-').replace(':', '').replace("'", '')
        multi_region_dict[normalized] = game

print(f"Jogos com múltiplas regiões: {len(multi_region)}")
print(f"Total de jogos US: {len(us_games)}")

# Gerar lista completa
full_comparison = []
found_multi = 0
only_single = 0

for us_game in us_games:
    # Tentar encontrar nos dados multi-região
    game_id = us_game.get('game_id', '')
    nsuid = us_game.get('nsuid', '')
    title_normalized = us_game['title'].lower().replace(' ', '-').replace(':', '').replace("'", '')

    multi_game = None
    if game_id and game_id in multi_region_dict:
        multi_game = multi_region_dict[game_id]
    elif nsuid and nsuid in multi_region_dict:
        multi_game = multi_region_dict[nsuid]
    elif title_normalized in multi_region_dict:
        multi_game = multi_region_dict[title_normalized]

    if multi_game:
        # Jogo existe em múltiplas regiões, usar dados existentes
        full_comparison.append(multi_game)
        found_multi += 1
    else:
        # Jogo existe só em US, criar entrada com uma região apenas
        full_comparison.append({
            'title': us_game['title'],
            'nsuid': us_game.get('nsuid'),
            'slug': us_game.get('game_id'),
            'prices': [
                {
                    'region': us_game['region'],
                    'currency': us_game['currency'],
                    'msrp': us_game['msrp'] if us_game['currency'] == 'USD' else us_game['msrp_brl'],
                    'sale_price': us_game['sale_price'] if us_game['currency'] == 'USD' else us_game['price_brl'],
                    'discount_percent': us_game['discount_percent'],
                    'msrp_brl': us_game['msrp_brl'],
                    'price_brl': us_game['price_brl']
                }
            ]
        })
        only_single += 1

print(f"\n[OK] Jogos com múltiplas regiões: {found_multi}")
print(f"[OK] Jogos com apenas US: {only_single}")
print(f"[OK] Total: {len(full_comparison)}")

# Salvar
output_path = '../data/multi-region-prices.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(full_comparison, f, ensure_ascii=False, indent=2)

print(f"\n✓ Arquivo atualizado: {output_path}")
print(f"✓ Agora todos os {len(full_comparison)} jogos têm página de comparação!")
