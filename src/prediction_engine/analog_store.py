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


def hit_summary(path: Path | None = None, house: str | None = None) -> dict:
    """Count analog retrievals only. No CPL/ROAS."""
    rows = read_hits(path=path, limit=200, house=house)
    n_hits = 0
    max_hits = 0
    by_kind: dict[str, int] = {}
    ids: set[str] = set()
    for row in rows:
        hits = row.get("hits") or []
        if not isinstance(hits, list):
            continue
        n_hits += len(hits)
        if len(hits) > max_hits:
            max_hits = len(hits)
        for item in hits:
            if not isinstance(item, dict):
                continue
            kind = str(item.get("kind") or "unknown")
            by_kind[kind] = by_kind.get(kind, 0) + 1
            hid = item.get("id")
            if hid:
                ids.add(str(hid))
    last_ts = None
    first_ts = None
    for row in rows:
        ts = row.get("ts")
        if not ts:
            continue
        s = str(ts)
        if last_ts is None or s > str(last_ts):
            last_ts = ts
        if first_ts is None or s < str(first_ts):
            first_ts = ts
    n_q = len(rows)
    mean_hits = (n_hits / n_q) if n_q else None
    return {
        "queries": n_q,
        "hits": n_hits,
        "unique_ids": len(ids),
        "mean_hits_per_query": mean_hits,
        "max_hits_in_query": max_hits if n_q else None,
        "by_kind": by_kind,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "house": house,
        "invented_market": False,
    }
