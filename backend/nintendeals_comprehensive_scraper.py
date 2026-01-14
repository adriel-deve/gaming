"""
Comprehensive Multi-Region Scraper usando nintendeals
Busca preços REAIS (não convertidos) de múltiplas regiões
"""
import json
import time
from nintendeals import noa, noe

# Taxas de conversão para BRL (para exibição)
RATES = {
    'USD': 5.80, 'CAD': 4.20, 'MXN': 0.32, 'BRL': 1.00,
    'EUR': 6.20, 'GBP': 7.20, 'AUD': 3.60, 'JPY': 0.039,
}

def fetch_noa_prices(games, limit=100):
    """Buscar preços das Américas (US, CA, MX)"""
    print("\n" + "="*60)
    print("FASE 1: Nintendo of America (US, CA, MX)")
    print("="*60)

    all_games = []
    countries = ['US', 'CA', 'MX']

    # Tentar carregar progresso anterior
    import os
    progress_file = 'noa_progress_all.json'
    start_index = 0

    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                all_games = json.load(f)
            start_index = len(all_games)
            print(f"[OK] Retomando do jogo {start_index}...")
        except:
            pass

    total = min(len(games), limit)

    for i, game in enumerate(games[start_index:limit], start=start_index):
        if (i + 1) % 50 == 0:
            print(f"  Progresso: {i+1}/{total} jogos... ({len(all_games)} com preços NoA)")
            # Salvar progresso a cada 50 jogos
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(all_games, f, ensure_ascii=False, indent=2)
            print(f"    >> Progresso salvo <<")

        game_data = {
            'title': game['title'],
            'nsuid': game.get('nsuid'),
            'slug': game.get('slug'),
            'prices': []
        }

        # Tentar buscar info do jogo
        try:
            # Buscar jogo no NoA
            search_results = list(noa.search_switch_games(game['title']))

            if not search_results:
                continue

            # Pegar primeiro resultado (melhor match)
            game_obj = search_results[0]

            # Buscar preços em cada país
            for country in countries:
                try:
                    price_obj = game_obj.price(country=country)
                    if price_obj and price_obj.value > 0:
                        sale_price = price_obj.sale_value if price_obj.on_sale else price_obj.value
                        discount = price_obj.sale_discount if price_obj.on_sale else 0

                        game_data['prices'].append({
                            'region': country,
                            'currency': price_obj.currency,
                            'msrp': price_obj.value,
                            'sale_price': sale_price,
                            'discount_percent': discount,
                            'msrp_brl': price_obj.value * RATES.get(price_obj.currency, 1),
                            'price_brl': sale_price * RATES.get(price_obj.currency, 1)
                        })

                    time.sleep(0.3)  # Rate limiting

                except Exception:
                    pass

        except Exception:
            pass

        if game_data['prices']:
            all_games.append(game_data)

    # Salvar progresso final
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(all_games, f, ensure_ascii=False, indent=2)

    print(f"\n  [OK] {len(all_games)} jogos com preços das Américas")
    return all_games

def fetch_noe_prices(games, limit=50):
    """Buscar preços da Europa (GB, DE, FR, ES, IT, etc.)"""
    print("\n" + "="*60)
    print("FASE 2: Nintendo of Europe (GB, DE, FR, ES, IT)")
    print("="*60)

    all_games = []
    countries = ['GB', 'DE', 'FR', 'ES', 'IT']

    for i, game in enumerate(games[:limit]):
        if (i + 1) % 5 == 0:
            print(f"  Progresso: {i+1}/{min(len(games), limit)} jogos...")

        game_data = {
            'title': game['title'],
            'nsuid': game.get('nsuid'),
            'slug': game.get('slug'),
            'prices': []
        }

        # Tentar buscar info do jogo no NoE (Europa tem NSUIDs diferentes)
        try:
            # Buscar jogo no NoE
            search_results = list(noe.search_switch_games(game['title']))

            if not search_results:
                continue

            # Pegar primeiro resultado (melhor match)
            game_obj = search_results[0]

            # Buscar preços em cada país
            for country in countries:
                try:
                    price_obj = game_obj.price(country=country)
                    if price_obj and price_obj.value > 0:
                        sale_price = price_obj.sale_value if price_obj.on_sale else price_obj.value
                        discount = price_obj.sale_discount if price_obj.on_sale else 0

                        game_data['prices'].append({
                            'region': country,
                            'currency': price_obj.currency,
                            'msrp': price_obj.value,
                            'sale_price': sale_price,
                            'discount_percent': discount,
                            'msrp_brl': price_obj.value * RATES.get(price_obj.currency, 1),
                            'price_brl': sale_price * RATES.get(price_obj.currency, 1)
                        })

                    time.sleep(0.5)  # Rate limiting maior para Europa

                except Exception:
                    pass

        except Exception:
            pass

        if game_data['prices']:
            all_games.append(game_data)

    print(f"\n  [OK] {len(all_games)} jogos com preços da Europa")
    return all_games

