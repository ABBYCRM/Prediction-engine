"""Domain hard-stops borrowed from public ABBYCRM product contracts."""

from __future__ import annotations

CCFL_STATES = ("FL", "CA", "AZ", "TX", "NY")


def ccfl_hard_stop(payload: dict) -> dict:
    represented = payload.get("already_represented")
    fault = str(payload.get("primary_fault") or "").upper()
    state = str(payload.get("state") or "").upper()
    if represented is True:
        return {"gate": "REJECT", "reason": "already_represented", "source": "CaseClosedFL-Validator README"}
    if fault in {"SELF", "PRIMARY", "CLAIMANT"}:
        return {"gate": "REJECT", "reason": "primary_fault_claimant", "source": "CaseClosedFL-Validator README"}
    if state and state not in CCFL_STATES:
        return {"gate": "DEFER", "reason": "state_outside_published_scope", "source": "CaseClosedFL-Validator README"}
    return {"gate": "COMMIT", "reason": "no_published_hard_stop_hit", "source": "CaseClosedFL-Validator README"}


def ssdi_intake_ok(payload: dict) -> dict:
    name = str(payload.get("name") or "").strip()
    digits = "".join(ch for ch in str(payload.get("phone") or "") if ch.isdigit())
    tcpa = payload.get("tcpa") is True
    if len(name) < 2 or len(digits) < 10 or not tcpa:
        return {"ok": False, "status": 422, "error": "validation", "source": "ssdi-campaigns validate.mjs"}
    return {"ok": True, "source": "ssdi-campaigns validate.mjs"}
