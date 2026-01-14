"""
Nintendo Switch eShop Scraper - 27 PAÍSES
Usando biblioteca nintendeals para buscar preços REAIS de cada região
"""
import json
import time
from nintendeals import noa, noe
from nintendeals.api import prices

# Taxas de conversão para BRL (janeiro 2026)
CURRENCY_RATES = {
    'USD': 5.80, 'CAD': 4.20, 'MXN': 0.32, 'BRL': 1.00,
    'ARS': 0.0062, 'CLP': 0.0062, 'COP': 0.0014, 'PEN': 1.55,
    'EUR': 6.20, 'GBP': 7.20, 'CHF': 6.50, 'SEK': 0.54,
    'NOK': 0.53, 'DKK': 0.83, 'PLN': 1.45, 'CZK': 0.25, 'RUB': 0.063,
    'JPY': 0.039, 'AUD': 3.60, 'NZD': 3.40, 'HKD': 0.74, 'KRW': 0.0043, 'ZAR': 0.31,
}

# Países suportados por região
COUNTRIES = {
    # Nintendo of America (3 países)
    'noa': {
        'US': {'name': 'Estados Unidos', 'currency': 'USD'},
        'CA': {'name': 'Canadá', 'currency': 'CAD'},
        'MX': {'name': 'México', 'currency': 'MXN'},
    },
    # Nintendo of Europe (24 países)
    'noe': {
        'AT': {'name': 'Áustria', 'currency': 'EUR'},
        'BE': {'name': 'Bélgica', 'currency': 'EUR'},
        'BG': {'name': 'Bulgária', 'currency': 'EUR'},
        'HR': {'name': 'Croácia', 'currency': 'EUR'},
        'CY': {'name': 'Chipre', 'currency': 'EUR'},
        'CZ': {'name': 'República Tcheca', 'currency': 'CZK'},
        'DK': {'name': 'Dinamarca', 'currency': 'DKK'},
        'EE': {'name': 'Estônia', 'currency': 'EUR'},
        'FI': {'name': 'Finlândia', 'currency': 'EUR'},
        'FR': {'name': 'França', 'currency': 'EUR'},
        'DE': {'name': 'Alemanha', 'currency': 'EUR'},
        'GR': {'name': 'Grécia', 'currency': 'EUR'},
        'HU': {'name': 'Hungria', 'currency': 'EUR'},
        'IE': {'name': 'Irlanda', 'currency': 'EUR'},
        'IT': {'name': 'Itália', 'currency': 'EUR'},
        'NL': {'name': 'Holanda', 'currency': 'EUR'},
        'NO': {'name': 'Noruega', 'currency': 'NOK'},
        'PL': {'name': 'Polônia', 'currency': 'PLN'},
        'PT': {'name': 'Portugal', 'currency': 'EUR'},
        'RO': {'name': 'Romênia', 'currency': 'EUR'},
        'RU': {'name': 'Rússia', 'currency': 'RUB'},
        'ZA': {'name': 'África do Sul', 'currency': 'ZAR'},
        'ES': {'name': 'Espanha', 'currency': 'EUR'},
        'SE': {'name': 'Suécia', 'currency': 'SEK'},
        'CH': {'name': 'Suíça', 'currency': 'CHF'},
        'GB': {'name': 'Reino Unido', 'currency': 'GBP'},
        'AU': {'name': 'Austrália', 'currency': 'AUD'},
        'NZ': {'name': 'Nova Zelândia', 'currency': 'NZD'},
    }
}

def fetch_us_brazil():
    """Buscar US e BR usando biblioteca Node.js (mais completo)"""
    print("\n" + "="*60)
    print("FASE 1: Carregando US e BR (biblioteca Node.js)")
    print("="*60)

    try:
        with open('comprehensive_prices.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[OK] Carregados {len(data)} jogos unicos de US e BR")
            return data
    except Exception as e:
        print(f"[ERRO] Erro ao carregar: {e}")
        return []

def fetch_noa_prices(games_list, limit=50):
    """Buscar preços de NoA (US, CA, MX)"""
    print("\n" + "="*60)
    print("FASE 2: Buscando preços NoA (Canadá, México)")
    print("="*60)

    all_prices = []
    countries_to_fetch = ['CA', 'MX']  # US já temos

    for game in games_list[:limit]:  # Limitar para teste
        if not game.get('nsuid'):
            continue

        nsuid = game['nsuid']

        for country_code in countries_to_fetch:
            try:
                country_info = COUNTRIES['noa'][country_code]
                print(f"  Buscando {game['title'][:40]} em {country_info['name']}...", end='')

                price_data = prices.get_price(
                    noa.game_info(nsuid),
                    country=country_code
                )

                if price_data and hasattr(price_data, 'sale_price'):
                    regular = float(price_data.regular_price or 0)
                    sale = float(price_data.sale_price or regular)

                    if regular > 0:
                        discount = int((1 - sale / regular) * 100) if sale < regular else 0
                        currency = country_info['currency']

                        all_prices.append({
                            'title': game['title'],
                            'nsuid': nsuid,
                            'slug': game.get('slug'),
                            'region': country_code,
                            'currency': currency,
                            'msrp': regular,
                            'sale_price': sale,
                            'discount_percent': discount,
                            'msrp_brl': regular * CURRENCY_RATES[currency],
                            'price_brl': sale * CURRENCY_RATES[currency],
                        })
                        print(f"  {currency} {sale:.2f}")
                    else:
                        print("  Sem preço")
                else:
                    print("  Não disponível")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"  Erro: {e}")
                continue

    print(f"\n Total NoA: {len(all_prices)} preços coletados")
    return all_prices

