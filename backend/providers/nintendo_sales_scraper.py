"""
Nintendo eShop Sales Scraper
Busca TODOS os jogos em promoção real da Nintendo eShop
Suporta múltiplas regiões e paginação completa
"""
import json
import time
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from datetime import datetime


# Regiões principais com eShop
ESHOP_REGIONS = {
    "US": {"name": "United States", "currency": "USD", "rate": 5.80, "lang": "en"},
    "BR": {"name": "Brazil", "currency": "BRL", "rate": 1.00, "lang": "pt"},
    "GB": {"name": "United Kingdom", "currency": "GBP", "rate": 7.20, "lang": "en"},
    "JP": {"name": "Japan", "currency": "JPY", "rate": 0.039, "lang": "ja"},
    "DE": {"name": "Germany", "currency": "EUR", "rate": 6.20, "lang": "de"},
    "FR": {"name": "France", "currency": "EUR", "rate": 6.20, "lang": "fr"},
    "MX": {"name": "Mexico", "currency": "MXN", "rate": 0.32, "lang": "es"},
    "AR": {"name": "Argentina", "currency": "ARS", "rate": 0.0062, "lang": "es"},
}


class NintendoSalesScraper:
    """Scraper especializado em buscar APENAS jogos em promoção"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }

    def _make_request(self, url: str, timeout: int = 30) -> Optional[Dict]:
        """Faz requisição HTTP com tratamento de erros"""
        try:
            req = Request(url, headers=self.headers)
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"  Erro na requisição: {e}")
            return None

    def search_sales_algolia(self, region: str, page: int = 0, per_page: int = 200) -> List[Dict]:
        """
        Busca jogos EM PROMOÇÃO usando Algolia
        """
        app_id = "U3B6GR4UA3"
        api_key = "c4da8be7fd29f0f5bfa42920b0a99dc7"

        lang = ESHOP_REGIONS[region]["lang"]
        country = region.lower()

        # Tentar diferentes índices
        index_patterns = [
            f"ncom_game_{lang}_{country}_title_asc",
            f"ncom_game_{country}_{lang}_title_asc",
            f"noa_aem_game_{country}_{lang}",
        ]

        for index in index_patterns:
            url = f"https://{app_id}-dsn.algolia.net/1/indexes/{index}/query"

            # Buscar jogos (vamos filtrar os em promoção depois)
            payload = json.dumps({
                "params": f"query=&hitsPerPage={per_page}&page={page}&facetFilters=[[\\\"type:game\\\"]]&filters=platform:Nintendo Switch"
            })

            try:
                req = Request(url, data=payload.encode(), headers={
                    **self.headers,
                    "X-Algolia-Application-Id": app_id,
                    "X-Algolia-API-Key": api_key,
                    "Content-Type": "application/json",
                })

                with urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    games = data.get("hits", [])
                    total = data.get("nbHits", 0)

                    if games:
                        print(f"  Pagina {page}: {len(games)} jogos (Total: {total}) - indice: {index}")
                        return games, total

            except Exception as e:
                print(f"  Erro com indice {index}: {str(e)[:80]}")
                continue

        return [], 0

    def get_all_sales_in_region(self, region: str, max_games: int = 1000) -> List[Dict]:
        """
        Busca TODOS os jogos em promoção de uma região (com paginação)
        """
        print(f"\n{'='*60}")
        print(f"Região: {ESHOP_REGIONS[region]['name']} ({region})")
        print(f"Buscando TODOS os jogos em promoção...")
        print(f"{'='*60}")

        all_games = []
        page = 0
        per_page = 200

        while len(all_games) < max_games:
            games, total = self.search_sales_algolia(region, page, per_page)

            if not games:
                break

            all_games.extend(games)

            # Se pegamos menos que per_page, chegamos no fim
            if len(games) < per_page:
                break

            page += 1
            time.sleep(0.5)  # Rate limiting

            # Limite de segurança
            if page > 10:  # Max 10 páginas = 2000 jogos
                break

        print(f"✓ Total de jogos em promoção: {len(all_games)}")
        return all_games

    def get_prices_batch(self, region: str, nsuids: List[str]) -> Dict[str, Dict]:
        """Busca preços em lote"""
        if not nsuids:
            return {}

        country = region
        lang = ESHOP_REGIONS[region]["lang"]

        base_url = "https://api.ec.nintendo.com/v1/price"
        params = {
            "country": country,
            "lang": lang,
            "ids": ",".join(nsuids[:50])
        }

        url = f"{base_url}?{urlencode(params)}"

        try:
            data = self._make_request(url)
            if not data or "prices" not in data:
                return {}

            prices = {}
            for price_info in data.get("prices", []):
                nsuid = str(price_info.get("title_id", ""))
                if nsuid:
                    prices[nsuid] = price_info

            return prices

        except Exception as e:
            return {}

    def scrape_sales_complete(self, region: str, max_games: int = 1000) -> List[Dict]:
        """
        Scrape completo: busca jogos em promoção + preços
        """
        # 1. Buscar TODOS os jogos em promoção
        games = self.get_all_sales_in_region(region, max_games)

        if not games:
            return []

        # 2. Extrair NSUIDs
        nsuids = []
        game_map = {}
        for game in games:
            nsuid = game.get("nsuid_txt") or game.get("nsuid") or game.get("objectID")
            if nsuid:
                nsuid_str = str(nsuid).split("-")[0]  # Remove sufixos
                nsuids.append(nsuid_str)
                game_map[nsuid_str] = game

        print(f"Buscando preços para {len(nsuids)} jogos...")

        # 3. Buscar preços em lotes
        all_prices = {}
        for i in range(0, len(nsuids), 50):
            batch = nsuids[i:i+50]
            prices = self.get_prices_batch(region, batch)
            all_prices.update(prices)
            print(f"  Processado {min(i+50, len(nsuids))}/{len(nsuids)}")
            time.sleep(0.5)

        # 4. Combinar dados
        results = []
        rate = ESHOP_REGIONS[region]["rate"]

        for nsuid, game in game_map.items():
            price_info = all_prices.get(nsuid, {})

            msrp = None
            sale_price = None
            discount = 0

            regular = price_info.get("regular_price", {})
            if regular and regular.get("raw_value"):
                msrp = regular["raw_value"] / 100

            discount_info = price_info.get("discount_price", {})
            if discount_info and discount_info.get("raw_value"):
                sale_price = discount_info["raw_value"] / 100
                if msrp and msrp > 0:
                    discount = round((1 - (sale_price / msrp)) * 100)

            # Apenas jogos COM desconto real
            if discount > 0 and sale_price:
                price_brl = sale_price * rate

                results.append({
                    "title": game.get("title", "Unknown"),
                    "nsuid": nsuid,
                    "store": "nintendo",
                    "platform": "switch",
                    "region": region,
                    "currency": ESHOP_REGIONS[region]["currency"],
                    "msrp": msrp,
                    "sale_price": sale_price,
                    "discount_percent": discount,
                    "price_brl": price_brl,
                    "url": f"https://www.nintendo.com/store/products/{game.get('url', '')}",
                    "publisher": game.get("publisher", ""),
                    "rating": game.get("esrbRating", ""),
                    "game_id": self._slugify(game.get("title", "")),
                    "last_updated": datetime.utcnow().isoformat(),
                })

        print(f"✓ {len(results)} jogos COM PROMOÇÃO REAL")
        return results

    def _slugify(self, text: str) -> str:
        """Converte título em slug"""
        import re
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

    def scrape_all_sales(self, regions: List[str], max_per_region: int = 1000) -> List[Dict]:
        """Scrape de promoções em múltiplas regiões"""
        all_results = []

        for region in regions:
            try:
                results = self.scrape_sales_complete(region, max_per_region)
                all_results.extend(results)
            except Exception as e:
                print(f"Erro em {region}: {e}")
                continue

        return all_results


def get_all_sales(regions: Optional[List[str]] = None, max_per_region: int = 1000) -> List[Dict]:
    """
    Função principal para buscar TODAS as promoções reais

    Args:
        regions: Lista de regiões
        max_per_region: Máximo de jogos por região

    Returns:
        Lista completa de jogos em promoção
    """
    if regions is None:
        regions = ["US", "BR"]  # Por padrão, buscar US e BR

    scraper = NintendoSalesScraper()
    return scraper.scrape_all_sales(regions, max_per_region)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("Buscando TODAS as promoções reais da Nintendo eShop...")
    print("="*60)

    sales = get_all_sales(regions=["US", "BR"], max_per_region=500)

    print(f"\n{'='*60}")
    print(f"TOTAL DE JOGOS EM PROMOÇÃO: {len(sales)}")
    print(f"{'='*60}")

    # Mostrar primeiros 10
    for item in sales[:10]:
        print(f"{item['title'][:40]:40s} -{item['discount_percent']}% | {item['currency']} {item['sale_price']:.2f} (R$ {item['price_brl']:.2f})")
