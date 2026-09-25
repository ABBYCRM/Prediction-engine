"""America/New_York cadence gate used by the 4-hour work windows."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

ALLOWED_HOURS = frozenset({0, 4, 8, 12, 16, 20})
TZ = ZoneInfo("America/New_York")


def current_hour(now: datetime | None = None) -> int:
    stamp = now.astimezone(TZ) if now is not None else datetime.now(TZ)
    return stamp.hour


def on_cadence(now: datetime | None = None) -> bool:
    return current_hour(now) in ALLOWED_HOURS


def cadence_status(now: datetime | None = None) -> dict:
    hour = current_hour(now)
    return {
        "tz": "America/New_York",
        "hour": hour,
        "allowed_hours": sorted(ALLOWED_HOURS),
        "on_cadence": hour in ALLOWED_HOURS,
    }
