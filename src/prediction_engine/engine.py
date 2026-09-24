"""Compose playbook retrieval + optional xAI rewrite. Never invents market numbers."""

from __future__ import annotations

from dataclasses import dataclass, field

from prediction_engine.playbook import list_facts, match_facts
from prediction_engine.xai_client import XAIClient, XAIError


@dataclass
class PredictionResult:
    query: str
    facts: list[dict] = field(default_factory=list)
    answer: str = ""
    used_xai: bool = False
    note: str = ""


class PredictionEngine:
    def __init__(self, client: XAIClient | None = None) -> None:
        self.client = client or XAIClient()

    def predict(self, query: str) -> PredictionResult:
        facts = match_facts(query) or list_facts()[:3]
        sourced = "\n".join(
            f"- [{f.get('id')}] {f.get('claim')} (source: {f.get('url')})" for f in facts
        )
        base = (
            "Sourced ads-policy facts only. No performance metrics were invented.\n"
            f"{sourced}"
        )
        if not self.client.available():
            return PredictionResult(
                query=query,
                facts=facts,
                answer=base,
                used_xai=False,
                note="XAI_API_KEY unset; returning sourced facts only",
            )
        messages = [
            {
                "role": "system",
                "content": (
                    "You may only restate the provided sourced facts. "
                    "Do not invent CTR, CPC, conversion rates, or any market numbers."
                ),
            },
            {"role": "user", "content": f"Query: {query}\nFacts:\n{sourced}"},
        ]
        try:
            text = self.client.chat(messages)
        except XAIError as exc:
            return PredictionResult(
                query=query, facts=facts, answer=base, used_xai=False, note=str(exc)
            )
        return PredictionResult(query=query, facts=facts, answer=text, used_xai=True)
