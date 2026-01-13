"""
Scraper para eshop-prices.com
Busca jogos em promoção real da Nintendo eShop
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Taxas de conversão para BRL
CURRENCY_RATES = {
    "USD": 5.80,
    "EUR": 6.20,
    "GBP": 7.20,
    "JPY": 0.039,
    "CAD": 4.20,
    "AUD": 3.60,
    "BRL": 1.00,
    "MXN": 0.32,
    "ARS": 0.0062,
}

def scrape_eshop_sales(country='us', limit=100) -> List[Dict]:
    """
    Scrape jogos em promoção do eshop-prices.com

    Args:
        country: País (us, br, gb, etc)
        limit: Número máximo de jogos a buscar

    Returns:
        Lista de jogos em promoção
    """
    url = f"https://eshop-prices.com/games/on-sale?currency={country.upper()}"

    print(f"Buscando jogos em promocao em {country.upper()}...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todos os cards de jogos
        games = []
        game_cards = soup.find_all('div', class_='game-card')

        if not game_cards:
            # Tentar outro seletor
            game_cards = soup.find_all('article', class_='game')

        if not game_cards:
            print(f"Nenhum jogo encontrado. HTML: {soup.prettify()[:500]}")
            return []

        print(f"Encontrados {len(game_cards)} jogos")

        for i, card in enumerate(game_cards[:limit]):
            if i >= limit:
                break

            try:
                # Extrair informações do card
                title_elem = card.find(['h2', 'h3', 'a'], class_=['title', 'game-title'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Buscar preços
                price_old = card.find(['span', 'div'], class_=['price-old', 'original-price'])
                price_new = card.find(['span', 'div'], class_=['price-new', 'sale-price', 'current-price'])
                discount = card.find(['span', 'div'], class_=['discount', 'badge-discount'])

                if price_new and discount:
                    # Extrair valores numéricos
                    msrp_text = price_old.get_text(strip=True) if price_old else price_new.get_text(strip=True)
                    sale_text = price_new.get_text(strip=True)
                    discount_text = discount.get_text(strip=True)

                    # Converter para números
                    msrp = float(''.join(c for c in msrp_text if c.isdigit() or c == '.'))
                    sale_price = float(''.join(c for c in sale_text if c.isdigit() or c == '.'))
                    discount_percent = int(''.join(c for c in discount_text if c.isdigit()))

                    # Game ID
                    game_id = title.lower().replace(' ', '-').replace(':', '').replace("'", '')

                    games.append({
                        'title': title,
                        'msrp': msrp,
                        'sale_price': sale_price,
                        'discount_percent': discount_percent,
                        'currency': country.upper(),
                        'region': country.upper(),
                        'game_id': game_id,
                        'store': 'nintendo',
                        'platform': 'switch'
                    })

                    if (i + 1) % 20 == 0:
                        print(f"  Processados {i + 1} jogos...")

            except Exception as e:
                print(f"  Erro ao processar jogo {i}: {e}")
                continue

        print(f"Total de jogos em promocao: {len(games)}")
        return games

    except Exception as e:
        print(f"Erro ao fazer scraping: {e}")
        return []


if __name__ == '__main__':
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("="*60)
    print("ESHOP-PRICES.COM SCRAPER")
    print("="*60)

    # Testar com US
    games = scrape_eshop_sales(country='us', limit=50)

    print(f"\n{'='*60}")
    print(f"TOTAL: {len(games)} jogos em promocao")
    print(f"{'='*60}\n")

    # Mostrar primeiros 10
    for i, game in enumerate(games[:10], 1):
        print(f"{i}. {game['title'][:40]:40s} -{game['discount_percent']}% | ${game['sale_price']:.2f}")

    if len(games) > 10:
        print(f"\n... e mais {len(games) - 10} jogos")
