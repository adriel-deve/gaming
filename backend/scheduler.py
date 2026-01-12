import argparse
import json
import time
from pathlib import Path

from pipeline.run_pipeline import run


def load_config() -> dict:
    config_path = Path(__file__).resolve().parent / "config.json"
    if not config_path.exists():
        return {"refresh_minutes": 60}
    return json.loads(config_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single cycle.")
    args = parser.parse_args()

    config = load_config()
    refresh_minutes = int(config.get("refresh_minutes", 60))
    refresh_seconds = max(refresh_minutes, 1) * 60

    if args.once:
        run()
        return

    while True:
        run()
        time.sleep(refresh_seconds)


if __name__ == "__main__":
    main()
