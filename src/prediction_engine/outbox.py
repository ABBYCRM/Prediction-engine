"""Resend-shaped outbox. Still refuses send without SMTP_HOST and SMTP_FROM."""

from __future__ import annotations

from prediction_engine.mailer import Mailer, MailerError


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
        sender = msg["from"] or self.mailer.settings.smtp_from
        try:
            result = self.mailer.send(msg["to"][0], msg["subject"], msg["text"])
        except MailerError as exc:
            raise OutboxError(str(exc)) from exc
        result["shape"] = "resend"
        result["from"] = sender
        result["to"] = msg["to"]
        return result
