"""Settings. xAI only at api.x.ai unless XAI_BASE_URL is an api.x.ai origin."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

ALLOWED_XAI_HOSTS = frozenset({"api.x.ai"})


class SettingsError(ValueError):
    pass


def _validate_base_url(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host not in ALLOWED_XAI_HOSTS:
        raise SettingsError("XAI_BASE_URL must use host api.x.ai")
    return url.rstrip("/")


@dataclass
class Settings:
    xai_api_key: str = ""
    xai_base_url: str = "https://api.x.ai/v1"
    xai_model: str = "grok-4"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    resend_api_key: str = ""
    host: str = "127.0.0.1"
    port: int = 8080

    def __post_init__(self) -> None:
        self.xai_base_url = _validate_base_url(self.xai_base_url)


def get_settings() -> Settings:
    return Settings(
        xai_api_key=os.environ.get("XAI_API_KEY", ""),
        xai_base_url=os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1"),
        xai_model=os.environ.get("XAI_MODEL", "grok-4"),
        smtp_host=os.environ.get("SMTP_HOST", ""),
        smtp_port=int(os.environ.get("SMTP_PORT", "587")),
        smtp_user=os.environ.get("SMTP_USER", ""),
        smtp_password=os.environ.get("SMTP_PASSWORD", ""),
        smtp_from=os.environ.get("SMTP_FROM", ""),
        resend_api_key=os.environ.get("RESEND_API_KEY", ""),
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8080")),
    )
