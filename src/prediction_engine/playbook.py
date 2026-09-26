"""Sourced ads-policy facts. No invented metrics."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_PATH = ROOT / "data" / "ads_playbook.json"


@lru_cache(maxsize=1)
def load_playbook() -> dict:
    return json.loads(PLAYBOOK_PATH.read_text(encoding="utf-8"))


def list_facts() -> list[dict]:
    pack = load_playbook()
    as_of = pack.get("as_of")
    facts = []
    for fact in pack.get("facts") or []:
        row = dict(fact)
        if as_of and not row.get("as_of"):
            row["as_of"] = as_of
        facts.append(row)
    return facts


def match_facts(query: str, limit: int = 5) -> list[dict]:
    tokens = {t.lower() for t in query.replace("/", " ").replace("-", " ").split() if len(t) > 2}
    scored: list[tuple[int, dict]] = []
    for fact in list_facts():
        blob = " ".join(
            [
                str(fact.get("id") or ""),
                str(fact.get("publisher") or ""),
                str(fact.get("title") or ""),
                str(fact.get("claim") or ""),
            ]
        ).lower()
        score = 0
        for t in tokens:
            if t in blob:
                score += 3 if t in str(fact.get("id") or "").lower() else 1
                if t in str(fact.get("publisher") or "").lower():
                    score += 1
        if score:
            scored.append((score, fact))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [fact for _, fact in scored[:limit]]
