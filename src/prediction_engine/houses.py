"""PI (CaseClosedFL) and SSDI are separate houses. Never mix payloads."""

from __future__ import annotations

HOUSES = frozenset({"pi", "ssdi"})


class HouseError(ValueError):
    pass


def assert_single_house(house: str, payload: dict | None = None) -> str:
    name = (house or "").strip().lower()
    if name not in HOUSES:
        raise HouseError(f"unknown house: {house!r}")
    blob = payload or {}
    foreign = set()
    if name == "pi":
        for key in ("ssdi", "disability", "ssa_claim"):
            if key in blob:
                foreign.add(key)
    else:
        for key in ("already_represented", "primary_fault", "mva", "caseclosed"):
            if key in blob:
                foreign.add(key)
    if foreign:
        raise HouseError(f"refusing mixed-house payload keys: {sorted(foreign)}")
    return name


def bridge_10_to_0(house: str) -> dict:
    """10→0: drop every field that is not the named house."""
    name = assert_single_house(house)
    return {"house": name, "mode": "10_to_0", "keep": [name], "drop": sorted(HOUSES - {name})}


def bridge_0_to_1(house: str) -> dict:
    """0→1: open an empty ledger for one house only."""
    name = assert_single_house(house)
    return {"house": name, "mode": "0_to_1", "ledger": [], "mixed": False}
