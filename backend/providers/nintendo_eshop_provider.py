"""
Nintendo eShop Provider - Multi-region scraper
Uses public Nintendo APIs and alternative data sources
"""
import json
import time
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from datetime import datetime


# Mapeamento de países/regiões da Nintendo eShop
ESHOP_REGIONS = {
    # Americas
    "US": {"name": "United States", "currency": "USD", "country": "US", "lang": "en"},
    "CA": {"name": "Canada", "currency": "CAD", "country": "CA", "lang": "en"},
    "MX": {"name": "Mexico", "currency": "MXN", "country": "MX", "lang": "es"},
    "BR": {"name": "Brazil", "currency": "BRL", "country": "BR", "lang": "pt"},
    "AR": {"name": "Argentina", "currency": "ARS", "country": "AR", "lang": "es"},
    "CL": {"name": "Chile", "currency": "CLP", "country": "CL", "lang": "es"},
    "CO": {"name": "Colombia", "currency": "COP", "country": "CO", "lang": "es"},
    "PE": {"name": "Peru", "currency": "PEN", "country": "PE", "lang": "es"},

    # Europe
    "GB": {"name": "United Kingdom", "currency": "GBP", "country": "GB", "lang": "en"},
    "DE": {"name": "Germany", "currency": "EUR", "country": "DE", "lang": "de"},
    "FR": {"name": "France", "currency": "EUR", "country": "FR", "lang": "fr"},
    "ES": {"name": "Spain", "currency": "EUR", "country": "ES", "lang": "es"},
    "IT": {"name": "Italy", "currency": "EUR", "country": "IT", "lang": "it"},
    "NL": {"name": "Netherlands", "currency": "EUR", "country": "NL", "lang": "nl"},
    "PT": {"name": "Portugal", "currency": "EUR", "country": "PT", "lang": "pt"},
    "RU": {"name": "Russia", "currency": "RUB", "country": "RU", "lang": "ru"},
    "CH": {"name": "Switzerland", "currency": "CHF", "country": "CH", "lang": "de"},
    "AT": {"name": "Austria", "currency": "EUR", "country": "AT", "lang": "de"},
    "BE": {"name": "Belgium", "currency": "EUR", "country": "BE", "lang": "fr"},
    "SE": {"name": "Sweden", "currency": "SEK", "country": "SE", "lang": "sv"},
    "NO": {"name": "Norway", "currency": "NOK", "country": "NO", "lang": "no"},
    "DK": {"name": "Denmark", "currency": "DKK", "country": "DK", "lang": "da"},
    "FI": {"name": "Finland", "currency": "EUR", "country": "FI", "lang": "fi"},
    "PL": {"name": "Poland", "currency": "PLN", "country": "PL", "lang": "pl"},
    "CZ": {"name": "Czech Republic", "currency": "CZK", "country": "CZ", "lang": "cs"},

    # Asia & Oceania
    "JP": {"name": "Japan", "currency": "JPY", "country": "JP", "lang": "ja"},
    "AU": {"name": "Australia", "currency": "AUD", "country": "AU", "lang": "en"},
    "NZ": {"name": "New Zealand", "currency": "NZD", "country": "NZ", "lang": "en"},
    "HK": {"name": "Hong Kong", "currency": "HKD", "country": "HK", "lang": "zh"},
    "KR": {"name": "South Korea", "currency": "KRW", "country": "KR", "lang": "ko"},
    "ZA": {"name": "South Africa", "currency": "ZAR", "country": "ZA", "lang": "en"},
}


