from __future__ import annotations

import pytest

from prediction_engine import __version__
from prediction_engine.analog_store import hit_summary, persist_hits
from prediction_engine.calibration import expected_calibration_error, record, reliability_buckets, summary
from prediction_engine.mcp import invoke


def test_version_is_018():
    assert __version__ == "0.22.0"


def test_ece_from_caller_scores_only(tmp_path):
    path = tmp_path / "c.jsonl"
    record(0.1, 0, house="pi", path=path)
    record(0.9, 1, house="pi", path=path)
    stats = summary(path=path, house="pi")
    assert stats["count"] == 2
    assert stats["ece"] is not None
    assert stats["ece"] == pytest.approx(0.1)
    assert stats["invented_market"] is False
    assert "cpl" not in str(stats).lower()
    assert "roas" not in str(stats).lower()
    empty = expected_calibration_error(reliability_buckets([]))
    assert empty is None


def test_analog_unique_ids(tmp_path):
    path = tmp_path / "a.jsonl"
    persist_hits(
        "ssa.gov policy",
        [{"id": "ssa-home", "kind": "policy", "analog_score": 1.0, "url": "https://www.ssa.gov/"}],
        path=path,
        house="ssdi",
    )
    persist_hits(
        "ssa.gov policy again",
        [{"id": "ssa-home", "kind": "policy", "analog_score": 1.0, "url": "https://www.ssa.gov/"}],
        path=path,
        house="ssdi",
    )
    stats = hit_summary(path=path, house="ssdi")
    assert stats["queries"] == 2
    assert stats["hits"] == 2
    assert stats["unique_ids"] == 1
    assert stats["invented_market"] is False


def test_mcp_calibration_reliability():
    out = invoke("calibration.reliability", {"house": "pi"})
    assert out["invented_market"] is False
    assert "buckets" in out
    assert "ece" in out
