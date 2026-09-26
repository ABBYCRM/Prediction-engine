"""Outbound mail. Dual-gate: SMTP_HOST+SMTP_FROM and SMTP_SEND_ENABLED."""

from __future__ import annotations

from email.message import EmailMessage

from prediction_engine.config import Settings, get_settings


class MailerError(RuntimeError):
    pass


class Mailer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def gate_a_config(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_from)

    def gate_b_enabled(self) -> bool:
        return bool(self.settings.smtp_send_enabled)

    def can_send(self) -> bool:
        return self.gate_a_config() and self.gate_b_enabled()

    def status(self) -> dict:
        return {
            "gate_a_config": self.gate_a_config(),
            "gate_b_enabled": self.gate_b_enabled(),
            "can_send": self.can_send(),
            "host_set": bool(self.settings.smtp_host),
            "from_set": bool(self.settings.smtp_from),
            "user_set": bool(self.settings.smtp_user),
            "resend_key_set": bool(self.settings.resend_api_key),
            "resend_bypasses_smtp": False,
            "live_smtp": False,
        }

    def send(self, to: str, subject: str, body: str) -> dict:
        if not self.gate_a_config():
            raise MailerError("refusing send: SMTP_HOST and SMTP_FROM are required")
        if not self.gate_b_enabled():
            raise MailerError(
                "refusing send: SMTP_SEND_ENABLED dual-gate is off "
                "(set SMTP_SEND_ENABLED=true after HOST+FROM)"
            )
        msg = EmailMessage()
        msg["From"] = self.settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        return {
            "queued": True,
            "sent": False,
            "live_smtp": False,
            "to": to,
            "from": self.settings.smtp_from,
            "host": self.settings.smtp_host,
            "gates": {"a": True, "b": True},
        }

    def preview_envelope(self, to: str, subject: str, body: str) -> dict:
        """Build headers only. Never opens a socket. Never returns secrets."""
        return {
            "ok": True,
            "live_smtp": False,
            "sent": False,
            "to": to,
            "from": self.settings.smtp_from or None,
            "subject": subject,
            "body_chars": len(body or ""),
            "host_set": bool(self.settings.smtp_host),
            "gates": {
                "a": self.gate_a_config(),
                "b": self.gate_b_enabled(),
            },
            "can_send": self.can_send(),
        }
