"""Read the local writeback ledger. Never talks to Google Sheets."""

from __future__ import annotations

import json
from pathlib import Path

from prediction_engine.houses import HOUSES

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "data" / "writeback_ledger.jsonl"

PUBLIC_KEYS = (
    "house",
    "kind",
    "target",
    "query",
    "claim",
    "url",
    "as_of",
    "used_xai",
    "xai_model",
    "note",
    "written_at",
    "remote",
)


def read_ledger(
    path: Path | None = None,
    limit: int = 50,
    house: str | None = None,
) -> list[dict]:
    target = path or DEFAULT_PATH
    if not target.is_file():
        return []
    rows: list[dict] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        raw = json.loads(line)
        if not isinstance(raw, dict):
            continue
        if house:
            if raw.get("house") != house:
                continue
        rows.append({k: raw.get(k) for k in PUBLIC_KEYS})
    return rows[-max(1, min(limit, 200)) :]


def append_local(row: dict, path: Path | None = None) -> dict:
    """Append a public-key row to the local JSONL ledger. Never remote."""
    from datetime import datetime, timezone

    from prediction_engine.writeback import validate_row

    cleaned = validate_row(row)
    cleaned["written_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cleaned["remote"] = False
    target = path or DEFAULT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(cleaned) + "\n")
    return cleaned


def ledger_summary(path: Path | None = None) -> dict:
    rows = read_ledger(path=path, limit=200)
    counts = {name: 0 for name in sorted(HOUSES)}
    for row in rows:
        name = row.get("house")
        if name in counts:
            counts[name] += 1
    return {
        "count": len(rows),
        "by_house": counts,
        "remote_writes": 0,
    }
