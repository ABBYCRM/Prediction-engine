"""Compose playbook retrieval + optional xAI rewrite. Never invents market numbers."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

from prediction_engine.analog import retrieve
from prediction_engine.analog_store import persist_hits
from prediction_engine.houses import HouseError, assert_single_house
from prediction_engine.playbook import list_facts, match_facts
from prediction_engine.publishers import is_allowlisted_publisher_url
from prediction_engine.scraper import SSRFError, scrape_public
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
    house: str | None = None


class PredictionEngine:
    def __init__(self, client: XAIClient | None = None, scrape_fn=None) -> None:
        self.client = client or XAIClient()
        self.scrape_fn = scrape_fn

    def _maybe_scrape(self, query: str, facts: list[dict], live_scrape: bool) -> dict | None:
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
            host = urlparse(url).hostname or ""
            if not live_scrape:
                return {
                    "url": url,
                    "fetched": False,
                    "note": "scrape_skipped_default_predict",
                    "host": host,
                }
            fn = self.scrape_fn or scrape_public
            try:
                out = fn(url)
            except SSRFError as exc:
                return {
                    "url": url,
                    "fetched": False,
                    "note": f"scrape_blocked:{exc}",
                    "host": host,
                }
            except Exception as exc:
                return {
                    "url": url,
                    "fetched": False,
                    "note": f"scrape_failed:{type(exc).__name__}",
                    "host": host,
                }
            if isinstance(out, dict):
                out.setdefault("url", url)
                out.setdefault("host", host)
                return out
            return {"url": url, "fetched": True, "host": host, "note": "scrape_ok"}
        return None

    def predict(
        self,
        query: str,
        live_scrape: bool = False,
        house: str | None = None,
    ) -> PredictionResult:
        query = (query or "").strip()
        house_name: str | None = None
        if house:
            try:
                house_name = assert_single_house(house)
            except HouseError as exc:
                return PredictionResult(
                    query=query,
                    facts=[],
                    answer="",
                    used_xai=False,
                    note=f"house_rejected:{exc}",
                    house=None,
                )
        if not query:
            return PredictionResult(
                query="",
                facts=[],
                answer="",
                used_xai=False,
                note="query_required",
                house=house_name,
            )
        facts = match_facts(query) or list_facts()[:3]
        analogs = retrieve(query, house=house_name)
        persist_hits(query, analogs, house=house_name)
        scrape = self._maybe_scrape(query, facts, live_scrape)
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
                house=house_name,
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
                house=house_name,
            )
        return PredictionResult(
            query=query,
            facts=facts,
            answer=text,
            used_xai=True,
            analogs=analogs,
            scrape=scrape,
            house=house_name,
        )
