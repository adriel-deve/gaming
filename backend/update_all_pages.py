"""
Atualizar TODAS as páginas com dados reais
Executa:
1. Scraper Node.js (busca dados da eShop)
2. Atualiza ofertas-nintendo.html
3. Atualiza nintendo.html
"""
import json
import re
import subprocess
import sys
import os

def run_scraper():
    """Executar scraper Node.js"""
    print("="*60)
    print("1. EXECUTANDO SCRAPER...")
    print("="*60)

    result = subprocess.run(
        ['node', 'nintendo_scraper.js'],
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        print("[OK] Scraper executado com sucesso!")
        return True
    else:
        print("[ERRO] Falha ao executar scraper:")
        print(result.stderr)
        return False

def update_ofertas_nintendo():
    """Atualizar ofertas-nintendo.html"""
    print("\n" + "="*60)
    print("2. ATUALIZANDO ofertas-nintendo.html...")
    print("="*60)

    # Ler dados
    with open('nintendo_sales_data.json', 'r', encoding='utf-8') as f:
        sales_data = json.load(f)

    # Gerar JS
    js_items = []
    for game in sales_data:
        js_item = f'        {{ title: "{game["title"]}", discount_percent: {game["discount_percent"]}, msrp: {game["price_brl"]:.2f}, sale_price: {game["price_brl"]:.2f}, currency: "BRL", region: "{game["region"]}", game_id: "{game["game_id"]}" }}'
        js_items.append(js_item)

    new_function = f'''    // Dados reais de {len(sales_data)} jogos em promoção (scraped da Nintendo eShop US)
    // Atualizado automaticamente a cada 6 horas
    function getDemoGames() {{
      return [
{",\\n".join(js_items)}
      ];
    }}'''

    # Ler HTML
    with open('../ofertas-nintendo.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Substituir
    pattern = r'    // Dados reais.*?\n    function getDemoGames\(\) \{.*?\n      \];\n    \}'
    html_content_updated = re.sub(pattern, new_function, html_content, flags=re.DOTALL)

    # Salvar
    with open('../ofertas-nintendo.html', 'w', encoding='utf-8') as f:
        f.write(html_content_updated)

    print(f"[OK] ofertas-nintendo.html atualizada com {len(sales_data)} jogos!")

def update_nintendo_page():
    """Atualizar nintendo.html"""
    print("\n" + "="*60)
    print("3. ATUALIZANDO nintendo.html...")
    print("="*60)

    # Ler dados
    with open('nintendo_sales_data.json', 'r', encoding='utf-8') as f:
        sales_data = json.load(f)

    # Gerar JS
    js_items = []
    for game in sales_data:
        js_item = f'        {{ title: "{game["title"]}", discount_percent: {game["discount_percent"]}, msrp: {game["price_brl"]:.2f}, sale_price: {game["price_brl"]:.2f}, currency: "BRL", region: "{game["region"]}", game_id: "{game["game_id"]}" }}'
        js_items.append(js_item)

    new_function = f'''    // Dados locais (backup)
    function getLocalGames() {{
      // Atualizado automaticamente a cada 6 horas via GitHub Actions
      // Total: {len(sales_data)} jogos em promoção
      return [
{",\\n".join(js_items)}
      ];
    }}'''

    # Ler HTML
    with open('../nintendo.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Substituir
    pattern = r'    // Dados locais \(backup\).*?\n    function getLocalGames\(\) \{.*?\n      \];\n    \}'
    html_content_updated = re.sub(pattern, new_function, html_content, flags=re.DOTALL)

    # Salvar
    with open('../nintendo.html', 'w', encoding='utf-8') as f:
        f.write(html_content_updated)

    print(f"[OK] nintendo.html atualizada com {len(sales_data)} jogos!")

def main():
    print("PIPELINE DE ATUALIZAÇÃO - ESHOP PULSE")
    print("="*60)

    # 1. Executar scraper
    if not run_scraper():
        print("\n[ERRO] Falha no scraper. Usando dados existentes.")

    # 2. Atualizar ofertas-nintendo.html
    try:
        update_ofertas_nintendo()
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar ofertas-nintendo.html: {e}")

    # 3. Atualizar nintendo.html
    try:
        update_nintendo_page()
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar nintendo.html: {e}")

    print("\n" + "="*60)
    print("PIPELINE CONCLUÍDO!")
    print("="*60)
    print("\nPróximos passos:")
    print("1. git add -A")
    print("2. git commit -m 'update: Atualizar dados dos jogos'")
    print("3. git push")

if __name__ == '__main__':
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    main()
