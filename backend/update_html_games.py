"""
Atualizar ofertas-nintendo.html com dados reais
"""
import json
import re

# Ler os dados de vendas
with open('nintendo_sales_data.json', 'r', encoding='utf-8') as f:
    sales_data = json.load(f)

# Pegar apenas os primeiros 50 jogos para manter a página rápida
sales_data = sales_data[:50]

# Gerar os dados JS
js_items = []
for game in sales_data:
    js_item = f'        {{ title: "{game["title"]}", discount_percent: {game["discount_percent"]}, msrp: {game["price_brl"]:.2f}, sale_price: {game["price_brl"]:.2f}, currency: "BRL", region: "{game["region"]}", game_id: "{game["game_id"]}" }}'
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

print(f'[OK] Página atualizada com {len(sales_data)} jogos em promoção!')
print(f'Total disponível: 1052 jogos')
