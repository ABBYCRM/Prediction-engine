from __future__ import annotations

from prediction_engine import __version__
from prediction_engine.analog import retrieve
from prediction_engine.contracts import list_contracts
from prediction_engine.houses import bridge_0_to_1, bridge_10_to_0
from prediction_engine.mcp import invoke


def test_version_is_015():
    assert __version__ == "0.15.0"


def test_geox_and_robyn_contracts_present():
    ids = {c["id"] for c in list_contracts()}
    assert "meridian-geox-design" in ids
    assert "meridian-geox-interventions" in ids
    assert "robyn-calibration-point" in ids
    geox = next(c for c in list_contracts() if c["id"] == "meridian-geox-interventions")
    assert "holdback" in geox["fields"]
    assert "go-dark" in geox["fields"]
    assert "heavy-up" in geox["fields"]
    assert geox["url"].startswith("https://developers.google.com/meridian/")
    assert geox.get("as_of")


def test_analog_retrieves_geox_contract():
    hits = retrieve("geox holdback go-dark heavy-up experiment")
    kinds = {h.get("kind") for h in hits}
    assert "portable_contract" in kinds
    ids = [h.get("id") for h in hits]
    assert any(i and str(i).startswith("meridian-geox") for i in ids)


def test_house_bridges_do_not_mix():
    ten = bridge_10_to_0("pi")
    assert ten["keep"] == ["pi"]
    assert ten["drop"] == ["ssdi"]
    one = bridge_0_to_1("ssdi")
    assert one["house"] == "ssdi"
    assert one["mixed"] is False
    out = invoke("house.bridge", {"house": "pi", "mode": "10_to_0"})
    assert out["keep"] == ["pi"]
