"""Analog retrieval over sourced playbook + portable contracts. No invented metrics."""

from __future__ import annotations

from prediction_engine.contracts import list_contracts
from prediction_engine.playbook import list_facts


def _tokens(text: str) -> set[str]:
    parts = [t.lower() for t in text.replace("/", " ").replace("-", " ").replace("_", " ").split() if len(t) > 2]
    grams = set(parts)
    for i in range(len(parts) - 1):
        grams.add(f"{parts[i]} {parts[i + 1]}")
    return grams


def _score(query_tokens: set[str], blob: str, extra_weight: int = 0) -> int:
    hay = blob.lower()
    score = extra_weight
    for tok in query_tokens:
        if tok in hay:
            score += 2 if len(tok) > 5 else 1
    return score


def retrieve(query: str, limit: int = 5, house: str | None = None) -> list[dict]:
    tokens = _tokens(query or "")
    ranked: list[tuple[int, dict]] = []
    wanted = (house or "").strip().lower() or None
    for fact in list_facts():
        fact_house = str(fact.get("house") or "").strip().lower() or None
        if wanted and fact_house and fact_house != wanted:
            continue
        blob = " ".join(str(fact.get(k) or "") for k in ("id", "publisher", "title", "claim"))
        score = _score(tokens, blob)
        if score:
            item = dict(fact)
            item["kind"] = "playbook_fact"
            item["analog_score"] = score
            ranked.append((score, item))
    for contract in list_contracts():
        fields = contract.get("fields") or []
        field_blob = " ".join(str(f) for f in fields) if isinstance(fields, list) else str(fields)
        blob = " ".join(
            [
                str(contract.get("id") or ""),
                str(contract.get("product") or ""),
                str(contract.get("title") or ""),
                field_blob,
            ]
        )
        extra = 2 if any(tok in field_blob.lower() for tok in tokens) else 0
        product = str(contract.get("product") or "").lower()
        if any(tok in product for tok in tokens if " " not in tok):
            extra += 1
        score = _score(tokens, blob, extra_weight=extra)
        if score:
            item = dict(contract)
            item["kind"] = "portable_contract"
            item["analog_score"] = score
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in ranked[:limit]]
