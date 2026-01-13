"""
Converter dados de promoções do JSON para formato JavaScript
"""
import json
import sys

def convert_to_js_format():
    # Ler dados do JSON
    with open('nintendo_sales_data.json', 'r', encoding='utf-8') as f:
        sales_data = json.load(f)

    # Converter para formato JS
    js_games = []
    for game in sales_data:
        js_game = {
            'title': game['title'],
            'discount_percent': game['discount_percent'],
            'msrp': game['price_brl'],  # Já em BRL
            'sale_price': game['price_brl'],  # Já em BRL
            'currency': 'BRL',
            'region': game['region'],
            'game_id': game['game_id']
        }
        js_games.append(js_game)

    # Gerar código JavaScript
    print('    // Dados reais de ' + str(len(js_games)) + ' jogos em promoção (atualizado automaticamente)')
    print('    function getDemoGames() {')
    print('      return [')

    # Mostrar apenas os primeiros 100 jogos (para não deixar o arquivo muito grande)
    for i, game in enumerate(js_games[:100]):
        line = f"        {{ title: \"{game['title']}\", discount_percent: {game['discount_percent']}, msrp: {game['msrp']:.2f}, sale_price: {game['sale_price']:.2f}, currency: \"{game['currency']}\", region: \"{game['region']}\", game_id: \"{game['game_id']}\" }}"
        if i < min(len(js_games), 100) - 1:
            line += ','
        print(line)

    print('      ];')
    print('    }')

    print(f'\n// Total de jogos disponíveis: {len(js_games)}', file=sys.stderr)
    print(f'// Mostrando os primeiros 100 jogos', file=sys.stderr)

if __name__ == '__main__':
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    convert_to_js_format()
