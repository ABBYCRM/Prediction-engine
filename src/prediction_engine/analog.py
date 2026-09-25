"""Analog retrieval over sourced playbook + portable contracts. No invented metrics."""

from __future__ import annotations

from prediction_engine.contracts import list_contracts
from prediction_engine.playbook import list_facts


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in text.replace("/", " ").replace("-", " ").split() if len(t) > 2}


def _score(query_tokens: set[str], blob: str) -> int:
    hay = blob.lower()
    score = 0
    for tok in query_tokens:
        if tok in hay:
            score += 2 if len(tok) > 5 else 1
    return score


def retrieve(query: str, limit: int = 5) -> list[dict]:
    tokens = _tokens(query or "")
    ranked: list[tuple[int, dict]] = []
    for fact in list_facts():
        blob = " ".join(str(fact.get(k) or "") for k in ("id", "publisher", "title", "claim"))
        score = _score(tokens, blob)
        if score:
            item = dict(fact)
            item["kind"] = "playbook_fact"
            item["analog_score"] = score
            ranked.append((score, item))
    for contract in list_contracts():
        blob = " ".join(str(contract.get(k) or "") for k in ("id", "product", "title", "fields"))
        score = _score(tokens, blob)
        if score:
            item = dict(contract)
            item["kind"] = "portable_contract"
            item["analog_score"] = score
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in ranked[:limit]]
