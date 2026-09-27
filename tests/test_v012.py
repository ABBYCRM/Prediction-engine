from __future__ import annotations

from prediction_engine import __version__
from prediction_engine.analog import retrieve
from prediction_engine.contracts import list_contracts
from prediction_engine.houses import bridge_0_to_1, bridge_10_to_0
from prediction_engine.mcp import invoke


def test_version_is_016():
    assert __version__ == "0.20.0"
