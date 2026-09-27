from __future__ import annotations

from prediction_engine import __version__
from prediction_engine.analog_store import hit_summary, persist_hits
from prediction_engine.calibration import record, summary
from prediction_engine.mcp import invoke


def test_version_is_023():
    assert __version__ == "0.23.0"


def test_analog_max_hits_in_query(tmp_path):
    path = tmp_path / "a.jsonl"
    persist_hits(
        "ssa.gov benefits",
        [{"id": "ssa-benefits", "kind": "policy", "url": "https://www.ssa.gov/benefits/disability/"}],
        path=path,
        house="ssdi",
    )
    persist_hits(
        "ssa.gov disability",
        [
            {"id": "ssa-disability", "kind": "policy", "url": "https://www.ssa.gov/disability/"},
            {"id": "ssa-benefits", "kind": "policy", "url": "https://www.ssa.gov/benefits/disability/"},
        ],
        path=path,
        house="ssdi",
    )
    stats = hit_summary(path=path, house="ssdi")
    assert stats["queries"] == 2
    assert stats["hits"] == 3
    assert stats["max_hits_in_query"] == 2
    assert stats["invented_market"] is False
    empty = hit_summary(path=tmp_path / "none.jsonl")
    assert empty["max_hits_in_query"] is None


def test_calibration_mae(tmp_path):
    path = tmp_path / "cal.jsonl"
    record(0.25, 0, house="pi", query="a", path=path)
    record(0.75, 1, house="pi", query="b", path=path)
    stats = summary(path=path, house="pi")
    assert stats["mean_abs_error"] == 0.25
    assert stats["invented_market"] is False
    out = invoke("calibration.mae", {"house": "pi"})
    assert out["invented_market"] is False
    assert "mean_abs_error" in out
    assert "cpl" not in str(out).lower()
    assert "roas" not in str(out).lower()
