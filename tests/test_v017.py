from __future__ import annotations

from prediction_engine import __version__
from prediction_engine.analog_store import hit_summary, persist_hits
from prediction_engine.calibration import record, reliability_buckets, summary
from prediction_engine.mcp import invoke


def test_version_is_017():
    assert __version__ == "0.24.0"


def test_reliability_buckets_split(tmp_path):
    path = tmp_path / "c.jsonl"
    record(0.1, 0, house="pi", path=path)
    record(0.9, 1, house="pi", path=path)
    stats = summary(path=path, house="pi")
    assert stats["count"] == 2
    assert "buckets" in stats
    assert len(stats["buckets"]) == 5
    filled = [b for b in stats["buckets"] if b["count"]]
    assert len(filled) == 2
    assert all("cpl" not in str(b).lower() for b in stats["buckets"])
    empty = reliability_buckets([])
    assert empty[0]["count"] == 0
    assert empty[0]["mean_p"] is None


def test_analog_hit_summary(tmp_path):
    path = tmp_path / "a.jsonl"
    persist_hits(
        "ssa.gov policy",
        [{"id": "ssa-home", "kind": "policy", "analog_score": 1.0, "url": "https://www.ssa.gov/"}],
        path=path,
        house="ssdi",
    )
    stats = hit_summary(path=path, house="ssdi")
    assert stats["queries"] == 1
    assert stats["hits"] == 1
    assert stats["by_kind"]["policy"] == 1
    assert stats["invented_market"] is False
    assert "roas" not in str(stats).lower()


def test_mcp_analog_summary():
    out = invoke("analog.summary", {"house": "pi"})
    assert out["invented_market"] is False
    assert "queries" in out
    assert "hits" in out
