"""Portable product contracts only. No CPL/ROAS/CTR invented."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_PATH = ROOT / "data" / "mmm_contracts.json"


@lru_cache(maxsize=1)
def load_contracts() -> dict:
    return json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))


def list_contracts() -> list[dict]:
    return list(load_contracts().get("contracts") or [])
