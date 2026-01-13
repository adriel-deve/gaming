"""
Atualizar ofertas-nintendo.html com dados reais
"""
import json
import re

# Ler os dados de vendas
with open('nintendo_sales_data.json', 'r', encoding='utf-8') as f:
    sales_data = json.load(f)

# Pegar TODOS os jogos (performance otimizada no frontend)
# sales_data já contém todos os jogos

# Gerar os dados JS
js_items = []
for game in sales_data:
    # Escapar aspas duplas no título
    title = game["title"].replace('"', '\\"')
    # Usar msrp_brl (preço original) e price_brl (preço com desconto)
    msrp_brl = game.get("msrp_brl", game["price_brl"])
    sale_price_brl = game["price_brl"]
    js_item = f'        {{ title: "{title}", discount_percent: {game["discount_percent"]}, msrp: {msrp_brl:.2f}, sale_price: {sale_price_brl:.2f}, currency: "BRL", region: "{game["region"]}", game_id: "{game["game_id"]}" }}'
    js_items.append(js_item)

new_function = f'''    // Dados reais de {len(sales_data)} jogos em promoção (scraped da Nintendo eShop US)
    // Total disponível: 1052 jogos | Mostrando os primeiros {len(sales_data)}
    function getDemoGames() {{
      return [
{",\\n".join(js_items)}
      ];
    }}'''

# Ler o arquivo HTML
with open('../ofertas-nintendo.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Encontrar e substituir a função
pattern = r'    // Dados reais.*?\n    function getDemoGames\(\) \{.*?\n      \];\n    \}'
replacement = new_function

html_content_updated = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

# Salvar
with open('../ofertas-nintendo.html', 'w', encoding='utf-8') as f:
    f.write(html_content_updated)

print(f'[OK] Página nintendo.html atualizada com {len(sales_data)} jogos!')
print(f'Dados salvos em: ../nintendo.html')
print(f'Total de jogos em promoção: {len(sales_data)}')
