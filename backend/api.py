"""
API simples para servir dados dos jogos Nintendo
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from providers.nintendo_extended_data import get_all_games_with_prices

class GameAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        if self.path == '/api/nintendo/games':
            # Buscar todos os jogos
            games = get_all_games_with_prices(
                regions=["US", "BR", "GB", "DE", "FR", "JP", "MX", "AR"]
            )

            # Converter para formato JSON
            self.wfile.write(json.dumps(games, ensure_ascii=False).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Silenciar logs do servidor
        pass

def run_server(port=8000):
    server = HTTPServer(('localhost', port), GameAPIHandler)
    print(f"Servidor rodando em http://localhost:{port}")
    print(f"API disponível em: http://localhost:{port}/api/nintendo/games")
    print("Pressione Ctrl+C para parar")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado")
        server.shutdown()

if __name__ == '__main__':
    run_server()