def merge_with_existing(us_br_games, noa_games, noe_games):
    """Combinar com dados existentes (US/BR)"""
    print("\n" + "="*60)
    print("COMBINANDO DADOS...")
    print("="*60)

    # Criar mapa por NSUID e título
    games_map = {}

    # Adicionar jogos US/BR existentes
    for game in us_br_games:
        key = game.get('nsuid') or game['title'].lower()
        games_map[key] = {
            'title': game['title'],
            'nsuid': game.get('nsuid'),
            'slug': game.get('slug'),
            'prices': game['prices'].copy()
        }

    # Adicionar preços NoA
    for game in noa_games:
        key = game.get('nsuid') or game['title'].lower()
        if key in games_map:
            # Adicionar novos preços (evitar duplicatas)
            existing_regions = {p['region'] for p in games_map[key]['prices']}
            for price in game['prices']:
                if price['region'] not in existing_regions:
                    games_map[key]['prices'].append(price)
        else:
            games_map[key] = game

    # Adicionar preços NoE
    for game in noe_games:
        key_title = game['title'].lower()
        # Buscar por título (Europa pode ter NSUID diferente)
        found = False
        for key, existing in games_map.items():
            if existing['title'].lower() == key_title:
                existing_regions = {p['region'] for p in existing['prices']}
                for price in game['prices']:
                    if price['region'] not in existing_regions:
                        existing['prices'].append(price)
                found = True
                break
        if not found:
            games_map[game['title'].lower()] = game

    result = list(games_map.values())
    print(f"  [OK] Total: {len(result)} jogos únicos")

    # Estatísticas
    by_region_count = {}
    for game in result:
        count = len(game['prices'])
        by_region_count[count] = by_region_count.get(count, 0) + 1

    print("\n  Jogos por número de regiões:")
    for count in sorted(by_region_count.keys(), reverse=True):
        print(f"    {count} regiões: {by_region_count[count]} jogos")

    return result

def main():
    print("="*60)
    print("SCRAPER COMPREHENSIVO - NINTENDEALS")
    print("Preços REAIS de múltiplas regiões - TODOS OS JOGOS")
    print("="*60)

    # Carregar jogos US/BR existentes
    try:
        with open('all_27_countries_prices.json', 'r', encoding='utf-8') as f:
            us_br_games = json.load(f)
        print(f"\n[OK] {len(us_br_games)} jogos carregados (US/BR)")
    except Exception as e:
        print(f"[ERRO] Não foi possível carregar jogos: {e}")
        return

    # Selecionar jogos com US ou BR (qualquer jogo com preço)
    games_to_enrich = [g for g in us_br_games if len(g['prices']) >= 1]
    print(f"[OK] {len(games_to_enrich)} jogos disponíveis para enriquecimento")

    # Fase 1: Buscar Américas (TODOS os jogos)
    print(f"\n[FASE 1] Buscando preços das Américas (CA, MX) para TODOS os {len(games_to_enrich)} jogos...")
    print("AVISO: Este processo pode levar 2-3 horas devido ao rate limiting da API")
    noa_games = fetch_noa_prices(games_to_enrich, limit=len(games_to_enrich))

    # Salvar progresso NoA
    with open('noa_progress_all.json', 'w', encoding='utf-8') as f:
        json.dump(noa_games, f, ensure_ascii=False, indent=2)

    # Combinar com dados US/BR (pular fase Europa por enquanto)
    print(f"\n[INFO] Pulando fase Europa para acelerar processo...")
    final_data = merge_with_existing(us_br_games, noa_games, [])

    # Salvar resultado final
    output_path = 'all_regions_comprehensive.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("\n" + "="*60)
    print("CONCLUÍDO!")
    print(f"  Arquivo: {output_path}")
    print(f"  Total: {len(final_data)} jogos")
    print("="*60)

    # Mostrar exemplos
    print("\nEXEMPLOS DE JOGOS COM MAIS REGIÕES:")
    multi_region = sorted([g for g in final_data if len(g['prices']) >= 5],
                          key=lambda x: len(x['prices']), reverse=True)[:5]

    for game in multi_region:
        print(f"\n{game['title']} - {len(game['prices'])} regiões")
        for price in sorted(game['prices'], key=lambda x: x['price_brl']):
            discount_text = f" (-{price['discount_percent']}%)" if price['discount_percent'] > 0 else ""
            print(f"  {price['region']}: {price['currency']} {price['sale_price']:.2f} = R$ {price['price_brl']:.2f}{discount_text}")

if __name__ == '__main__':
    main()
