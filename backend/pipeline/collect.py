import json
from datetime import datetime, timezone
from pathlib import Path

from providers.nintendo_eshop_provider import get_items


def collect(output_dir: Path) -> Path:
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "items": get_items(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "latest.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    collect(root / "data" / "raw")
