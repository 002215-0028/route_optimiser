import json
from pathlib import Path

CACHE_DIR = Path(".cache")


def load_cache(name: str) -> dict:
    path = CACHE_DIR / f"{name}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(name: str, cache: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"{name}.json"
    path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")