from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prediction_engine import __version__
from prediction_engine.cadence import cadence_status, window_remaining_minutes
from prediction_engine.calibration import CalibrationError, brier, record, summary
from prediction_engine.houses import HouseError
from prediction_engine.ledger import append_local, read_ledger
from prediction_engine.mcp import invoke
from prediction_engine.writeback import WritebackError


def test_version_is_016():
    assert __version__ == "0.16.0"


def test_brier_known_values():
    assert brier(0.0, 0) == 0.0
    assert brier(1.0, 1) == 0.0
    assert brier(0.5, 1) == 0.25


def test_calibration_rejects_out_of_range(tmp_path):
    with pytest.raises(CalibrationError):
        record(1.5, 1, house="pi", path=tmp_path / "c.jsonl")
    with pytest.raises(CalibrationError):
        record(0.2, 2, house="pi", path=tmp_path / "c.jsonl")


def test_calibration_rejects_unknown_house(tmp_path):
    with pytest.raises(HouseError):
        record(0.2, 1, house="mixed", path=tmp_path / "c.jsonl")


def test_calibration_records_caller_only(tmp_path):
    path = tmp_path / "c.jsonl"
    row = record(0.4, 0, house="ssdi", query="policy page", path=path)
    assert row["invented_market"] is False
    assert row["source"] == "caller"
    assert row["brier"] == pytest.approx(0.16)
    stats = summary(path=path, house="ssdi")
    assert stats["count"] == 1
    assert stats["mean_brier"] == pytest.approx(0.16)
    assert "cpl" not in str(stats).lower()
    assert "roas" not in str(stats).lower()


def test_mcp_calibration_and_ledger_append(tmp_path, monkeypatch):
    out = invoke("calibration.record", {"p": 0.2, "y": 0, "house": "pi", "query": "q"})
    assert out.get("error") is None
    assert out["house"] == "pi"
    stats = invoke("calibration.summary", {"house": "pi"})
    assert stats["invented_market"] is False
    assert stats["count"] >= 1

    rec = invoke(
        "ledger.append",
        {
            "row": {
                "house": "pi",
                "kind": "observation",
                "target": "local_jsonl",
                "query": "q",
                "claim": "caller-supplied observation only",
            }
        },
    )
    assert rec["remote"] is False
    assert rec["house"] == "pi"


def test_append_local_requires_schema(tmp_path):
    with pytest.raises(WritebackError):
        append_local({"house": "pi", "kind": "nope", "target": "local_jsonl"}, path=tmp_path / "l.jsonl")
    row = append_local(
        {
            "house": "ssdi",
            "kind": "fact",
            "target": "local_jsonl",
            "url": "https://www.ssa.gov/",
            "as_of": "2026-09-26",
            "claim": "SSA public site exists",
        },
        path=tmp_path / "l.jsonl",
    )
    rows = read_ledger(path=tmp_path / "l.jsonl")
    assert rows[-1]["url"] == "https://www.ssa.gov/"
    assert row["remote"] is False


def test_window_remaining_on_and_off_cadence():
    tz = ZoneInfo("America/New_York")
    on = datetime(2026, 9, 26, 12, 2, tzinfo=tz)
    off = datetime(2026, 9, 26, 13, 10, tzinfo=tz)
    assert window_remaining_minutes(on) == 58
    assert window_remaining_minutes(off) == 0
    status = cadence_status(on)
    assert status["on_cadence"] is True
    assert status["slice_budget_minutes"] == 30
    assert status["window_remaining_minutes"] == 58
