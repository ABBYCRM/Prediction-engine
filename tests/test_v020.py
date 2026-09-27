from __future__ import annotations

import pytest

from prediction_engine import __version__
from prediction_engine.mcp import invoke
from prediction_engine.oauth import OAuthError, google_ads_live_get, meta_ads_live_get
from prediction_engine.research import cite_house_sources, write_run
from prediction_engine.writeback import row_values, sheet_header, validate_row


def test_version_is_020():
    assert __version__ == "0.22.0"


def test_writeback_sheet_header_and_values():
    header = sheet_header()
    assert header[0] == "house"
    assert "claim" in header
    row = validate_row(
        {
            "house": "pi",
            "kind": "prediction",
            "target": "local_jsonl",
            "query": "policy",
            "claim": "Prediction: test only, no bids",
        }
    )
    vals = row_values(row)
    assert len(vals) == len(header)
    assert vals[0] == "pi"
    assert "cpl" not in "".join(vals).lower()


def test_oauth_live_get_refuses_without_tokens():
    with pytest.raises(OAuthError):
        google_ads_live_get("/customers")
    with pytest.raises(OAuthError):
        meta_ads_live_get("/act_0/insights")


def test_cite_and_write_run_isolates_houses(tmp_path):
    items = [
        {
            "kind": "fact",
            "claim": "Public SSA disability landing page exists",
            "url": "https://www.ssa.gov/disability/",
            "as_of": "2026-09-27",
        }
    ]
    dest = write_run("ssdi", "competitor", items, path=tmp_path / "ssdi_competitor_test.json")
    assert dest.exists()
    listed = invoke("research.list", {"house": "ssdi"})
    assert listed["invented_market"] is False
    assert "count" in listed


def test_cite_house_sources_returns_url_as_of():
    rows = cite_house_sources("ssdi")
    assert rows
    for row in rows:
        assert row.get("url")
        assert row.get("as_of")
        assert row["kind"] in {"fact", "observation"}
        lowered = str(row.get("claim") or "").lower()
        assert "cpc" not in lowered
        assert "roas" not in lowered
