# Nintendo eShop Scraper - Guia de Uso

## Visão Geral

O scraper da Nintendo eShop coleta informações de preços de jogos de **todas as regiões** da eShop, incluindo:

- **27 países** suportados (Americas, Europa, Ásia, Oceania)
- Preços em **moeda local** de cada região
- Detecção automática de **promoções e descontos**
- **Rate limiting** para não sobrecarregar a API
- Dados de imagem, publisher, data de lançamento

## Regiões Suportadas

### Americas
- 🇺🇸 US (USD) - United States
- 🇨🇦 CA (CAD) - Canada
- 🇲🇽 MX (MXN) - Mexico
- 🇧🇷 BR (BRL) - Brazil
- 🇦🇷 AR (ARS) - Argentina
- 🇨🇱 CL (CLP) - Chile
- 🇨🇴 CO (COP) - Colombia
- 🇵🇪 PE (PEN) - Peru

### Europa
- 🇬🇧 GB (GBP) - United Kingdom
- 🇩🇪 DE (EUR) - Germany
- 🇫🇷 FR (EUR) - France
- 🇪🇸 ES (EUR) - Spain
- 🇮🇹 IT (EUR) - Italy
- 🇳🇱 NL (EUR) - Netherlands
- 🇵🇹 PT (EUR) - Portugal
- 🇷🇺 RU (RUB) - Russia
- E mais: CH, AT, BE, SE, NO, DK, FI, PL, CZ

### Ásia & Oceania
- 🇯🇵 JP (JPY) - Japan
- 🇦🇺 AU (AUD) - Australia
- 🇳🇿 NZ (NZD) - New Zealand
- 🇭🇰 HK (HKD) - Hong Kong
- 🇰🇷 KR (KRW) - South Korea
- 🇿🇦 ZA (ZAR) - South Africa

## Instalação

Não precisa instalar nada! O scraper usa apenas bibliotecas padrão do Python.

```bash
python --version  # Requer Python 3.7+
```

## Uso Rápido

### 1. Testar o scraper (modo teste)

```bash
# Teste básico com US e BR
python backend/test_eshop_scraper.py

# Teste com regiões específicas
python backend/test_eshop_scraper.py --regions US BR JP GB --limit 20

# Buscar jogos específicos
python backend/test_eshop_scraper.py --regions US --query "zelda" --limit 10

# Ver todas as regiões disponíveis
python backend/test_eshop_scraper.py --show-regions

# Salvar resultados em arquivo
python backend/test_eshop_scraper.py --regions US BR --limit 50 --output results.json
```

### 2. Executar o pipeline completo

```bash
# Executa todo o pipeline (coleta, normaliza, armazena)
python backend/pipeline/run_pipeline.py

# Executar apenas a coleta
python backend/pipeline/collect.py
```

### 3. Iniciar o servidor API

```bash
# Inicia o servidor na porta 9000
python backend/api/server.py --port 9000

# Em outro terminal, teste a API
curl http://localhost:9000/api/health
curl http://localhost:9000/api/offers?store=nintendo&region=BR
```

### 4. Usar o scheduler (atualização automática)

```bash
# Executa uma vez e para
python backend/scheduler.py --once

# Executa continuamente (a cada 60 minutos)
python backend/scheduler.py
```

## Configuração

Edite [eshop_config.json](eshop_config.json) para ajustar:

```json
{
  "regions": {
    "priority": ["US", "BR", "GB", "JP", "DE", "FR", "MX", "AU"],
    "all": ["US", "CA", "MX", ...]
  },
  "scraping": {
    "limit_per_region": 100,
    "rate_limit_delay": 0.5,
    "use_all_regions": false
  }
}
```

### Opções:

- **limit_per_region**: Quantos jogos buscar por região (padrão: 100)
- **rate_limit_delay**: Delay entre requests em segundos (padrão: 0.5)
- **use_all_regions**: Se true, busca todas as 27 regiões (padrão: false, usa apenas priority)

## Uso Programático

### Python

```python
from providers.nintendo_eshop_provider import NintendoEshopScraper

# Criar scraper
scraper = NintendoEshopScraper(
    regions=["US", "BR", "JP"],
    rate_limit_delay=0.5
)

# Scrape todas as regiões
items = scraper.scrape_all_regions(limit_per_region=50)

# Ou scrape apenas uma região
us_items = scraper.scrape_region("US", limit=100)

# Acessar dados
for item in items:
    print(f"{item['title']} - {item['currency']} {item['msrp']}")
    if item['discount_percent'] > 0:
        print(f"  ON SALE: -{item['discount_percent']}%")
```

### Função simples

```python
from providers.nintendo_eshop_provider import get_items

# Busca regiões padrão (US, BR, GB, JP, etc)
items = get_items()

# Busca regiões específicas
items = get_items(regions=["US", "BR", "JP"], limit_per_region=100)
```

## Formato dos Dados

Cada item retornado contém:

```python
{
    "title": "The Legend of Zelda: Tears of the Kingdom",
    "nsuid": "70010000063714",
    "store": "nintendo",
    "platform": "switch",
    "region": "US",
    "currency": "USD",
    "msrp": 69.99,              # Preço normal
    "sale_price": 52.49,        # Preço em promoção (ou None)
    "discount_percent": 25,      # Porcentagem de desconto
    "url": "https://www.nintendo.com/store/products/...",
    "cover_url": "https://...",
    "release_date": "2023-05-12",
    "publisher": "Nintendo",
    "last_updated": "2024-01-12T10:30:00"
}
```

## Performance

- **1 região**: ~5-10 segundos para 100 jogos
- **8 regiões** (priority): ~1-2 minutos para 800 jogos
- **27 regiões** (todas): ~5-10 minutos para 2700 jogos

O scraper usa rate limiting automático para evitar banimento.

## Troubleshooting

### Erro: "No games found"
- A API da Nintendo pode estar temporariamente indisponível
- Tente novamente após alguns segundos
- Verifique sua conexão com a internet

### Erro: Timeout
- Aumente o timeout em `_make_request()` (linha ~75)
- Aumente o `rate_limit_delay` para 1.0 segundo

### Poucos jogos retornados
- Algumas regiões têm menos jogos disponíveis
- Aumente `limit_per_region` no config

### Preços não aparecem
- Alguns jogos não têm preço disponível na API
- Jogos não lançados ainda não têm preço
- Free-to-play não têm preço

## API da Nintendo

O scraper usa duas APIs oficiais da Nintendo:

1. **Algolia Search API**: Busca e metadados dos jogos
2. **Nintendo Pricing API**: Preços e promoções

Ambas são públicas e usadas pelo site oficial da Nintendo.

## Próximos Passos

Depois de coletar os dados, você pode:

1. ✅ Visualizar no frontend ([index.html](../index.html))
2. ✅ Criar alertas de preço
3. ✅ Comparar preços entre regiões
4. ✅ Histórico de preços
5. ✅ Adicionar outros providers (PlayStation, Xbox, Steam)

## Suporte

Dúvidas? Abra uma issue ou consulte:
- [README principal](README.md)
- [Documentação da API](api/server.py)
