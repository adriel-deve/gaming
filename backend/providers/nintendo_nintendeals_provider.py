"""
Nintendo eShop Sales Provider usando nintendeals
Busca TODOS os jogos em promoção real da Nintendo eShop
"""
import sys
from typing import List, Dict
from datetime import datetime
from nintendeals import noa, noe  # Nintendo of America, Nintendo of Europe
from nintendeals.api.prices import get_prices

# Taxas de conversão para BRL
CURRENCY_RATES = {
    "USD": 5.80,
    "CAD": 4.20,
    "MXN": 0.32,
    "BRL": 1.00,
    "EUR": 6.20,
    "GBP": 7.20,
    "JPY": 0.039,
    "AUD": 3.60,
    "NZD": 3.40,
}

# Mapeamento de regiões
REGION_MAP = {
    "US": {"name": "United States", "currency": "USD", "api": noa},
    "CA": {"name": "Canada", "currency": "CAD", "api": noa},
    "MX": {"name": "Mexico", "currency": "MXN", "api": noa},
    "BR": {"name": "Brazil", "currency": "BRL", "api": noa},
    "GB": {"name": "United Kingdom", "currency": "GBP", "api": noe},
    "DE": {"name": "Germany", "currency": "EUR", "api": noe},
    "FR": {"name": "France", "currency": "EUR", "api": noe},
    "ES": {"name": "Spain", "currency": "EUR", "api": noe},
    "IT": {"name": "Italy", "currency": "EUR", "api": noe},
}


def get_all_sales(regions: List[str] = None, limit: int = 500) -> List[Dict]:
    """
    Busca TODOS os jogos em promoção usando nintendeals

    Args:
        regions: Lista de códigos de regiões
        limit: Limite de jogos a buscar

    Returns:
        Lista de jogos em promoção
    """
    if regions is None:
        regions = ["US", "BR"]

    all_sales = []

    for region in regions:
        if region not in REGION_MAP:
            print(f"Regiao {region} nao suportada")
            continue

        print(f"\n{'='*60}")
        print(f"Buscando promocoes em {REGION_MAP[region]['name']} ({region})")
        print(f"{'='*60}")

        try:
            # Buscar jogos em promoção
            api = REGION_MAP[region]["api"]

            # Buscar jogos (nintendeals tem métodos para buscar games)
            # Vamos buscar e filtrar os que estão em promoção
            print("  Buscando jogos...")

            # Buscar lista de jogos do switch (é um generator)
            print("  Listando jogos...")
            games_list = []
            for i, game in enumerate(api.list_switch_games()):
                if i >= limit:
                    break
                games_list.append(game)

            print(f"  Encontrados {len(games_list)} jogos, buscando precos em lote...")

            # Criar um mapa de nsuid para game
            game_map = {game.nsuid: game for game in games_list}

            # Buscar preços em lote (mais eficiente)
            count = 0
            try:
                prices_iterator = get_prices(games_list, country=region.lower())

                for nsuid, price in prices_iterator:
                    if price and hasattr(price, 'sale_discount') and price.sale_discount:
                        discount = price.sale_discount
                        if discount > 0:
                            # Jogo está em promoção!
                            game = game_map.get(nsuid)
                            if not game:
                                continue

                            # Extrair preços
                            msrp = price.full_price if hasattr(price, 'full_price') and price.full_price else None
                            sale_price = price.sale_value if hasattr(price, 'sale_value') and price.sale_value else None

                            if msrp and sale_price and sale_price < msrp:
                                currency = REGION_MAP[region]["currency"]
                                rate = CURRENCY_RATES.get(currency, 1.0)

                                all_sales.append({
                                    "title": game.title,
                                    "nsuid": game.nsuid,
                                    "store": "nintendo",
                                    "platform": "switch",
                                    "region": region,
                                    "currency": currency,
                                    "msrp": msrp,
                                    "sale_price": sale_price,
                                    "discount_percent": int(discount),
                                    "price_brl": sale_price * rate,
                                    "url": f"https://www.nintendo.com/store/products/{game.slug}" if hasattr(game, 'slug') else "",
                                    "game_id": game.slug if hasattr(game, 'slug') else game.nsuid,
                                    "last_updated": datetime.utcnow().isoformat(),
                                })

                                count += 1
                                if count % 10 == 0:
                                    print(f"  Encontradas {count} promocoes...")

            except Exception as e:
                print(f"  Erro ao buscar precos: {e}")

            print(f"[OK] Total de promocoes em {region}: {count}")

        except Exception as e:
            print(f"[ERRO] Erro ao buscar {region}: {e}")
            continue

    return all_sales


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("Buscando promocoes usando nintendeals...")
    print("="*60)

    # Testar com US apenas (rápido)
    sales = get_all_sales(regions=["US"], limit=100)

    print(f"\n{'='*60}")
    print(f"TOTAL DE JOGOS EM PROMOCAO: {len(sales)}")
    print(f"{'='*60}")

    # Mostrar primeiros 10
    for item in sales[:10]:
        print(f"{item['title'][:40]:40s} -{item['discount_percent']}% | {item['currency']} {item['sale_price']:.2f} (R$ {item['price_brl']:.2f})")
