"""HTTP fetch with SSRF guards: no private, loopback, link-local, or file URLs."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from prediction_engine.browser import snapshot_html
from prediction_engine.publishers import is_allowlisted_publisher_url

BLOCKED_SCHEMES = frozenset({"file", "ftp", "gopher", "data", "javascript"})


class SSRFError(ValueError):
    pass


def _is_blocked_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def assert_public_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SSRFError(f"blocked scheme: {parsed.scheme or 'missing'}")
    host = parsed.hostname
    if not host:
        raise SSRFError("missing host")
    lowered = host.lower()
    if lowered in {"localhost", "metadata.google.internal"} or lowered.endswith(".local"):
        raise SSRFError(f"blocked host: {host}")
    try:
        infos = socket.getaddrinfo(host, parsed.port or 80, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SSRFError(f"unresolvable host: {host}") from exc
    for info in infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            raise SSRFError(f"blocked address {ip} for host {host}")


def fetch_text(url: str, timeout: float = 10.0) -> str:
    assert_public_http_url(url)
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text


def scrape_public(url: str, timeout: float = 10.0) -> dict:
    """SSRF first; publisher allowlist second; snapshot text only. No metrics."""
    assert_public_http_url(url)
    if not is_allowlisted_publisher_url(url):
        raise SSRFError(f"publisher not allowlisted: {url}")
    html = fetch_text(url, timeout=timeout)
    return {"url": url, "text": snapshot_html(html), "fetched": True}
