"""Google Sheets write gate. Never writes remotely without OAuth + spreadsheet id."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prediction_engine.oauth import OAuthError, google_ads_status
from prediction_engine.writeback import WritebackError, validate_row

ROOT = Path(__file__).resolve().parents[2]
LOCAL_LEDGER = ROOT / "data" / "writeback_ledger.jsonl"


class SheetsError(RuntimeError):
    pass


def google_sheets_ready() -> bool:
    """Sheets needs the Ads OAuth quartet plus an explicit spreadsheet id."""
    ads = google_ads_status()
    sheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip()
    return ads.present and bool(sheet_id)


def require_google_sheets() -> dict[str, Any]:
    if not google_sheets_ready():
        raise OAuthError(
            "Sheets write refused: missing Google OAuth tokens and/or "
            "GOOGLE_SHEETS_SPREADSHEET_ID"
        )
    return {
        "provider": "google_sheets",
        "present": True,
        "spreadsheet_id_set": True,
    }


def append_local(row: dict[str, Any], path: Path | None = None) -> Path:
    validated = validate_row(row)
    if validated["target"] == "sheets":
        raise SheetsError("target=sheets cannot land in the local ledger")
    dest = path or LOCAL_LEDGER
    dest.parent.mkdir(parents=True, exist_ok=True)
    record = {
        **validated,
        "written_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "remote": False,
    }
    with dest.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    return dest


def write_row(row: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    """Route a validated row. Sheets target requires OAuth; otherwise local_jsonl."""
    try:
        validated = validate_row(row)
    except WritebackError as exc:
        raise SheetsError(str(exc)) from exc
    target = validated["target"]
    if target == "sheets":
        require_google_sheets()
        # Tokens present: still no live Google API client in this slice.
        # Refuse network write until a dedicated client is added after Luis signs off.
        raise SheetsError(
            "OAuth present but live Sheets client is not wired; no remote write"
        )
    if target == "hubspot_readonly_note":
        raise SheetsError("hubspot target is read-only; no write")
    dest = append_local(validated, path=path)
    return {"ok": True, "target": "local_jsonl", "path": str(dest), "remote": False}
