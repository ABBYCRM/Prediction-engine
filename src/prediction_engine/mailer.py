"""Outbound mail. Refuses to send unless SMTP_HOST and SMTP_FROM are set."""

from __future__ import annotations

from email.message import EmailMessage

from prediction_engine.config import Settings, get_settings


class MailerError(RuntimeError):
    pass


class Mailer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def can_send(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_from)

    def send(self, to: str, subject: str, body: str) -> dict:
        if not self.can_send():
            raise MailerError("refusing send: SMTP_HOST and SMTP_FROM are required")
        msg = EmailMessage()
        msg["From"] = self.settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        return {
            "queued": True,
            "to": to,
            "from": self.settings.smtp_from,
            "host": self.settings.smtp_host,
        }
