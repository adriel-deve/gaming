"""
Nintendo Hybrid Provider
Combina dados estáticos (extended_data) com scraping real (real_scraper)
Sempre retorna dados: fallback para extended_data se API falhar
"""
from typing import List, Dict, Optional
from .nintendo_extended_data import get_all_games_with_prices, POPULAR_GAMES
from .nintendo_real_scraper import NintendoRealScraper, ESHOP_REGIONS


class NintendoHybridProvider:
    """
    Provider híbrido que combina dados estáticos com scraping real
    """

    def __init__(self, use_api: bool = True):
        """
        Args:
            use_api: Se True, tenta buscar da API. Se False, usa apenas dados estáticos.
        """
        self.use_api = use_api
        self.scraper = NintendoRealScraper() if use_api else None

    def get_items(
        self,
        regions: Optional[List[str]] = None,
        limit_per_region: int = 200,
        fallback_to_static: bool = True
    ) -> List[Dict]:
        """
        Busca jogos com preços, usando API ou fallback para dados estáticos

        Args:
            regions: Lista de regiões (padrão: principais)
            limit_per_region: Limite de jogos por região na API
            fallback_to_static: Se True, usa dados estáticos se API falhar

        Returns:
            Lista de jogos com preços
        """
        if regions is None:
            regions = ["US", "BR", "GB", "JP", "DE", "FR", "MX", "AR"]

        # 1. Tentar buscar da API real
        if self.use_api and self.scraper:
            print("Tentando buscar da API real da Nintendo...")
            try:
                api_results = self.scraper.scrape_all_regions(regions, limit_per_region)

                if api_results and len(api_results) > 0:
                    print(f"[OK] API retornou {len(api_results)} jogos")
                    return api_results
                else:
                    print("[AVISO] API nao retornou jogos")

            except Exception as e:
                print(f"[ERRO] Erro na API: {e}")

        # 2. Fallback para dados estáticos
        if fallback_to_static:
            print("Usando base de dados estatica (extended_data)...")
            static_results = get_all_games_with_prices(regions)
            print(f"[OK] Base estatica retornou {len(static_results)} jogos")
            return static_results

        return []

    def get_popular_games_count(self) -> int:
        """Retorna quantidade de jogos populares na base estática"""
        return len(POPULAR_GAMES)

    def get_supported_regions(self) -> List[str]:
        """Retorna lista de todas as regiões suportadas"""
        return list(ESHOP_REGIONS.keys())


def get_items(
    regions: Optional[List[str]] = None,
    limit_per_region: int = 200,
    use_api: bool = False  # Por padrão, usa dados estáticos (mais rápido)
) -> List[Dict]:
    """
    Função principal para buscar preços da Nintendo eShop

    Args:
        regions: Lista de regiões (padrão: principais)
        limit_per_region: Limite de jogos por região
        use_api: Se True, tenta buscar da API real (mais lento, pode falhar)

    Returns:
        Lista de jogos com preços
    """
    provider = NintendoHybridProvider(use_api=use_api)
    return provider.get_items(regions, limit_per_region)


if __name__ == "__main__":
    import sys

    # Teste do provider híbrido
    print("="*60)
    print("TESTE: Nintendo Hybrid Provider")
    print("="*60)

    # Teste 1: Dados estáticos
    print("\n[1] Testando com dados estáticos...")
    items_static = get_items(regions=["US", "BR"], use_api=False)
    print(f"Total de items: {len(items_static)}")

    # Mostrar primeiros 5
    for item in items_static[:5]:
        price = item.get('sale_price') or item.get('msrp')
        discount = item.get('discount_percent', 0)
        discount_str = f" (-{discount}%)" if discount > 0 else ""
        print(f"{item['title'][:40]:40s} {item['region']} {item['currency']} {price:8.2f}{discount_str}")

    # Teste 2: Com API (pode falhar)
    print("\n[2] Testando com API real...")
    items_api = get_items(regions=["US"], limit_per_region=10, use_api=True)
    print(f"Total de items: {len(items_api)}")

    # Estatísticas
    print("\n" + "="*60)
    print("ESTATÍSTICAS")
    print("="*60)

    provider = NintendoHybridProvider()
    print(f"Jogos populares na base estática: {provider.get_popular_games_count()}")
    print(f"Regiões suportadas: {len(provider.get_supported_regions())}")
    print(f"Regiões: {', '.join(provider.get_supported_regions()[:10])}...")
