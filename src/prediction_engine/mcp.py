"""Tiny MCP-style gateway: allowlisted tools only; reject unknown names and extra keys."""

from __future__ import annotations

from typing import Any, Callable

from prediction_engine.analog_store import read_hits
from prediction_engine.domain.intake_rules import ccfl_hard_stop, ssdi_intake_ok
from prediction_engine.engine import PredictionEngine
from prediction_engine.oauth import OAuthError
from prediction_engine.playbook import list_facts, match_facts
from prediction_engine.ledger import read_ledger
from prediction_engine.sheets import SheetsError, write_row

ToolFn = Callable[[dict[str, Any]], dict[str, Any]]

ALLOWED_TOOLS: dict[str, set[str]] = {
    "playbook.list": set(),
    "playbook.match": {"query"},
    "intake.ccfl": {"payload"},
    "intake.ssdi": {"payload"},
    "engine.predict": {"query", "live_scrape", "house"},
    "analog.log": {"limit"},
    "sheets.write": {"row"},
    "ledger.read": {"limit", "house"},
}


def _playbook_list(_args: dict[str, Any]) -> dict[str, Any]:
    facts = list_facts()
    return {"count": len(facts), "facts": facts}


def _playbook_match(args: dict[str, Any]) -> dict[str, Any]:
    return {"matches": match_facts(str(args.get("query") or ""))}


def _intake_ccfl(args: dict[str, Any]) -> dict[str, Any]:
    payload = args.get("payload") or {}
    if not isinstance(payload, dict):
        return {"error": "payload must be an object"}
    return ccfl_hard_stop(payload)


def _intake_ssdi(args: dict[str, Any]) -> dict[str, Any]:
    payload = args.get("payload") or {}
    if not isinstance(payload, dict):
        return {"error": "payload must be an object"}
    return ssdi_intake_ok(payload)


def _engine_predict(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get("query") or "").strip()
    if not query:
        return {"error": "query_required"}
    live = bool(args.get("live_scrape"))
    house = args.get("house")
    house_s = str(house).strip() if house else None
    result = PredictionEngine().predict(query, live_scrape=live, house=house_s)
    return {
        "query": result.query,
        "answer": result.answer,
        "facts": result.facts,
        "used_xai": result.used_xai,
        "note": result.note,
        "analogs": result.analogs,
        "scrape": result.scrape,
        "live_scrape": live,
        "house": result.house,
    }


def _analog_log(args: dict[str, Any]) -> dict[str, Any]:
    raw = args.get("limit", 20)
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        limit = 20
    limit = max(1, min(limit, 50))
    hits = read_hits(limit=limit)
    return {"count": len(hits), "hits": hits}


def _ledger_read(args: dict[str, Any]) -> dict[str, Any]:
    raw = args.get("limit", 20)
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        limit = 20
    house = args.get("house")
    house_s = str(house).strip() if house else None
    rows = read_ledger(limit=limit, house=house_s)
    return {"count": len(rows), "rows": rows, "remote": False}


def _sheets_write(args: dict[str, Any]) -> dict[str, Any]:
    row = args.get("row") or {}
    if not isinstance(row, dict):
        return {"error": "row must be an object"}
    try:
        return write_row(row)
    except (SheetsError, OAuthError) as exc:
        return {"error": str(exc), "remote": False}


HANDLERS: dict[str, ToolFn] = {
    "playbook.list": _playbook_list,
    "playbook.match": _playbook_match,
    "intake.ccfl": _intake_ccfl,
    "intake.ssdi": _intake_ssdi,
    "engine.predict": _engine_predict,
    "analog.log": _analog_log,
    "sheets.write": _sheets_write,
    "ledger.read": _ledger_read,
}


def list_tools() -> list[str]:
    return sorted(ALLOWED_TOOLS)


class MCPError(ValueError):
    pass


def invoke(tool: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    if tool not in ALLOWED_TOOLS:
        raise MCPError(f"unknown tool: {tool}")
    args = dict(arguments or {})
    extra = set(args) - ALLOWED_TOOLS[tool]
    if extra:
        raise MCPError(f"extra keys rejected: {sorted(extra)}")
    return HANDLERS[tool](args)
