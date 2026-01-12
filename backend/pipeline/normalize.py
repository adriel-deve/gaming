import json
import re
from datetime import datetime, timezone
from pathlib import Path


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def _normalize_item(item: dict) -> dict:
    msrp = item.get("msrp")
    sale_price = item.get("sale_price")
    price = sale_price if sale_price is not None else msrp
    discount = item.get("discount_percent", 0)

    if discount == 0 and msrp and sale_price:
        discount = round((1 - (sale_price / msrp)) * 100)

    return {
        "game_id": _slugify(item.get("title", "")),
        "title": item.get("title", "Unknown"),
        "store": item.get("store", "unknown"),
        "platform": item.get("platform", "unknown"),
        "region": item.get("region", "unknown"),
        "currency": item.get("currency", "USD"),
        "price": price,
        "msrp": msrp,
        "discount_percent": discount,
        "url": item.get("url"),
        "cover_url": item.get("cover_url"),
    }


def normalize(raw_path: Path, output_dir: Path) -> Path:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    items = [_normalize_item(item) for item in raw.get("items", [])]

    payload = {
        "normalized_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "latest.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    normalize(root / "data" / "raw" / "latest.json", root / "data" / "normalized")
