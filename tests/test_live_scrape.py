from prediction_engine.engine import PredictionEngine
from prediction_engine.mcp import MCPError, invoke, list_tools
import pytest


def test_live_scrape_flag_uses_injected_fn():
    seen = {}

    def fake_scrape(url: str):
        seen["url"] = url
        return {"url": url, "fetched": True, "text": "policy page snapshot", "host": "support.google.com"}

    result = PredictionEngine(scrape_fn=fake_scrape).predict(
        "google limited ad serving", live_scrape=True
    )
    assert result.scrape is not None
    assert result.scrape["fetched"] is True
    assert "support.google.com" in seen["url"]


def test_default_predict_still_skips_fetch():
    def boom(url: str):
        raise AssertionError("default predict must not live-fetch")

    result = PredictionEngine(scrape_fn=boom).predict("google limited ad serving")
    assert result.scrape is not None
    assert result.scrape["fetched"] is False


def test_mcp_analog_log_and_extra_keys():
    assert "analog.log" in list_tools()
    out = invoke("analog.log", {})
    assert "hits" in out
    with pytest.raises(MCPError):
        invoke("analog.log", {"limit": 5, "extra": 1})
