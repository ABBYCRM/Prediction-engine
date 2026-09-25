"""Allowlist publisher hosts drawn from playbook URLs. No scrape off-list."""

from __future__ import annotations

from urllib.parse import urlparse

from prediction_engine.playbook import list_facts

# Hard floor so a truncated playbook cannot widen the net.
FLOOR_HOSTS = frozenset(
    {
        "support.google.com",
        "transparency.meta.com",
    }
)


def publisher_hosts() -> frozenset[str]:
    hosts = set(FLOOR_HOSTS)
    for fact in list_facts():
        host = (urlparse(str(fact.get("url") or "")).hostname or "").lower()
        if host:
            hosts.add(host)
    return frozenset(hosts)


def is_allowlisted_publisher_url(url: str) -> bool:
    parsed = urlparse(url or "")
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    return host in publisher_hosts()


def list_publishers() -> dict:
    hosts = sorted(publisher_hosts())
    return {
        "count": len(hosts),
        "hosts": hosts,
        "floor_hosts": sorted(FLOOR_HOSTS),
        "live_fetch": False,
    }
