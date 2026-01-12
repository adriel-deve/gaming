import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def _load_prices() -> dict:
    root = Path(__file__).resolve().parents[1]
    prices_path = root / "data" / "store" / "prices.json"
    if not prices_path.exists():
        return {"updated_at": None, "items": []}
    return json.loads(prices_path.read_text(encoding="utf-8"))


class ApiHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _filter_items(self, items, params):
        store = params.get("store", [None])[0]
        region = params.get("region", [None])[0]
        platform = params.get("platform", [None])[0]
        on_sale = params.get("on_sale", [None])[0]

        def matches(item):
            if store and item.get("store") != store:
                return False
            if region and item.get("region") != region:
                return False
            if platform and item.get("platform") != platform:
                return False
            if on_sale in ("1", "true") and item.get("discount_percent", 0) <= 0:
                return False
            return True

        return [item for item in items if matches(item)]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        data = _load_prices()
        items = data.get("items", [])

        if parsed.path == "/api/health":
            self._send_json(200, {"status": "ok", "updated_at": data.get("updated_at")})
            return

        if parsed.path == "/api/offers":
            filtered = self._filter_items(items, params)
            self._send_json(
                200,
                {"updated_at": data.get("updated_at"), "items": filtered},
            )
            return

        if parsed.path == "/api/games":
            filtered = self._filter_items(items, params)
            games = {}
            for item in filtered:
                game_id = item.get("game_id")
                if game_id not in games:
                    games[game_id] = {
                        "game_id": game_id,
                        "title": item.get("title"),
                        "platform": item.get("platform"),
                    }
            game_list = sorted(games.values(), key=lambda g: g.get("title", ""))
            self._send_json(200, {"items": game_list})
            return

        if parsed.path == "/api/prices":
            game_id = params.get("game_id", [None])[0]
            if not game_id:
                self._send_json(400, {"error": "game_id is required"})
                return
            filtered = [item for item in items if item.get("game_id") == game_id]
            self._send_json(200, {"game_id": game_id, "items": filtered})
            return

        self._send_json(404, {"error": "not_found"})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()

    server = HTTPServer(("127.0.0.1", args.port), ApiHandler)
    print(f"API server running on http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
