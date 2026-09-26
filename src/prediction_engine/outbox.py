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


def _as_list(value) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


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
    tags = payload.get("tags") or []
    if isinstance(tags, dict):
        tags = [{"name": str(k), "value": str(v)} for k, v in tags.items()]
    elif isinstance(tags, list):
        tags = list(tags)
    else:
        tags = []
    return {
        "from": str(payload.get("from") or ""),
        "to": to_list,
        "cc": _as_list(payload.get("cc")),
        "bcc": _as_list(payload.get("bcc")),
        "reply_to": _as_list(payload.get("reply_to") or payload.get("replyTo")),
        "subject": str(payload.get("subject") or ""),
        "html": html,
        "text": str(text),
        "tags": tags,
        "scheduled_at": payload.get("scheduled_at"),
        "headers": payload.get("headers") if isinstance(payload.get("headers"), dict) else {},
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
        result["cc"] = msg["cc"]
        result["bcc"] = msg["bcc"]
        result["reply_to"] = msg["reply_to"]
        result["tags"] = msg["tags"]
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
            "cc": msg["cc"],
            "bcc": msg["bcc"],
            "reply_to": msg["reply_to"],
            "subject": msg["subject"],
            "tags": msg["tags"],
            "scheduled_at": msg.get("scheduled_at"),
            "headers": msg.get("headers") or {},
        }
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")
        return record

    def list_drafts(self, path: Path | None = None, limit: int = 50) -> list[dict]:
        target = path or DRAFTS_PATH
        if not target.is_file():
            return []
        rows = []
        for line in target.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return rows[-max(1, min(limit, 200)) :]
