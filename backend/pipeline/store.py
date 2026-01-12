import json
from pathlib import Path


def _load_history(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def store(normalized_path: Path, store_dir: Path) -> None:
    normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
    items = normalized.get("items", [])
    updated_at = normalized.get("normalized_at")

    store_dir.mkdir(parents=True, exist_ok=True)
    prices_path = store_dir / "prices.json"
    history_path = store_dir / "history.json"

    prices_payload = {
        "updated_at": updated_at,
        "items": items,
    }
    prices_path.write_text(json.dumps(prices_payload, indent=2), encoding="utf-8")

    history = _load_history(history_path)
    for item in items:
        key = f"{item.get('game_id')}:{item.get('store')}:{item.get('region')}"
        history.setdefault(key, [])
        history[key].append(
            {
                "seen_at": updated_at,
                "price": item.get("price"),
                "currency": item.get("currency"),
                "discount_percent": item.get("discount_percent", 0),
            }
        )
        history[key] = history[key][-50:]

    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    store(root / "data" / "normalized" / "latest.json", root / "data" / "store")
