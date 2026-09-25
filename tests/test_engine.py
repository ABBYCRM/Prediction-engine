from __future__ import annotations

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from prediction_engine.cadence import ALLOWED_HOURS, on_cadence
from prediction_engine.config import Settings, SettingsError
from prediction_engine.domain.intake_rules import ccfl_hard_stop, ssdi_intake_ok
from prediction_engine.engine import PredictionEngine
from prediction_engine.mailer import Mailer, MailerError
from prediction_engine.mcp import MCPError, invoke, list_tools
from prediction_engine.playbook import list_facts
from prediction_engine.scraper import SSRFError, assert_public_http_url


def test_ccfl_rejects_already_represented():
    out = ccfl_hard_stop({"already_represented": True, "state": "FL"})
    assert out["gate"] == "REJECT"
    assert out["reason"] == "already_represented"


def test_ssdi_requires_name_phone_tcpa():
    out = ssdi_intake_ok({"name": "A", "phone": "555", "tcpa": False})
    assert out["ok"] is False
    assert out["status"] == 422


def test_scraper_blocks_loopback():
    with pytest.raises(SSRFError):
        assert_public_http_url("http://127.0.0.1/secret")
    with pytest.raises(SSRFError):
        assert_public_http_url("file:///etc/passwd")


def test_mailer_refuses_without_smtp():
    mailer = Mailer(Settings(smtp_host="", smtp_from=""))
    assert mailer.can_send() is False
    with pytest.raises(MailerError):
        mailer.send("a@b.c", "hi", "body")


def test_mcp_rejects_unknown_tool():
    with pytest.raises(MCPError):
        invoke("not.a.tool", {})


def test_mcp_rejects_extra_keys():
    with pytest.raises(MCPError):
        invoke("playbook.list", {"unexpected": True})


def test_playbook_has_eleven_sourced_facts():
    facts = list_facts()
    assert len(facts) == 11
    for fact in facts:
        assert fact["url"].startswith("https://")
        assert "ctr" not in fact["claim"].lower()
        assert "%" not in fact["claim"]


def test_engine_returns_sourced_facts_without_xai():
    result = PredictionEngine().predict("google limited ad serving")
    assert result.used_xai is False
    assert result.facts
    assert "invent" not in result.answer.lower() or "No performance" in result.answer


def test_xai_base_url_must_be_api_x_ai():
    with pytest.raises(SettingsError):
        Settings(xai_base_url="https://api.openai.com/v1")
    ok = Settings(xai_base_url="https://api.x.ai/v1")
    assert ok.xai_base_url.endswith("/v1")


def test_cadence_hours_are_fixed():
    ny = ZoneInfo("America/New_York")
    on = datetime(2026, 9, 24, 20, 0, tzinfo=ny)
    off = datetime(2026, 9, 24, 21, 0, tzinfo=ny)
    assert on_cadence(on) is True
    assert on_cadence(off) is False
    assert ALLOWED_HOURS == frozenset({0, 4, 8, 12, 16, 20})


def test_engine_empty_query_does_not_invent():
    result = PredictionEngine().predict("   ")
    assert result.used_xai is False
    assert result.facts == []
    assert result.note == "query_required"


def test_mcp_engine_predict_and_tool_list():
    assert "engine.predict" in list_tools()
    out = invoke("engine.predict", {"query": "meta ad standards"})
    assert out["used_xai"] is False
    assert out["facts"]
    with pytest.raises(MCPError):
        invoke("engine.predict", {"query": "x", "extra": 1})
