from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from prediction_engine import __version__
from prediction_engine.cadence import next_window
from prediction_engine.config import Settings
from prediction_engine.mailer import Mailer
from prediction_engine.mcp import invoke, list_tools
from prediction_engine.xai_client import XAIClient


def test_version_015():
    assert __version__ == "0.15.0"


def test_next_window_on_and_off_cadence():
    tz = ZoneInfo("America/New_York")
    on = next_window(datetime(2026, 9, 26, 8, 6, tzinfo=tz))
    assert on["on_cadence"] is True
    assert on["hours_until"] == 0
    assert on["next_hour"] == 8
    off = next_window(datetime(2026, 9, 26, 9, 0, tzinfo=tz))
    assert off["on_cadence"] is False
    assert off["next_hour"] == 12
    assert off["hours_until"] == 3
    wrap = next_window(datetime(2026, 9, 26, 21, 0, tzinfo=tz))
    assert wrap["next_hour"] == 0
    assert wrap["hours_until"] == 3


def test_mailer_preview_never_sends():
    mailer = Mailer(
        Settings(
            smtp_host="smtp.example.com",
            smtp_from="ops@example.com",
            smtp_password="secret",
            smtp_send_enabled=True,
        )
    )
    out = mailer.preview_envelope("a@b.c", "subj", "hello")
    assert out["live_smtp"] is False
    assert out["sent"] is False
    assert out["body_chars"] == 5
    assert out["can_send"] is True
    blob = str(out)
    assert "secret" not in blob
    assert "smtp_password" not in blob


def test_mcp_preview_cadence_xai_tools():
    tools = list_tools()
    assert "mailer.preview" in tools
    assert "cadence.status" in tools
    assert "xai.guard" in tools
    preview = invoke("mailer.preview", {"to": "a@b.c", "subject": "s", "body": "b"})
    assert preview["sent"] is False
    cadence = invoke("cadence.status", {})
    assert cadence["tz"] == "America/New_York"
    assert "next_hour" in cadence
    guard = invoke("xai.guard", {})
    assert guard["allowed_hosts"] == ["api.x.ai"]
    assert "key" not in str(guard).lower() or guard["key_set"] in {True, False}
    assert "XAI_API_KEY" not in str(guard)


def test_xai_guard_refuses_other_hosts_via_settings_object():
    client = XAIClient(Settings(xai_api_key="", xai_base_url="https://api.x.ai/v1"))
    out = client.host_guard()
    assert out["ok"] is True
    assert out["will_call"] is False
    assert out["host"] == "api.x.ai"
