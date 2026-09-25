"""CRM / Sheets writeback schema. No live sheet writes without OAuth."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prediction_engine.houses import assert_single_house

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "data" / "writeback_schema.json"

ALLOWED_TARGETS = frozenset({"sheets", "hubspot_readonly_note", "local_jsonl"})


class WritebackError(ValueError):
    pass


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    house = assert_single_house(str(row.get("house") or ""), row)
    kind = row.get("kind")
    if kind not in {"fact", "prediction", "observation"}:
        raise WritebackError("kind must be fact|prediction|observation")
    target = row.get("target")
    if target not in ALLOWED_TARGETS:
        raise WritebackError(f"unknown target: {target}")
    if kind == "fact" and (not row.get("url") or not row.get("as_of")):
        raise WritebackError("facts require url and as_of")
    if row.get("used_xai") and not row.get("xai_model"):
        raise WritebackError("used_xai rows must name xai_model")
    return {
        "house": house,
        "kind": kind,
        "target": target,
        "query": str(row.get("query") or ""),
        "claim": str(row.get("claim") or ""),
        "url": row.get("url"),
        "as_of": row.get("as_of"),
        "used_xai": bool(row.get("used_xai")),
        "xai_model": row.get("xai_model"),
        "note": str(row.get("note") or ""),
    }
