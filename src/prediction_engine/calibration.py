"""Local probability calibration scores.

Records only caller-supplied p and y. Never invents CPL, ROAS, or market rates.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prediction_engine.houses import HOUSES, HouseError, assert_single_house

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "data" / "calibration_ledger.jsonl"


class CalibrationError(ValueError):
    pass


def _as_prob(value: Any, name: str) -> float:
    try:
        p = float(value)
    except (TypeError, ValueError) as exc:
        raise CalibrationError(f"{name} must be a number") from exc
    if p < 0.0 or p > 1.0:
        raise CalibrationError(f"{name} must be in [0, 1]")
    return p


def _as_label(value: Any) -> int:
    if value in (0, 1, True, False, "0", "1"):
        return int(value) if value not in (True, False) else (1 if value else 0)
    raise CalibrationError("y must be 0 or 1")


def brier(p: float, y: int) -> float:
    return (p - y) ** 2


def record(
    p: Any,
    y: Any,
    *,
    house: str,
    query: str = "",
    path: Path | None = None,
) -> dict[str, Any]:
    house_s = assert_single_house(house, {"house": house})
    if house_s not in HOUSES:
        raise HouseError(f"unknown house: {house_s}")
    prob = _as_prob(p, "p")
    label = _as_label(y)
    score = brier(prob, label)
    row = {
        "house": house_s,
        "query": str(query or ""),
        "p": prob,
        "y": label,
        "brier": score,
        "written_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "caller",
        "invented_market": False,
    }
    target = path or DEFAULT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def read_scores(path: Path | None = None, house: str | None = None) -> list[dict]:
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
        if house and raw.get("house") != house:
            continue
        rows.append(raw)
    return rows


def summary(path: Path | None = None, house: str | None = None) -> dict[str, Any]:
    rows = read_scores(path=path, house=house)
    if not rows:
        return {
            "count": 0,
            "mean_brier": None,
            "house": house,
            "invented_market": False,
        }
    mean = sum(float(r["brier"]) for r in rows) / len(rows)
    return {
        "count": len(rows),
        "mean_brier": mean,
        "house": house,
        "invented_market": False,
    }
