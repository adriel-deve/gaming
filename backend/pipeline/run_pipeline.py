import sys
from pathlib import Path

# Adiciona o diretório pai ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.collect import collect
from pipeline.normalize import normalize
from pipeline.store import store


def run() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "data" / "raw"
    normalized_dir = root / "data" / "normalized"
    store_dir = root / "data" / "store"

    raw_path = collect(raw_dir)
    normalized_path = normalize(raw_path, normalized_dir)
    store(normalized_path, store_dir)


if __name__ == "__main__":
    run()
