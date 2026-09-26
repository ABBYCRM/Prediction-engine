from __future__ import annotations

import pytest

from prediction_engine.config import Settings
from prediction_engine.mailer import Mailer, MailerError
from prediction_engine.mcp import invoke
from prediction_engine.outbox import ResendOutbox
from prediction_engine.sheets import live_client_contract, preview_values_append


def test_dual_gate_requires_enable_flag():
    configured = Settings(
        smtp_host="smtp.example.com",
        smtp_from="ops@example.com",
        smtp_send_enabled=False,
    )
    mailer = Mailer(configured)
    assert mailer.gate_a_config() is True
    assert mailer.gate_b_enabled() is False
    assert mailer.can_send() is False
    with pytest.raises(MailerError) as exc:
        mailer.send("a@b.c", "hi", "body")
    assert "SMTP_SEND_ENABLED" in str(exc.value)


def test_dual_gate_open_still_does_not_live_smtp():
    mailer = Mailer(
        Settings(
            smtp_host="smtp.example.com",
            smtp_from="ops@example.com",
            smtp_send_enabled=True,
        )
    )
    assert mailer.can_send() is True
    out = mailer.send("a@b.c", "hi", "body")
    assert out["queued"] is True
    assert out["sent"] is False
    assert out["live_smtp"] is False
    assert out["gates"] == {"a": True, "b": True}


def test_resend_key_plus_host_still_needs_enable():
    settings = Settings(
        smtp_host="smtp.example.com",
        smtp_from="ops@example.com",
        resend_api_key="re_test",
        smtp_send_enabled=False,
    )
    box = ResendOutbox(Mailer(settings))
    with pytest.raises(Exception):
        box.send({"to": "a@b.c", "subject": "x", "text": "y"})


def test_mailer_status_mcp_hides_secrets():
    status = invoke("mailer.status", {})
    assert status["resend_bypasses_smtp"] is False
    assert status["live_smtp"] is False
    assert "smtp_password" not in status
    assert "resend_api_key" not in status


def test_sheets_preview_is_field_names_only():
    contract = live_client_contract()
    assert "spreadsheetId" in contract["path_fields"]
    assert "valueInputOption" in contract["query_fields"]
    assert contract["live"] is False
    preview = preview_values_append()
    assert preview["remote"] is False
    assert preview["wired"] is False
    out = invoke("sheets.preview", {})
    assert out["contract"]["url"].startswith("https://developers.google.com/sheets/")
    blob = str(out)
    assert "cpl" not in blob.lower()
    assert "roas" not in blob.lower()
