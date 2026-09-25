"""Google Ads / Meta Marketing API connectors. Refuse without real OAuth tokens."""

from __future__ import annotations

import os
from dataclasses import dataclass


class OAuthError(RuntimeError):
    pass


@dataclass
class TokenBundle:
    provider: str
    present: bool
    scopes_note: str


def _env(*names: str) -> bool:
    return all(bool(os.environ.get(name, "").strip()) for name in names)


def google_ads_status() -> TokenBundle:
    present = _env("GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_OAUTH_REFRESH_TOKEN", "GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET")
    return TokenBundle(
        provider="google_ads",
        present=present,
        scopes_note="https://www.googleapis.com/auth/adwords",
    )


def meta_ads_status() -> TokenBundle:
    present = _env("META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN")
    return TokenBundle(
        provider="meta_ads",
        present=present,
        scopes_note="ads_read ads_management",
    )


def require_google_ads() -> TokenBundle:
    status = google_ads_status()
    if not status.present:
        raise OAuthError(
            "Google Ads connector refused: missing GOOGLE_ADS_DEVELOPER_TOKEN / "
            "GOOGLE_ADS_OAUTH_REFRESH_TOKEN / GOOGLE_ADS_CLIENT_ID / GOOGLE_ADS_CLIENT_SECRET"
        )
    return status


def require_meta_ads() -> TokenBundle:
    status = meta_ads_status()
    if not status.present:
        raise OAuthError(
            "Meta Ads connector refused: missing META_APP_ID / META_APP_SECRET / META_ACCESS_TOKEN"
        )
    return status
