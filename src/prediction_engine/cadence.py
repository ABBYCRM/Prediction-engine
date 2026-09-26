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


def next_window(now: datetime | None = None) -> dict:
    """Next allowed ET hour and hours until that window opens."""
    stamp = now.astimezone(TZ) if now is not None else datetime.now(TZ)
    hour = stamp.hour
    hours = sorted(ALLOWED_HOURS)
    if hour in ALLOWED_HOURS:
        return {
            "current_hour": hour,
            "on_cadence": True,
            "next_hour": hour,
            "hours_until": 0,
        }
    for candidate in hours:
        if candidate > hour:
            return {
                "current_hour": hour,
                "on_cadence": False,
                "next_hour": candidate,
                "hours_until": candidate - hour,
            }
    return {
        "current_hour": hour,
        "on_cadence": False,
        "next_hour": hours[0],
        "hours_until": (24 - hour) + hours[0],
    }


def cadence_status(now: datetime | None = None) -> dict:
    hour = current_hour(now)
    nxt = next_window(now)
    return {
        "tz": "America/New_York",
        "hour": hour,
        "allowed_hours": sorted(ALLOWED_HOURS),
        "on_cadence": hour in ALLOWED_HOURS,
        "next_hour": nxt["next_hour"],
        "hours_until": nxt["hours_until"],
    }