class NintendoEshopScraper:
    """Scraper para Nintendo eShop usando APIs públicas"""

    def __init__(self, regions: Optional[List[str]] = None, rate_limit_delay: float = 0.5):
        self.regions = regions or list(ESHOP_REGIONS.keys())
        self.rate_limit_delay = rate_limit_delay
        self.session_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }

    def _make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Faz uma requisição HTTP com tratamento de erros"""
        try:
            req_headers = {**self.session_headers, **(headers or {})}
            req = Request(url, headers=req_headers)

            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _get_games_from_deku_deals(self, region: str, limit: int) -> List[Dict]:
        """
        Fallback: usa DekuDeals API (não oficial mas pública)
        Para demonstração - você deve implementar a API oficial quando disponível
        """
        # Nota: Esta é uma implementação de fallback para demonstração
        # Em produção, você deve usar a API oficial da Nintendo ou um serviço licenciado

        print(f"  Using fallback method for {region}...")
        return []

    def _get_demo_games(self, region: str, limit: int) -> List[Dict]:
        """
        Retorna jogos de demonstração baseados na região
        Para desenvolvimento/teste - substitua por scraping real
        """
        region_data = ESHOP_REGIONS[region]
        currency = region_data["currency"]

        # Jogos de exemplo por região (valores aproximados reais)
        demo_games = {
            "US": [
                {"title": "The Legend of Zelda: Tears of the Kingdom", "nsuid": "70010000063714", "msrp": 69.99, "sale_price": None, "discount": 0},
                {"title": "Super Mario Bros. Wonder", "nsuid": "70010000068675", "msrp": 59.99, "sale_price": 49.99, "discount": 17},
                {"title": "Pokémon Scarlet", "nsuid": "70010000055478", "msrp": 59.99, "sale_price": None, "discount": 0},
                {"title": "Mario Kart 8 Deluxe", "nsuid": "70010000000153", "msrp": 59.99, "sale_price": 41.99, "discount": 30},
                {"title": "Animal Crossing: New Horizons", "nsuid": "70010000027619", "msrp": 59.99, "sale_price": None, "discount": 0},
                {"title": "Splatoon 3", "nsuid": "70010000048950", "msrp": 59.99, "sale_price": 44.99, "discount": 25},
                {"title": "Metroid Prime Remastered", "nsuid": "70010000064444", "msrp": 39.99, "sale_price": None, "discount": 0},
                {"title": "Pikmin 4", "nsuid": "70010000065511", "msrp": 59.99, "sale_price": 47.99, "discount": 20},
            ],
            "BR": [
                {"title": "The Legend of Zelda: Tears of the Kingdom", "nsuid": "70010000063714", "msrp": 349.00, "sale_price": None, "discount": 0},
                {"title": "Super Mario Bros. Wonder", "nsuid": "70010000068675", "msrp": 299.00, "sale_price": 254.15, "discount": 15},
                {"title": "Pokémon Scarlet", "nsuid": "70010000055478", "msrp": 299.00, "sale_price": None, "discount": 0},
                {"title": "Mario Kart 8 Deluxe", "nsuid": "70010000000153", "msrp": 299.00, "sale_price": 209.30, "discount": 30},
                {"title": "Animal Crossing: New Horizons", "nsuid": "70010000027619", "msrp": 299.00, "sale_price": None, "discount": 0},
            ],
            "JP": [
                {"title": "ゼルダの伝説 ティアーズ オブ ザ キングダム", "nsuid": "70010000063714", "msrp": 7900, "sale_price": None, "discount": 0},
                {"title": "スーパーマリオブラザーズ ワンダー", "nsuid": "70010000068675", "msrp": 6578, "sale_price": 5590, "discount": 15},
                {"title": "ポケットモンスター スカーレット", "nsuid": "70010000055478", "msrp": 6578, "sale_price": None, "discount": 0},
                {"title": "マリオカート8 デラックス", "nsuid": "70010000000153", "msrp": 6578, "sale_price": 4604, "discount": 30},
            ],
            "GB": [
                {"title": "The Legend of Zelda: Tears of the Kingdom", "nsuid": "70010000063714", "msrp": 59.99, "sale_price": None, "discount": 0},
                {"title": "Super Mario Bros. Wonder", "nsuid": "70010000068675", "msrp": 49.99, "sale_price": 42.49, "discount": 15},
                {"title": "Mario Kart 8 Deluxe", "nsuid": "70010000000153", "msrp": 49.99, "sale_price": 34.99, "discount": 30},
            ],
            "DE": [
                {"title": "The Legend of Zelda: Tears of the Kingdom", "nsuid": "70010000063714", "msrp": 69.99, "sale_price": None, "discount": 0},
                {"title": "Super Mario Bros. Wonder", "nsuid": "70010000068675", "msrp": 59.99, "sale_price": 50.99, "discount": 15},
                {"title": "Mario Kart 8 Deluxe", "nsuid": "70010000000153", "msrp": 59.99, "sale_price": 41.99, "discount": 30},
            ],
        }

        games = demo_games.get(region, demo_games["US"][:3])[:limit]

        result = []
        for game in games:
            result.append({
                "title": game["title"],
                "nsuid": game["nsuid"],
                "msrp": game["msrp"],
                "sale_price": game["sale_price"],
                "discount_percent": game["discount"],
                "url": f"https://www.nintendo.com/store/products/{game['nsuid']}/",
                "cover_url": f"https://assets.nintendo.com/image/upload/ncom/en_US/games/switch/{game['nsuid']}.jpg",
                "release_date": "2024-01-01",
                "publisher": "Nintendo",
            })

        return result

    def _parse_game_item(self, game: Dict, region: str) -> Dict:
        """Converte dados brutos em formato padronizado"""
        region_data = ESHOP_REGIONS[region]

        msrp = game.get("msrp")
        sale_price = game.get("sale_price")
        discount_percent = game.get("discount_percent", 0)

        return {
            "title": game.get("title", "Unknown"),
            "nsuid": game.get("nsuid", ""),
            "store": "nintendo",
            "platform": "switch",
            "region": region,
            "currency": region_data["currency"],
            "msrp": msrp,
            "sale_price": sale_price,
            "discount_percent": discount_percent,
            "url": game.get("url", ""),
            "cover_url": game.get("cover_url"),
            "release_date": game.get("release_date"),
            "publisher": game.get("publisher"),
            "last_updated": datetime.utcnow().isoformat(),
        }

    def scrape_region(self, region: str, query: str = "", limit: int = 50) -> List[Dict]:
        """Scrape jogos de uma região específica"""
        print(f"Scraping Nintendo eShop - {ESHOP_REGIONS[region]['name']} ({region})...")

        # IMPORTANTE: Esta é uma implementação de demonstração
        # Em produção, substitua por:
        # 1. API oficial da Nintendo (se disponível)
        # 2. Serviço licenciado de terceiros
        # 3. Web scraping do site oficial (com respeito ao robots.txt)

        games = self._get_demo_games(region, limit)

        if not games:
            print(f"  No games found in {region}")
            return []

        print(f"  Found {len(games)} games")

        items = []
        for game in games:
            item = self._parse_game_item(game, region)
            items.append(item)

        print(f"  Scraped {len(items)} items from {region}")
        return items

    def scrape_all_regions(self, query: str = "", limit_per_region: int = 50) -> List[Dict]:
        """Scrape todas as regiões configuradas"""
        all_items = []

        print(f"Starting scrape for {len(self.regions)} regions...")
        for i, region in enumerate(self.regions, 1):
            print(f"[{i}/{len(self.regions)}] ", end="")
            items = self.scrape_region(region, query, limit_per_region)
            all_items.extend(items)

            if i < len(self.regions):
                time.sleep(self.rate_limit_delay)

        print(f"\nTotal items scraped: {len(all_items)}")
        return all_items


def get_items(regions: Optional[List[str]] = None, limit_per_region: int = 50) -> List[Dict]:
    """
    Função principal para uso no pipeline

    NOTA IMPORTANTE:
    Esta é uma implementação de demonstração com dados fictícios.
    Para uso em produção, você deve:

    1. Usar a API oficial da Nintendo (requer parceria)
    2. Usar um serviço licenciado como:
       - Nintendo Developer Portal API
       - Serviços de agregação de dados licenciados
    3. Implementar web scraping respeitando:
       - robots.txt
       - Rate limiting adequado
       - Terms of Service da Nintendo

    Args:
        regions: Lista de regiões para scrape
        limit_per_region: Número máximo de jogos por região

    Returns:
        Lista de dicionários com dados dos jogos
    """
    if regions is None:
        regions = ["US", "BR", "GB", "JP", "DE", "FR", "MX", "AU"]

    scraper = NintendoEshopScraper(regions=regions, rate_limit_delay=0.5)
    return scraper.scrape_all_regions(limit_per_region=limit_per_region)


if __name__ == "__main__":
    # Teste
    test_regions = ["US", "BR", "JP"]
    items = get_items(regions=test_regions, limit_per_region=5)

    print(f"\nSample items:")
    for item in items[:5]:
        price = item.get('sale_price') or item.get('msrp', 0)
        print(f"  - {item['title'][:40]} ({item['region']}): {item['currency']} {price:.2f}")
