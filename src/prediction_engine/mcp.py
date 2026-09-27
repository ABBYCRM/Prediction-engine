"""Tiny MCP-style gateway: allowlisted tools only; reject unknown names and extra keys."""

from __future__ import annotations

from typing import Any, Callable

from prediction_engine.analog_store import hit_summary, read_hits
from prediction_engine.contracts import list_contracts
from prediction_engine.houses import HouseError, bridge_0_to_1, bridge_10_to_0
from prediction_engine.domain.intake_rules import ccfl_hard_stop, ssdi_intake_ok
from prediction_engine.engine import PredictionEngine
from prediction_engine.oauth import OAuthError
from prediction_engine.playbook import list_facts, match_facts
from prediction_engine.calibration import CalibrationError, record as cal_record, summary as cal_summary
from prediction_engine.ledger import append_local, read_ledger
from prediction_engine.research import list_run_index, sources_for
from prediction_engine.writeback import WritebackError
from prediction_engine.publishers import list_publishers
from prediction_engine.cadence import cadence_status
from prediction_engine.mailer import Mailer
from prediction_engine.sheets import SheetsError, preview_values_append, write_row
from prediction_engine.xai_client import XAIClient

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
    "mailer.preview": {"to", "subject", "body"},
    "sheets.preview": {"row"},
    "cadence.status": set(),
    "xai.guard": set(),
    "calibration.record": {"p", "y", "house", "query"},
    "calibration.summary": {"house"},
    "calibration.reliability": {"house"},
    "calibration.log_loss": {"house"},
    "ledger.append": {"row"},
    "analog.summary": {"house"},
    "research.list": {"house"},
    "research.sources": {"house"},
    "calibration.brier": {"house"},
    "calibration.means": {"house"},
    "calibration.mae": {"house"},
    "calibration.max_ae": {"house"},
}
