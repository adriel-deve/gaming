"""
Nintendo eShop Real Price Scraper
Busca preços reais da API oficial da Nintendo
Suporta 27 países e centenas de jogos
"""
import json
import time
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from datetime import datetime


# TODOS os países com eShop
ESHOP_REGIONS = {
    "US": {"name": "United States", "currency": "USD", "rate": 5.80, "lang": "en"},
    "CA": {"name": "Canada", "currency": "CAD", "rate": 4.20, "lang": "en"},
    "MX": {"name": "Mexico", "currency": "MXN", "rate": 0.32, "lang": "es"},
    "BR": {"name": "Brazil", "currency": "BRL", "rate": 1.00, "lang": "pt"},
    "AR": {"name": "Argentina", "currency": "ARS", "rate": 0.0062, "lang": "es"},
    "CL": {"name": "Chile", "currency": "CLP", "rate": 0.0062, "lang": "es"},
    "CO": {"name": "Colombia", "currency": "COP", "rate": 0.0014, "lang": "es"},
    "PE": {"name": "Peru", "currency": "PEN", "rate": 1.55, "lang": "es"},
    "GB": {"name": "United Kingdom", "currency": "GBP", "rate": 7.20, "lang": "en"},
    "DE": {"name": "Germany", "currency": "EUR", "rate": 6.20, "lang": "de"},
    "FR": {"name": "France", "currency": "EUR", "rate": 6.20, "lang": "fr"},
    "ES": {"name": "Spain", "currency": "EUR", "rate": 6.20, "lang": "es"},
    "IT": {"name": "Italy", "currency": "EUR", "rate": 6.20, "lang": "it"},
    "NL": {"name": "Netherlands", "currency": "EUR", "rate": 6.20, "lang": "nl"},
    "PT": {"name": "Portugal", "currency": "EUR", "rate": 6.20, "lang": "pt"},
    "RU": {"name": "Russia", "currency": "RUB", "rate": 0.063, "lang": "ru"},
    "CH": {"name": "Switzerland", "currency": "CHF", "rate": 6.50, "lang": "de"},
    "AT": {"name": "Austria", "currency": "EUR", "rate": 6.20, "lang": "de"},
    "BE": {"name": "Belgium", "currency": "EUR", "rate": 6.20, "lang": "fr"},
    "SE": {"name": "Sweden", "currency": "SEK", "rate": 0.54, "lang": "sv"},
    "NO": {"name": "Norway", "currency": "NOK", "rate": 0.53, "lang": "no"},
    "DK": {"name": "Denmark", "currency": "DKK", "rate": 0.83, "lang": "da"},
    "FI": {"name": "Finland", "currency": "EUR", "rate": 6.20, "lang": "fi"},
    "PL": {"name": "Poland", "currency": "PLN", "rate": 1.45, "lang": "pl"},
    "CZ": {"name": "Czech Republic", "currency": "CZK", "rate": 0.25, "lang": "cs"},
    "JP": {"name": "Japan", "currency": "JPY", "rate": 0.039, "lang": "ja"},
    "AU": {"name": "Australia", "currency": "AUD", "rate": 3.60, "lang": "en"},
    "NZ": {"name": "New Zealand", "currency": "NZD", "rate": 3.40, "lang": "en"},
    "HK": {"name": "Hong Kong", "currency": "HKD", "rate": 0.74, "lang": "zh"},
    "KR": {"name": "South Korea", "currency": "KRW", "rate": 0.0043, "lang": "ko"},
    "ZA": {"name": "South Africa", "currency": "ZAR", "rate": 0.31, "lang": "en"},
}


