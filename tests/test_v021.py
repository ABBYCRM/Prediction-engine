from __future__ import annotations

from prediction_engine import __version__
from prediction_engine.analog_store import hit_summary, persist_hits
from prediction_engine.mcp import invoke
from prediction_engine.research import sources_for


def test_version_is_021():
    assert __version__ == "0.22.0"


def test_research_sources_public_only():
    urls = sources_for("ssdi")
    assert urls
    assert all(u.startswith("https://www.ssa.gov/") for u in urls)
    out = invoke("research.sources", {"house": "ssdi"})
    assert out["invented_market"] is False
    assert out["fetched"] is False
    assert out["count"] == len(urls)
    listed = invoke("research.list", {"house": "ssdi"})
    assert listed["invented_market"] is False
    assert "count" in listed


def test_analog_first_ts(tmp_path):
    path = tmp_path / "a.jsonl"
    persist_hits(
        "ssa.gov benefits",
        [{"id": "ssa-benefits", "kind": "policy", "url": "https://www.ssa.gov/benefits/disability/"}],
        path=path,
        house="ssdi",
    )
    stats = hit_summary(path=path, house="ssdi")
    assert stats["first_ts"]
    assert stats["last_ts"]
    assert stats["first_ts"] == stats["last_ts"]
    assert stats["invented_market"] is False
    empty = hit_summary(path=tmp_path / "none.jsonl")
    assert empty["first_ts"] is None


def test_mcp_calibration_brier():
    out = invoke("calibration.brier", {"house": "pi"})
    assert out["invented_market"] is False
    assert "mean_brier" in out
    assert "count" in out
    assert "cpl" not in str(out).lower()
    assert "roas" not in str(out).lower()
