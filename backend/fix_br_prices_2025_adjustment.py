"""
Corrige precos BR que ainda estao com valores de 2024
Em 2025 a Nintendo reajustou os precos no Brasil:
- R$ 249 -> R$ 299 (+20%)
- R$ 299 -> R$ 349 (+16.7%)
- R$ 357 -> R$ 399 (+11.8%)

Este script detecta precos que parecem estar defasados
e aplica a correcao apropriada.
"""
import json
from datetime import datetime

print("="*70)
print("CORRECAO DE PRECOS BR - REAJUSTE 2025")
print("="*70)
print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Mapeamento de precos antigos -> novos (2025)
# Baseado no reajuste oficial da Nintendo Brasil
PRICE_CORRECTIONS = {
    # Faixa baixa (jogos indie/menores)
    39.90: 49.90,
    49.90: 59.90,
    59.90: 69.90,
    69.90: 79.90,
    79.90: 89.90,
    89.90: 99.90,
    99.90: 119.00,

    # Faixa media
    119.00: 139.00,
    129.00: 149.00,
    139.00: 159.00,
    149.00: 169.00,
    159.00: 179.00,
    169.00: 189.00,
    179.00: 199.00,
    189.00: 209.00,
    199.00: 229.00,
    199.90: 229.00,

    # Faixa alta (jogos AAA)
    229.00: 269.00,
    249.00: 299.00,
    249.90: 299.00,
    269.00: 299.00,
    279.00: 319.00,
    289.00: 329.00,
    299.00: 349.00,
    299.90: 349.00,

    # Faixa premium
    319.00: 369.00,
    329.00: 379.00,
    339.00: 389.00,
    349.00: 399.00,
    357.00: 399.00,
    359.00: 399.00,
    369.00: 419.00,
    379.00: 429.00,
    389.00: 439.00,
    399.00: 449.00,
}

# Fator de correcao geral para precos nao mapeados
# Baseado na media dos reajustes (~15-17%)
GENERAL_CORRECTION_FACTOR = 1.165

def should_correct_price(price):
    """Verifica se o preco parece estar defasado (valor de 2024)"""
    # Precos que terminam em .90 ou .00 e estao na faixa conhecida
    # sao provavelmente precos antigos

    # Verificar se esta no mapeamento direto
    for old_price in PRICE_CORRECTIONS.keys():
        if abs(price - old_price) < 0.5:  # Tolerancia de 50 centavos
            return True

    return False

def get_corrected_price(price):
    """Retorna o preco corrigido"""
    # Primeiro tentar mapeamento direto
    for old_price, new_price in PRICE_CORRECTIONS.items():
        if abs(price - old_price) < 0.5:
            return new_price

    # Se nao encontrar, aplicar fator geral
    return round(price * GENERAL_CORRECTION_FACTOR, 2)

# Carregar dados
print("\n[1/4] Carregando dados...")
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] {len(games)} jogos carregados")

# Analisar precos BR atuais
print("\n[2/4] Analisando precos BR...")

price_distribution = {}
corrections_needed = []

for game in games:
    for price in game.get('prices', []):
        if price.get('region') == 'BR' and price.get('msrp', 0) > 0:
            msrp = price['msrp']

            # Contar distribuicao
            rounded = round(msrp)
            price_distribution[rounded] = price_distribution.get(rounded, 0) + 1

            # Verificar se precisa correcao
            if should_correct_price(msrp):
                corrections_needed.append({
                    'title': game['title'],
                    'old_price': msrp,
                    'new_price': get_corrected_price(msrp)
                })

print(f"[OK] {len(corrections_needed)} jogos precisam de correcao")

# Mostrar distribuicao atual
print("\n[INFO] Top 20 precos mais comuns (ANTES da correcao):")
sorted_prices = sorted(price_distribution.items(), key=lambda x: -x[1])
for price, count in sorted_prices[:20]:
    needs_fix = "[CORRIGIR]" if any(abs(price - p) < 1 for p in PRICE_CORRECTIONS.keys()) else ""
    print(f"  R$ {price}: {count} jogos {needs_fix}")

# Aplicar correcoes
print("\n[3/4] Aplicando correcoes...")
corrected = 0
skipped = 0

for game in games:
    for price in game.get('prices', []):
        if price.get('region') == 'BR':
            old_msrp = price.get('msrp', 0)
            old_sale = price.get('sale_price', old_msrp)

            if old_msrp > 0 and should_correct_price(old_msrp):
                # Aplicar correcao
                new_msrp = get_corrected_price(old_msrp)

                # Se estava em promocao, manter o desconto percentual
                if price.get('on_sale') and old_sale < old_msrp:
                    discount_pct = price.get('discount_percent', 0)
                    if discount_pct > 0:
                        new_sale = round(new_msrp * (1 - discount_pct / 100), 2)
                    else:
                        # Calcular desconto do preco antigo
                        old_discount = round((1 - old_sale / old_msrp) * 100)
                        new_sale = round(new_msrp * (1 - old_discount / 100), 2)
                else:
                    new_sale = new_msrp

                # Atualizar
                price['msrp'] = new_msrp
                price['sale_price'] = new_sale
                price['msrp_brl'] = new_msrp
                price['price_brl'] = new_sale

                # Marcar como corrigido
                price['corrected_2025'] = True

                corrected += 1
            else:
                skipped += 1

print(f"[OK] {corrected} precos corrigidos")
print(f"[INFO] {skipped} precos BR mantidos (ja estavam corretos)")

# Salvar
print("\n[4/4] Salvando dados...")
with open('multi_region_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("[OK] Salvo em multi_region_enriched.json")

# Estatisticas finais
print("\n" + "="*70)
print("RESUMO DA CORRECAO")
print("="*70)

# Nova distribuicao
new_distribution = {}
for game in games:
    for price in game.get('prices', []):
        if price.get('region') == 'BR' and price.get('msrp', 0) > 0:
            rounded = round(price['msrp'])
            new_distribution[rounded] = new_distribution.get(rounded, 0) + 1

print("\nTop 20 precos mais comuns (DEPOIS da correcao):")
sorted_new = sorted(new_distribution.items(), key=lambda x: -x[1])
for price, count in sorted_new[:20]:
    print(f"  R$ {price}: {count} jogos")

# Exemplos de correcoes
print("\n" + "="*70)
print("EXEMPLOS DE CORRECOES APLICADAS:")
print("="*70)

count = 0
for game in games:
    for price in game.get('prices', []):
        if price.get('region') == 'BR' and price.get('corrected_2025'):
            print(f"\n{game['title']}")
            # Encontrar o preco original na lista de correcoes
            for corr in corrections_needed:
                if corr['title'] == game['title']:
                    print(f"  R$ {corr['old_price']:.2f} -> R$ {price['msrp']:.2f}")
                    if price.get('on_sale'):
                        print(f"  Em promocao: R$ {price['sale_price']:.2f} (-{price.get('discount_percent', 0)}%)")
                    break
            count += 1
            if count >= 20:
                break
    if count >= 20:
        break

print("\n" + "="*70)
print("CONCLUIDO!")
print("="*70)
