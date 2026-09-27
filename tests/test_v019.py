from __future__ import annotations

import math

import pytest

from prediction_engine import __version__
from prediction_engine.analog_store import hit_summary, persist_hits
from prediction_engine.calibration import log_loss, record, summary
from prediction_engine.mcp import invoke


def test_version_is_019():
    assert __version__ == "0.23.0"


def test_log_loss_from_caller_scores_only(tmp_path):
    path = tmp_path / "c.jsonl"
    record(0.1, 0, house="pi", path=path)
    record(0.9, 1, house="pi", path=path)
    stats = summary(path=path, house="pi")
    assert stats["count"] == 2
    expected = -math.log(0.9)
    assert stats["mean_log_loss"] == pytest.approx(expected)
    assert log_loss(0.9, 1) == pytest.approx(expected)
    assert stats["invented_market"] is False
    assert "cpl" not in str(stats).lower()
    assert "roas" not in str(stats).lower()
    empty = summary(path=tmp_path / "missing.jsonl")
    assert empty["mean_log_loss"] is None


def test_analog_last_ts(tmp_path):
    path = tmp_path / "a.jsonl"
    persist_hits(
        "ssa.gov policy",
        [{"id": "ssa-home", "kind": "policy", "analog_score": 1.0, "url": "https://www.ssa.gov/"}],
        path=path,
        house="ssdi",
    )
    stats = hit_summary(path=path, house="ssdi")
    assert stats["queries"] == 1
    assert stats["last_ts"]
    assert stats["invented_market"] is False
    empty = hit_summary(path=tmp_path / "none.jsonl")
    assert empty["last_ts"] is None
    assert empty["unique_ids"] == 0


def test_mcp_calibration_log_loss():
    out = invoke("calibration.log_loss", {"house": "pi"})
    assert out["invented_market"] is False
    assert "mean_log_loss" in out
    assert "count" in out
