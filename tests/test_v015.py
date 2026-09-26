from __future__ import annotations

from prediction_engine.analog import retrieve
from prediction_engine.contracts import list_contracts
from prediction_engine.houses import apply_10_to_0, bridge_0_to_1
from prediction_engine.outbox import ResendOutbox


def test_new_contracts_are_field_names_only():
    ids = {c["id"] for c in list_contracts()}
    assert "meridian-holdout-spec" in ids
    assert "adobe-mix-conversions" in ids
    assert "adobe-mix-harmonized-fields" in ids
    assert "gads-performance-planner-view" in ids
    assert "keen-planning-module" in ids
    holdout = next(c for c in list_contracts() if c["id"] == "meridian-holdout-spec")
    assert "holdout_id" in holdout["fields"]
    assert "GeoHoldoutSpec" in holdout["fields"]
    assert holdout["url"].startswith("https://developers.google.com/meridian/")
    assert holdout.get("as_of")
    for contract in list_contracts():
        blob = str(contract).lower()
        assert "cpl" not in blob
        assert '"roas"' not in blob


def test_analog_retrieves_holdout_and_harmonized_fields():
    hits = retrieve("holdout_id GeoHoldoutSpec date_ranges")
    assert any(h.get("id") == "meridian-holdout-spec" for h in hits)
    harm = retrieve("harmonized brand campaign channel_id event_date")
    assert any(h.get("id") == "adobe-mix-harmonized-fields" for h in harm)


def test_house_bridge_never_copies_foreign_ledger():
    cleaned = apply_10_to_0("ssdi", {"ssdi": True, "already_represented": False, "note": "keep"})
    assert cleaned["house"] == "ssdi"
    assert "already_represented" not in cleaned["payload"]
    assert cleaned["payload"]["note"] == "keep"
    assert cleaned["mixed"] is False
    one = bridge_0_to_1("pi")
    assert one["ledger"] == []
    assert "ssdi" not in one["path"]


def test_outbox_draft_keeps_scheduled_at(tmp_path):
    box = ResendOutbox()
    path = tmp_path / "drafts.jsonl"
    rec = box.queue_draft(
        {
            "to": "ops@example.com",
            "subject": "later",
            "text": "queued only",
            "scheduled_at": "2026-09-26T16:00:00Z",
            "headers": {"X-House": "pi"},
        },
        path=path,
    )
    assert rec["sent"] is False
    assert rec["scheduled_at"] == "2026-09-26T16:00:00Z"
    assert rec["headers"]["X-House"] == "pi"
    assert rec["shape"] == "resend"
