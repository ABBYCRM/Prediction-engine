"""Tiny MCP-style gateway: allowlisted tools only; reject unknown names and extra keys."""

from __future__ import annotations

from typing import Any, Callable

from prediction_engine.analog_store import read_hits
from prediction_engine.contracts import list_contracts
from prediction_engine.houses import HouseError, bridge_0_to_1, bridge_10_to_0
from prediction_engine.domain.intake_rules import ccfl_hard_stop, ssdi_intake_ok
from prediction_engine.engine import PredictionEngine
from prediction_engine.oauth import OAuthError
from prediction_engine.playbook import list_facts, match_facts
from prediction_engine.ledger import read_ledger
from prediction_engine.publishers import list_publishers
from prediction_engine.mailer import Mailer
from prediction_engine.sheets import SheetsError, preview_values_append, write_row

ToolFn = Callable[[dict[str, Any]], dict[str, Any]]

ALLOWED_TOOLS: dict[str, set[str]] = {
    "playbook.list": set(),
    "playbook.match": {"query"},
    "intake.ccfl": {"payload"},
    "intake.ssdi": {"payload"},
    "engine.predict": {"query", "live_scrape", "house"},
    "analog.log": {"limit", "house"},
    "sheets.write": {"row"},
    "ledger.read": {"limit", "house"},
    "publishers.list": set(),
    "contracts.list": set(),
    "house.bridge": {"house", "mode", "payload"},
    "mailer.status": set(),
    "sheets.preview": {"row"},
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
    house = args.get("house")
    house_s = str(house).strip() if house else None
    hits = read_hits(limit=limit, house=house_s)
    return {"count": len(hits), "hits": hits, "house": house_s}


def _publishers_list(_args: dict[str, Any]) -> dict[str, Any]:
    return list_publishers()


def _contracts_list(_args: dict[str, Any]) -> dict[str, Any]:
    rows = list_contracts()
    return {"count": len(rows), "contracts": rows}


def _house_bridge(args: dict[str, Any]) -> dict[str, Any]:
    house = str(args.get("house") or "")
    mode = str(args.get("mode") or "10_to_0")
    payload = args.get("payload")
    if payload is not None and not isinstance(payload, dict):
        return {"error": "payload must be an object", "mixed": True}
    try:
        if mode == "0_to_1":
            return bridge_0_to_1(house)
        return bridge_10_to_0(house, payload if isinstance(payload, dict) else None)
    except HouseError as exc:
        return {"error": str(exc), "mixed": True}


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


def _mailer_status(_args: dict[str, Any]) -> dict[str, Any]:
    return Mailer().status()


def _sheets_preview(args: dict[str, Any]) -> dict[str, Any]:
    row = args.get("row")
    if row is not None and not isinstance(row, dict):
        return {"error": "row must be an object", "remote": False}
    try:
        return preview_values_append(row if isinstance(row, dict) else None)
    except SheetsError as exc:
        return {"error": str(exc), "remote": False}


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
    "publishers.list": _publishers_list,
    "contracts.list": _contracts_list,
    "house.bridge": _house_bridge,
    "mailer.status": _mailer_status,
    "sheets.preview": _sheets_preview,
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
