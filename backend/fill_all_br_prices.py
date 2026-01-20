"""
Preenche preços BR para TODOS os 6438 jogos
- Jogos com preço BR real: mantém
- Jogos sem preço BR: calcula estimativa baseada no preço US

Taxa de conversão média: US$ 1 = R$ 5.80
Mas jogos Nintendo BR são mais caros proporcionalmente
"""
import json
from datetime import datetime

print("="*70)
print("PREENCHENDO PRECOS BR PARA TODOS OS JOGOS")
print("="*70)
print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Taxa de conversão USD -> BRL
# Baseado na análise de preços reais:
# US$ 59.99 (AAA games) = R$ 349 -> taxa efetiva = 5.82
# US$ 19.99 = R$ 119 -> taxa efetiva = 5.95
# Média: ~5.80
USD_TO_BRL = 5.80

# Taxas para outras moedas
EXCHANGE_RATES = {
    'USD': 5.80,
    'CAD': 4.20,
    'MXN': 0.32,
    'EUR': 6.35,
    'GBP': 7.45,
    'JPY': 0.039,
    'AUD': 3.85,
}

# Load current data
print("\n[1/4] Carregando dados atuais...")
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] {len(games)} jogos carregados")

# Count initial state
initial_with_br = sum(1 for g in games for p in g.get('prices', [])
                      if p.get('region') == 'BR' and p.get('msrp', 0) > 0)
print(f"[INFO] Jogos com preco BR inicial: {initial_with_br}")

# Fill missing BR prices
print("\n[2/4] Preenchendo precos BR faltantes...")
filled = 0
already_has = 0
no_source = 0

for game in games:
    prices = game.get('prices', [])
    if not prices:
        game['prices'] = []
        prices = game['prices']

    # Check if already has BR price
    has_br = False
    for p in prices:
        if p.get('region') == 'BR' and p.get('msrp', 0) > 0:
            has_br = True
            already_has += 1
            break

    if has_br:
        continue

    # Find best source for price estimation
    source_price = None
    source_currency = None
    source_region = None

    # Priority: US > CA > MX > any EUR country
    for region in ['US', 'CA', 'MX']:
        for p in prices:
            if p.get('region') == region and p.get('msrp', 0) > 0:
                source_price = p
                source_region = region
                source_currency = p.get('currency', 'USD')
                break
        if source_price:
            break

    # If no Americas price, try any price
    if not source_price:
        for p in prices:
            if p.get('msrp', 0) > 0:
                source_price = p
                source_region = p.get('region')
                source_currency = p.get('currency', 'USD')
                break

    if source_price:
        # Calculate BR price
        msrp_original = source_price.get('msrp', 0)
        sale_original = source_price.get('sale_price', msrp_original)
        discount = source_price.get('discount_percent', 0)
        on_sale = source_price.get('on_sale', discount > 0)

        # Convert to BRL
        rate = EXCHANGE_RATES.get(source_currency, 5.80)
        msrp_brl = round(msrp_original * rate, 2)
        sale_brl = round(sale_original * rate, 2)

        # Add BR price entry
        prices.append({
            'region': 'BR',
            'currency': 'BRL',
            'msrp': msrp_brl,
            'sale_price': sale_brl,
            'discount_percent': discount,
            'msrp_brl': msrp_brl,
            'price_brl': sale_brl,
            'on_sale': on_sale,
            'estimated': True,  # Flag to indicate this is estimated
            'source_region': source_region
        })
        filled += 1
    else:
        no_source += 1

print(f"[OK] {filled} precos BR estimados adicionados")
print(f"[INFO] {already_has} jogos ja tinham preco BR")
print(f"[WARN] {no_source} jogos sem nenhuma fonte de preco")

# Save
print("\n[3/4] Salvando dados...")
with open('multi_region_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("[OK] Salvo em multi_region_enriched.json")

# Final stats
print("\n[4/4] Estatisticas finais...")

final_with_br = sum(1 for g in games for p in g.get('prices', [])
                    if p.get('region') == 'BR' and p.get('msrp', 0) > 0)
total_on_sale = sum(1 for g in games for p in g.get('prices', [])
                    if p.get('region') == 'BR' and p.get('on_sale'))
estimated_count = sum(1 for g in games for p in g.get('prices', [])
                      if p.get('region') == 'BR' and p.get('estimated'))

print("\n" + "="*70)
print("RESUMO FINAL")
print("="*70)
print(f"Total de jogos: {len(games)}")
print(f"Jogos com preco BR (antes): {initial_with_br}")
print(f"Jogos com preco BR (depois): {final_with_br}")
print(f"  - Precos reais: {final_with_br - estimated_count}")
print(f"  - Precos estimados: {estimated_count}")
print(f"Jogos em promocao BR: {total_on_sale}")

# Show some examples of filled prices
print("\n" + "="*70)
print("EXEMPLOS DE PRECOS ESTIMADOS:")
print("="*70)

count = 0
for game in games:
    for p in game.get('prices', []):
        if p.get('region') == 'BR' and p.get('estimated'):
            src = p.get('source_region', '?')
            print(f"\n{game['title']}")
            print(f"  Estimado de {src}: R$ {p['msrp']:.2f}")
            if p.get('on_sale'):
                print(f"  Em promocao: R$ {p['sale_price']:.2f} (-{p['discount_percent']}%)")
            count += 1
            if count >= 15:
                break
    if count >= 15:
        break

print("\n" + "="*70)
print("CONCLUIDO!")
print("="*70)
