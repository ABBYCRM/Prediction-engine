"""Resend-shaped outbox. Still refuses send without SMTP_HOST and SMTP_FROM."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from prediction_engine.mailer import Mailer, MailerError

ROOT = Path(__file__).resolve().parents[2]
DRAFTS_PATH = ROOT / "data" / "outbox_drafts.jsonl"


class OutboxError(MailerError):
    pass


def normalize(payload: dict) -> dict:
    to = payload.get("to")
    if isinstance(to, str):
        to_list = [to]
    elif isinstance(to, list):
        to_list = [str(x) for x in to]
    else:
        to_list = []
    html = payload.get("html")
    text = payload.get("text") or payload.get("body") or ""
    if html and not text:
        text = str(html)
    return {
        "from": str(payload.get("from") or ""),
        "to": to_list,
        "subject": str(payload.get("subject") or ""),
        "html": html,
        "text": str(text),
    }


class ResendOutbox:
    def __init__(self, mailer: Mailer | None = None) -> None:
        self.mailer = mailer or Mailer()

    def send(self, payload: dict) -> dict:
        msg = normalize(payload)
        if not msg["to"] or not msg["subject"]:
            raise OutboxError("to and subject are required")
        settings = self.mailer.settings
        if settings.resend_api_key and not (settings.smtp_host and settings.smtp_from):
            raise OutboxError(
                "RESEND_API_KEY does not bypass SMTP_HOST+SMTP_FROM gate"
            )
        sender = msg["from"] or self.mailer.settings.smtp_from
        try:
            result = self.mailer.send(msg["to"][0], msg["subject"], msg["text"])
        except MailerError as exc:
            raise OutboxError(str(exc)) from exc
        result["shape"] = "resend"
        result["from"] = sender
        result["to"] = msg["to"]
        return result

    def queue_draft(self, payload: dict, path: Path | None = None) -> dict:
        """Persist a Resend-shaped draft. Does not send."""
        msg = normalize(payload)
        if not msg["to"] or not msg["subject"]:
            raise OutboxError("to and subject are required")
        target = path or DRAFTS_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "shape": "resend",
            "queued": True,
            "sent": False,
            "from": msg["from"],
            "to": msg["to"],
            "subject": msg["subject"],
        }
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")
        return record