class NintendoRealScraper:
    """Scraper avançado com busca de preços reais"""

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
            print(f"  Error: {e}")
            return None

    def search_games_algolia(self, region: str, limit: int = 200) -> List[Dict]:
        """
        Busca jogos usando Algolia (API pública da Nintendo)
        """
        print(f"Buscando jogos em {region}...")

        # Algolia Search API da Nintendo
        app_id = "U3B6GR4UA3"
        api_key = "c4da8be7fd29f0f5bfa42920b0a99dc7"
        lang = ESHOP_REGIONS[region]["lang"]
        country = region.lower()

        # Index naming varies by region - try multiple patterns
        index_patterns = [
            f"ncom_game_{lang}_{country}_title_asc",
            f"ncom_game_{country}_{lang}_title_asc",
            f"noa_aem_game_{country}_{lang}",
        ]

        games = []
        for index in index_patterns:
            url = f"https://{app_id}-dsn.algolia.net/1/indexes/{index}/query"

            payload = json.dumps({
                "params": f"query=&hitsPerPage={limit}&facetFilters=[[\"type:game\"]]&filters=platform:Nintendo Switch"
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
                    if games:
                        print(f"  Encontrados {len(games)} jogos usando índice: {index}")
                        return games

            except Exception as e:
                print(f"  Tentativa com índice {index} falhou: {e}")
                continue

        print(f"  Nenhum jogo encontrado com os índices testados")
        return []

    def get_prices_batch(self, region: str, nsuids: List[str]) -> Dict[str, Dict]:
        """
        Busca preços em lote da API de preços da Nintendo
        """
        if not nsuids:
            return {}

        country = region
        lang = ESHOP_REGIONS[region]["lang"]

        # API de preços oficial
        base_url = "https://api.ec.nintendo.com/v1/price"
        params = {
            "country": country,
            "lang": lang,
            "ids": ",".join(nsuids[:50])  # Max 50 por vez
        }

        url = f"{base_url}?{urlencode(params)}"

        try:
            data = self._make_request(url)
            if not data or "prices" not in data:
                return {}

            # Mapear por NSUID
            prices = {}
            for price_info in data.get("prices", []):
                nsuid = str(price_info.get("title_id", ""))
                if nsuid:
                    prices[nsuid] = price_info

            return prices

        except Exception as e:
            print(f"  Erro ao buscar preços: {e}")
            return {}

    def scrape_region_complete(self, region: str, limit: int = 200) -> List[Dict]:
        """
        Scrape completo de uma região: busca jogos + preços
        """
        print(f"\n{'='*60}")
        print(f"Região: {ESHOP_REGIONS[region]['name']} ({region})")
        print(f"{'='*60}")

        # 1. Buscar jogos
        games = self.search_games_algolia(region, limit)
        if not games:
            return []

        # 2. Extrair NSUIDs
        nsuids = []
        game_map = {}
        for game in games:
            nsuid = game.get("nsuid") or game.get("nsuid_txt") or game.get("objectID")
            if nsuid:
                nsuid_str = str(nsuid)
                nsuids.append(nsuid_str)
                game_map[nsuid_str] = game

        print(f"Buscando preços para {len(nsuids)} jogos...")

        # 3. Buscar preços em lotes de 50
        all_prices = {}
        for i in range(0, len(nsuids), 50):
            batch = nsuids[i:i+50]
            prices = self.get_prices_batch(region, batch)
            all_prices.update(prices)
            print(f"  Processado {min(i+50, len(nsuids))}/{len(nsuids)}")
            time.sleep(0.5)  # Rate limiting

        # 4. Combinar dados
        results = []
        for nsuid, game in game_map.items():
            price_info = all_prices.get(nsuid, {})

            # Extrair preços
            msrp = None
            sale_price = None
            discount = 0

            regular = price_info.get("regular_price", {})
            if regular and regular.get("raw_value"):
                msrp = regular["raw_value"] / 100  # Centavos para unidade

            discount_info = price_info.get("discount_price", {})
            if discount_info and discount_info.get("raw_value"):
                sale_price = discount_info["raw_value"] / 100
                if msrp and msrp > 0:
                    discount = round((1 - (sale_price / msrp)) * 100)

            # Converter para BRL
            rate = ESHOP_REGIONS[region]["rate"]
            final_price = sale_price if sale_price else msrp
            price_brl = final_price * rate if final_price else None

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
                "release_date": game.get("releaseDateDisplay", ""),
                "last_updated": datetime.utcnow().isoformat(),
            })

        print(f"✓ Completado: {len(results)} jogos com preços")
        return results

    def scrape_all_regions(self, regions: List[str], limit_per_region: int = 200) -> List[Dict]:
        """Scrape múltiplas regiões"""
        all_results = []

        for region in regions:
            try:
                results = self.scrape_region_complete(region, limit_per_region)
                all_results.extend(results)
            except Exception as e:
                print(f"Erro em {region}: {e}")
                continue

        return all_results


def get_items(regions: Optional[List[str]] = None, limit_per_region: int = 200) -> List[Dict]:
    """
    Função principal para buscar preços reais

    IMPORTANTE: Esta função faz requisições reais à API da Nintendo.
    Use com moderação para não sobrecarregar os servidores.

    Args:
        regions: Lista de regiões (padrão: principais)
        limit_per_region: Limite de jogos por região

    Returns:
        Lista de jogos com preços reais
    """
    if regions is None:
        # Regiões principais por padrão
        regions = ["US", "BR", "GB", "JP", "DE", "MX"]

    scraper = NintendoRealScraper()
    return scraper.scrape_all_regions(regions, limit_per_region)


if __name__ == "__main__":
    # Teste com uma região
    print("Testando scraper real...")
    items = get_items(regions=["US"], limit_per_region=20)

    print(f"\n{'='*60}")
    print(f"Total: {len(items)} jogos")
    print(f"{'='*60}")

    # Mostrar primeiros 5
    for item in items[:5]:
        price = item.get('sale_price') or item.get('msrp')
        if price:
            print(f"{item['title'][:40]:40s} {item['currency']} {price:8.2f} (R$ {item.get('price_brl', 0):.2f})")
