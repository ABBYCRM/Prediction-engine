from __future__ import annotations

import pytest

from prediction_engine.analog_store import persist_hits, read_hits
from prediction_engine.mcp import MCPError, invoke, list_tools
from prediction_engine.publishers import list_publishers


def test_list_publishers_includes_floor_hosts():
    listing = list_publishers()
    assert listing["live_fetch"] is False
    assert "support.google.com" in listing["hosts"]
    assert "transparency.meta.com" in listing["hosts"]
    assert listing["count"] == len(listing["hosts"])


def test_mcp_publishers_list_and_extra_keys():
    assert "publishers.list" in list_tools()
    out = invoke("publishers.list", {})
    assert out["count"] >= 2
    assert out["live_fetch"] is False
    with pytest.raises(MCPError):
        invoke("publishers.list", {"extra": 1})


def test_analog_log_filters_house(tmp_path):
    path = tmp_path / "hits.jsonl"
    persist_hits(
        "google ads policy",
        [{"id": "gads-areas", "kind": "playbook_fact", "analog_score": 2}],
        path=path,
        house="pi",
    )
    persist_hits(
        "ssa disability",
        [{"id": "ssa-overview", "kind": "playbook_fact", "analog_score": 1}],
        path=path,
        house="ssdi",
    )
    pi_hits = read_hits(path=path, house="pi")
    assert len(pi_hits) == 1
    assert pi_hits[0]["house"] == "pi"