def fetch_noe_prices(games_list, limit=50):
    """Buscar preços de NoE (Europa, AU, NZ, ZA)"""
    print("\n" + "="*60)
    print("FASE 3: Buscando preços NoE (Europa + Oceania)")
    print("="*60)

    all_prices = []
    # Selecionar países principais
    priority_countries = ['GB', 'DE', 'FR', 'ES', 'IT', 'AU', 'NZ', 'PT', 'NL']

    for game in games_list[:limit]:
        if not game.get('nsuid'):
            continue

        # Para NoE, precisamos do NSUID europeu (diferente do US)
        # A biblioteca nintendeals vai buscar automaticamente

        for country_code in priority_countries:
            try:
                country_info = COUNTRIES['noe'][country_code]
                print(f"  {game['title'][:30]:30} em {country_info['name']:15}...", end='')

                # Buscar info do jogo primeiro
                game_info = noe.game_info(game['title'])  # Busca por título

                if game_info:
                    price_data = prices.get_price(game_info, country=country_code)

                    if price_data and hasattr(price_data, 'sale_price'):
                        regular = float(price_data.regular_price or 0)
                        sale = float(price_data.sale_price or regular)

                        if regular > 0:
                            discount = int((1 - sale / regular) * 100) if sale < regular else 0
                            currency = country_info['currency']

                            all_prices.append({
                                'title': game['title'],
                                'nsuid': game.get('nsuid'),
                                'slug': game.get('slug'),
                                'region': country_code,
                                'currency': currency,
                                'msrp': regular,
                                'sale_price': sale,
                                'discount_percent': discount,
                                'msrp_brl': regular * CURRENCY_RATES[currency],
                                'price_brl': sale * CURRENCY_RATES[currency],
                            })
                            print(f"  {currency} {sale:.2f}")
                        else:
                            print("  Sem preço")
                    else:
                        print("  Indisponível")
                else:
                    print("  Jogo não encontrado")

                time.sleep(0.8)  # Rate limiting maior para NoE

            except Exception as e:
                print(f"  {str(e)[:30]}")
                continue

    print(f"\n Total NoE: {len(all_prices)} preços coletados")
    return all_prices

def merge_all_prices(us_br_data, noa_prices, noe_prices):
    """Combinar todos os preços por jogo"""
    print("\n" + "="*60)
    print("COMBINANDO DADOS DE TODAS AS REGIÕES...")
    print("="*60)

    # Adicionar novos preços aos jogos existentes
    for game in us_br_data:
        # Adicionar preços NoA
        for price in noa_prices:
            if price['nsuid'] == game.get('nsuid') or price['title'] == game['title']:
                game['prices'].append({
                    'region': price['region'],
                    'currency': price['currency'],
                    'msrp': price['msrp'],
                    'sale_price': price['sale_price'],
                    'discount_percent': price['discount_percent'],
                    'msrp_brl': price['msrp_brl'],
                    'price_brl': price['price_brl']
                })

        # Adicionar preços NoE
        for price in noe_prices:
            if price['title'] == game['title']:
                game['prices'].append({
                    'region': price['region'],
                    'currency': price['currency'],
                    'msrp': price['msrp'],
                    'sale_price': price['sale_price'],
                    'discount_percent': price['discount_percent'],
                    'msrp_brl': price['msrp_brl'],
                    'price_brl': price['price_brl']
                })

    multi_region = [g for g in us_br_data if len(g['prices']) > 2]
    print(f"\n {len(multi_region)} jogos com 3+ regiões!")

    return us_br_data

def main():
    print("="*60)
    print("SCRAPER COMPLETO - ATÉ 27 PAÍSES")
    print("Usando nintendeals (Python) + nintendo-switch-eshop (Node.js)")
    print("="*60)

    # Fase 1: Carregar US e BR
    us_br_data = fetch_us_brazil()

    # Fase 2: Buscar NoA (50 jogos principais)
    print("\n  LIMITANDO A 50 JOGOS PARA TESTE (evitar rate limiting)")
    noa_prices = fetch_noa_prices(us_br_data, limit=50)

    # Fase 3: Buscar NoE (50 jogos principais)
    noe_prices = fetch_noe_prices(us_br_data, limit=50)

    # Combinar tudo
    final_data = merge_all_prices(us_br_data, noa_prices, noe_prices)

    # Salvar
    output_path = 'multi_country_prices_extended.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n CONCLUÍDO! Salvo em: {output_path}")
    print(f" Total de jogos: {len(final_data)}")

    # Estatísticas
    print("\n JOGOS POR NÚMERO DE REGIÕES:")
    by_count = {}
    for game in final_data:
        count = len(game['prices'])
        by_count[count] = by_count.get(count, 0) + 1

    for count in sorted(by_count.keys(), reverse=True):
        print(f"  {count} regiões: {by_count[count]} jogos")

if __name__ == '__main__':
    main()
