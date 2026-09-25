"""House-isolated live research runs. Never invents CPC/CTR; records fetch errors."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prediction_engine.houses import HOUSES, HouseError, assert_single_house

ROOT = Path(__file__).resolve().parents[2]
LIVE_DIR = ROOT / "data" / "live_runs"


class ResearchError(ValueError):
    pass


def live_dir() -> Path:
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    return LIVE_DIR


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_run(
    house: str,
    kind: str,
    items: list[dict[str, Any]],
    *,
    note: str = "",
    xai_attempted: bool = False,
    xai_error: str | None = None,
    path: Path | None = None,
) -> Path:
    name = assert_single_house(house)
    if kind not in {"competitor", "keyword", "policy"}:
        raise ResearchError(f"unknown run kind: {kind}")
    for item in items:
        if "kind" not in item:
            raise ResearchError("each item needs kind=fact|prediction|observation")
        if item["kind"] == "fact":
            if not item.get("url") or not item.get("as_of"):
                raise ResearchError("facts require url and as_of")
        claim = str(item.get("claim") or "")
        lowered = claim.lower()
        if any(tok in lowered for tok in ("cpc", "ctr", "cpl", "roas")) or "%" in claim:
            raise ResearchError("refusing performance metrics in live run items")
    payload = {
        "house": name,
        "kind": kind,
        "as_of": _now_iso(),
        "xai_attempted": xai_attempted,
        "xai_error": xai_error,
        "note": note,
        "items": items,
        "mixed_house": False,
    }
    dest = path or (live_dir() / f"{name}_{kind}_{payload['as_of'].replace(':', '')}.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return dest


def list_runs(house: str | None = None) -> list[Path]:
    if not LIVE_DIR.exists():
        return []
    files = sorted(LIVE_DIR.glob("*.json"))
    if house is None:
        return files
    name = assert_single_house(house)
    return [p for p in files if p.name.startswith(f"{name}_")]


def assert_runs_not_mixed() -> None:
    for path in list_runs():
        data = json.loads(path.read_text(encoding="utf-8"))
        house = data.get("house")
        if house not in HOUSES:
            raise HouseError(f"live run missing house: {path}")
        blob = json.dumps(data).lower()
        if house == "pi" and "ssa.gov" in blob:
            raise HouseError(f"PI run cites SSA: {path}")
        if house == "ssdi" and ("caseclosed" in blob or "already_represented" in blob):
            raise HouseError(f"SSDI run mixed PI keys: {path}")
