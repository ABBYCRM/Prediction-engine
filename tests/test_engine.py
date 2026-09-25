from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prediction_engine.analog_store import persist_hits, read_hits
from prediction_engine.cadence import ALLOWED_HOURS, on_cadence
from prediction_engine.config import Settings, SettingsError
from prediction_engine.domain.intake_rules import ccfl_hard_stop, ssdi_intake_ok
from prediction_engine.engine import PredictionEngine
from prediction_engine.mailer import Mailer, MailerError
from prediction_engine.mcp import MCPError, invoke, list_tools
from prediction_engine.outbox import OutboxError, ResendOutbox
from prediction_engine.playbook import list_facts
from prediction_engine.oauth import (
    OAuthError,
    require_google_ads,
    require_google_sheets,
    require_meta_ads,
)
from prediction_engine.sheets import SheetsError, write_row
from prediction_engine.publishers import is_allowlisted_publisher_url
from prediction_engine.research import ResearchError, assert_runs_not_mixed, write_run
from prediction_engine.scraper import SSRFError, assert_public_http_url, scrape_public
from prediction_engine.writeback import WritebackError, validate_row


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


def test_publisher_allowlist_rejects_offlist():
    assert is_allowlisted_publisher_url(
        "https://support.google.com/adspolicy/answer/6008942"
    )
    assert is_allowlisted_publisher_url(
        "https://transparency.meta.com/policies/ad-standards/"
    )
    assert not is_allowlisted_publisher_url("https://example.com/ads")


def test_scrape_public_rejects_offlist_after_ssrf():
    with pytest.raises(SSRFError):
        scrape_public("https://example.com/not-a-publisher")


def test_resend_key_does_not_bypass_smtp():
    settings = Settings(
        smtp_host="",
        smtp_from="",
        resend_api_key="re_test_not_a_real_key",
    )
    box = ResendOutbox(Mailer(settings))
    with pytest.raises(OutboxError):
        box.send({"to": "a@b.c", "subject": "x", "text": "y"})


def test_analog_hits_persist(tmp_path):
    path = tmp_path / "hits.jsonl"
    persist_hits(
        "google ads policy",
        [{"id": "gads-areas", "kind": "playbook_fact", "analog_score": 2}],
        path=path,
    )
    rows = read_hits(path)
    assert len(rows) == 1
    assert rows[0]["hits"][0]["id"] == "gads-areas"
    assert "%" not in json.dumps(rows[0])


def test_predict_records_allowlisted_scrape_without_fetch():
    result = PredictionEngine().predict("google limited ad serving")
    assert result.analogs
    assert result.scrape is not None
    assert result.scrape["fetched"] is False
    assert "support.google.com" in result.scrape.get("host", "")


def test_research_write_run_rejects_metrics(tmp_path):
    with pytest.raises(ResearchError):
        write_run(
            "pi",
            "keyword",
            [{"kind": "prediction", "claim": "CPC is 12%"}],
            path=tmp_path / "bad.json",
        )


def test_research_write_run_persists(tmp_path):
    path = write_run(
        "ssdi",
        "policy",
        [
            {
                "kind": "fact",
                "claim": "SSA publishes an official disability overview.",
                "url": "https://www.ssa.gov/disability",
                "as_of": "2026-09-25",
            }
        ],
        note="unit",
        path=tmp_path / "ssdi_policy_unit.json",
    )
    assert path.is_file()
    body = json.loads(path.read_text())
    assert body["house"] == "ssdi"
    assert body["mixed_house"] is False


def test_oauth_connectors_refuse_without_tokens(monkeypatch):
    for key in (
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_OAUTH_REFRESH_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "META_APP_ID",
        "META_APP_SECRET",
        "META_ACCESS_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(OAuthError):
        require_google_ads()
    with pytest.raises(OAuthError):
        require_meta_ads()
    with pytest.raises(OAuthError):
        require_google_sheets()


def test_sheets_target_refuses_without_oauth(tmp_path, monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEETS_SPREADSHEET_ID", raising=False)
    for key in (
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_OAUTH_REFRESH_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
    ):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises((SheetsError, OAuthError)):
        write_row(
            {
                "house": "pi",
                "kind": "prediction",
                "target": "sheets",
                "query": "policy",
                "claim": "Prediction: test geo modifiers first.",
            },
            path=tmp_path / "ledger.jsonl",
        )


def test_local_jsonl_writeback(tmp_path):
    dest = tmp_path / "ledger.jsonl"
    out = write_row(
        {
            "house": "ssdi",
            "kind": "prediction",
            "target": "local_jsonl",
            "query": "policy",
            "claim": "Prediction: cite SSA pages only.",
        },
        path=dest,
    )
    assert out["ok"] is True
    assert out["remote"] is False
    assert dest.is_file()


def test_mcp_sheets_write_and_extra_keys():
    assert "sheets.write" in list_tools()
    out = invoke(
        "sheets.write",
        {
            "row": {
                "house": "pi",
                "kind": "prediction",
                "target": "sheets",
                "query": "policy",
                "claim": "Prediction: stay on sourced policy pages.",
            }
        },
    )
    assert "error" in out
    with pytest.raises(MCPError):
        invoke("sheets.write", {"row": {}, "extra": 1})


def test_writeback_row_requires_fact_source():
    with pytest.raises(WritebackError):
        validate_row(
            {
                "house": "pi",
                "kind": "fact",
                "target": "local_jsonl",
                "query": "policy",
                "claim": "unsourced",
            }
        )
    row = validate_row(
        {
            "house": "pi",
            "kind": "prediction",
            "target": "local_jsonl",
            "query": "policy",
            "claim": "Prediction: test geo modifiers first.",
        }
    )
    assert row["house"] == "pi"


def test_live_runs_on_disk_are_house_isolated():
    assert_runs_not_mixed()
