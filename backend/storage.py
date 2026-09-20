"""Local, file-backed result store.

Replaces DynamoDB: results are written to a small JSON file on disk
(`data/results.json`) guarded by a lock, so results survive a server
restart without needing any external database. Fine for a demo /
single-instance app; swap for a real database if this ever needs to
run behind more than one worker process.
"""

import json
import threading
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent / "data"
RESULTS_FILE = DATA_DIR / "results.json"

_lock = threading.Lock()


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RESULTS_FILE.exists():
        RESULTS_FILE.write_text("{}", encoding="utf-8")


def _read_all() -> dict:
    _ensure_store()
    try:
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def save_result(item: dict) -> None:
    with _lock:
        data = _read_all()
        data[item["documentId"]] = item
        RESULTS_FILE.write_text(json.dumps(data, default=str), encoding="utf-8")


def get_result(document_id: str) -> Optional[dict]:
    with _lock:
        return _read_all().get(document_id)


def delete_result(document_id: str) -> bool:
    """Removes a stored result. Returns True if it existed, False if
    there was nothing to delete."""
    with _lock:
        data = _read_all()
        existed = data.pop(document_id, None) is not None
        if existed:
            RESULTS_FILE.write_text(json.dumps(data, default=str), encoding="utf-8")
        return existed


def list_results(limit: int = 20) -> list:
    with _lock:
        data = _read_all()
    items = sorted(data.values(), key=lambda i: i.get("createdAt", 0), reverse=True)
    return items[:limit]
