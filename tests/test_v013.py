from __future__ import annotations

from prediction_engine.analog import retrieve
from prediction_engine.browser import chrome_available, dump_dom
from prediction_engine.contracts import list_contracts
from prediction_engine.houses import apply_10_to_0, bridge_0_to_1, bridge_10_to_0
from prediction_engine.mcp import invoke
from prediction_engine.outbox import ResendOutbox
from prediction_engine.playbook import list_facts


def test_new_portable_contracts_are_named_only():
    ids = {c["id"] for c in list_contracts()}
    assert "robyn-calibration-input" in ids
    assert "gads-reach-planner" in ids
    assert "adobe-mix-goal-plan" in ids
    assert "gads-campaign-to-forecast" in ids
    robyn = next(c for c in list_contracts() if c["id"] == "robyn-calibration-input")
    assert "liftStartDate" in robyn["fields"]
    assert "calibration_scope" in robyn["fields"]
    assert robyn["url"].startswith("https://")
    assert robyn.get("as_of")
    for contract in list_contracts():
        assert "cpl" not in contract
        assert "roas_value" not in contract
        assert not any(isinstance(contract.get(k), (int, float)) and k.endswith("_value") for k in contract)


def test_analog_ranks_reach_planner_and_lift_axes():
    hits = retrieve("reach planner geographic_location product_mix 92 days")
    ids = [h.get("id") for h in hits]
    assert "gads-reach-planner" in ids
    lift = retrieve("holdback_percentage study_duration conversion lift")
    assert any(h.get("id", "").startswith("gads-conversion-lift") for h in lift)


def test_bridge_strips_foreign_keys_without_mixing():
    cleaned = apply_10_to_0("pi", {"already_represented": True, "ssdi": True, "state": "FL"})
    assert cleaned["house"] == "pi"
    assert "ssdi" not in cleaned["payload"]
    assert cleaned["payload"]["state"] == "FL"
    assert cleaned["mixed"] is False
    ten = bridge_10_to_0("pi")
    assert ten["drop"] == ["ssdi"]
    one = bridge_0_to_1("ssdi")
    assert one["ledger"] == []
    assert one["seeded"] is True
    out = invoke("house.bridge", {"house": "ssdi", "mode": "10_to_0", "payload": {"name": "A"}})
    assert out["payload"]["name"] == "A"


def test_playbook_facts_carry_as_of():
    facts = list_facts()
    assert len(facts) == 11
    for fact in facts:
        assert fact.get("as_of")
        assert fact["url"].startswith("https://")


def test_outbox_draft_keeps_resend_shape(tmp_path):
    box = ResendOutbox()
    path = tmp_path / "drafts.jsonl"
    rec = box.queue_draft(
        {
            "to": ["ops@example.com"],
            "cc": "legal@example.com",
            "reply_to": "noreply@example.com",
            "subject": "sourced draft",
            "text": "no send",
            "tags": {"house": "pi"},
        },
        path=path,
    )
    assert rec["queued"] is True
    assert rec["sent"] is False
    assert rec["cc"] == ["legal@example.com"]
    assert rec["reply_to"] == ["noreply@example.com"]
    listed = box.list_drafts(path=path)
    assert len(listed) == 1


def test_chrome_dump_reports_presence():
    snap = dump_dom("<p>hello policy</p>")
    assert "hello policy" in snap["text"]
    assert snap["fetched"] is False
    assert "chrome" in snap
    assert chrome_available() in {True, False}
