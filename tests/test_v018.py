from __future__ import annotations

import pytest

from prediction_engine import __version__
from prediction_engine.analog_store import hit_summary, persist_hits
from prediction_engine.calibration import expected_calibration_error, record, reliability_buckets, summary
from prediction_engine.mcp import invoke


def test_version_is_018():
    assert __version__ == "0.20.0"
