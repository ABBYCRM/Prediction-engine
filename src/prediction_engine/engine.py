"""Compose playbook retrieval + optional xAI rewrite. Never invents market numbers."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

from prediction_engine.analog import retrieve
from prediction_engine.analog_store import persist_hits
from prediction_engine.playbook import list_facts, match_facts
from prediction_engine.publishers import is_allowlisted_publisher_url
from prediction_engine.xai_client import XAIClient, XAIError


@dataclass
class PredictionResult:
    query: str
    facts: list[dict] = field(default_factory=list)
    answer: str = ""
    used_xai: bool = False
    note: str = ""
    analogs: list[dict] = field(default_factory=list)
    scrape: dict | None = None


class PredictionEngine:
    def __init__(self, client: XAIClient | None = None, scrape_fn=None) -> None:
        self.client = client or XAIClient()
        self.scrape_fn = scrape_fn

    def _maybe_scrape(self, query: str, facts: list[dict]) -> dict | None:
        candidates: list[str] = []
        for token in query.split():
            if token.startswith("http://") or token.startswith("https://"):
                candidates.append(token)
        for fact in facts:
            url = str(fact.get("url") or "")
            if url:
                candidates.append(url)
        for url in candidates:
            if not is_allowlisted_publisher_url(url):
                continue
            if self.scrape_fn is None:
                return {
                    "url": url,
                    "fetched": False,
                    "note": "scrape_skipped_default_predict",
                    "host": (urlparse(url).hostname or ""),
                }
            return self.scrape_fn(url)
        return None

    def predict(self, query: str) -> PredictionResult:
        query = (query or "").strip()
        if not query:
            return PredictionResult(
                query="",
                facts=[],
                answer="",
                used_xai=False,
                note="query_required",
            )
        facts = match_facts(query) or list_facts()[:3]
        analogs = retrieve(query)
        persist_hits(query, analogs)
        scrape = self._maybe_scrape(query, facts)
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
                analogs=analogs,
                scrape=scrape,
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
                query=query,
                facts=facts,
                answer=base,
                used_xai=False,
                note=str(exc),
                analogs=analogs,
                scrape=scrape,
            )
        return PredictionResult(
            query=query,
            facts=facts,
            answer=text,
            used_xai=True,
            analogs=analogs,
            scrape=scrape,
        )
