"""Append-only analog hit log. No metrics invented; stores retrieval ids only."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "data" / "analog_hits.jsonl"


def persist_hits(
    query: str,
    hits: list[dict],
    path: Path | None = None,
    house: str | None = None,
) -> Path:
    target = path or DEFAULT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "house": house,
        "hits": [
            {
                "id": item.get("id"),
                "kind": item.get("kind"),
                "analog_score": item.get("analog_score"),
                "url": item.get("url"),
            }
            for item in hits
        ],
    }
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    return target


def read_hits(
    path: Path | None = None,
    limit: int = 50,
    house: str | None = None,
) -> list[dict]:
    target = path or DEFAULT_PATH
    if not target.is_file():
        return []
    lines = target.read_text(encoding="utf-8").splitlines()
    out: list[dict] = []
    wanted = (house or "").strip() or None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if wanted and row.get("house") != wanted:
            continue
        out.append(row)
    if limit < 1:
        limit = 1
    return out[-limit:]
