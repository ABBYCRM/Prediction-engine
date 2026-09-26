"""PI (CaseClosedFL) and SSDI are separate houses. Never mix payloads."""

from __future__ import annotations

from pathlib import Path

HOUSES = frozenset({"pi", "ssdi"})

ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "data" / "house_ledgers"

PI_KEYS = frozenset({"already_represented", "primary_fault", "mva", "caseclosed"})
SSDI_KEYS = frozenset({"ssdi", "disability", "ssa_claim"})


class HouseError(ValueError):
    pass


def assert_single_house(house: str, payload: dict | None = None) -> str:
    name = (house or "").strip().lower()
    if name not in HOUSES:
        raise HouseError(f"unknown house: {house!r}")
    blob = payload or {}
    foreign = set()
    if name == "pi":
        for key in SSDI_KEYS:
            if key in blob:
                foreign.add(key)
    else:
        for key in PI_KEYS:
            if key in blob:
                foreign.add(key)
    if foreign:
        raise HouseError(f"refusing mixed-house payload keys: {sorted(foreign)}")
    return name


def apply_10_to_0(house: str, payload: dict | None = None) -> dict:
    """Drop every field that belongs to the other house. Does not invent values."""
    name = (house or "").strip().lower()
    if name not in HOUSES:
        raise HouseError(f"unknown house: {house!r}")
    src = dict(payload or {})
    drop_keys = SSDI_KEYS if name == "pi" else PI_KEYS
    kept = {k: v for k, v in src.items() if k not in drop_keys}
    dropped = sorted(k for k in src if k in drop_keys)
    return {
        "house": name,
        "mode": "10_to_0",
        "keep": [name],
        "drop": sorted(HOUSES - {name}),
        "payload": kept,
        "dropped_keys": dropped,
        "mixed": False,
    }


def bridge_10_to_0(house: str, payload: dict | None = None) -> dict:
    """10-to-0: drop every field that is not the named house."""
    if payload:
        return apply_10_to_0(house, payload)
    name = assert_single_house(house)
    return {"house": name, "mode": "10_to_0", "keep": [name], "drop": sorted(HOUSES - {name})}


def seed_0_to_1(house: str, path: Path | None = None) -> Path:
    """Create an empty per-house ledger file if missing. Never copies the other house."""
    name = assert_single_house(house)
    target = path or (LEDGER_DIR / f"{name}.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text("", encoding="utf-8")
    return target


def bridge_0_to_1(house: str) -> dict:
    """0-to-1: open an empty ledger for one house only."""
    name = assert_single_house(house)
    path = seed_0_to_1(name)
    return {
        "house": name,
        "mode": "0_to_1",
        "ledger": [],
        "mixed": False,
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "seeded": path.exists(),
    }
