"""stdlib HTTP API + static frontend. No DigitalOcean deploy."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from prediction_engine import __version__
from prediction_engine.cadence import cadence_status
from prediction_engine.config import get_settings
from prediction_engine.engine import PredictionEngine
from prediction_engine.analog_store import read_hits
from prediction_engine.mcp import MCPError, invoke, list_tools
from prediction_engine.oauth import (
    OAuthError,
    google_ads_status,
    google_sheets_status,
    meta_ads_status,
)
from prediction_engine.playbook import list_facts
from prediction_engine.ledger import ledger_summary, read_ledger
from prediction_engine.sheets import SheetsError, write_row

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
ENGINE = PredictionEngine()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _static(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self._json(404, {"error": "not_found"})
            return
        raw = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            settings = get_settings()
            facts = list_facts()
            self._json(
                200,
                {
                    "ok": True,
                    "service": "prediction-engine",
                    "version": __version__,
                    "xai_available": bool(settings.xai_api_key),
                    "xai_host": "api.x.ai",
                    "playbook_facts": len(facts),
                    "cadence": cadence_status(),
                    "mcp_tools": list_tools(),
                    "connectors": {
                        "google_ads": google_ads_status().present,
                        "google_sheets": google_sheets_status().present,
                        "meta_ads": meta_ads_status().present,
                    },
                },
            )
            return
        if path == "/tools":
            self._json(200, {"tools": list_tools()})
            return
        if path == "/facts":
            facts = list_facts()
            self._json(200, {"count": len(facts), "facts": facts})
            return
        if path == "/analogs":
            hits = read_hits(limit=50)
            self._json(200, {"count": len(hits), "hits": hits})
            return
        if path == "/ledger":
            summary = ledger_summary()
            rows = read_ledger(limit=50)
            self._json(200, {**summary, "rows": rows, "remote": False})
            return
        if path in {"/", "/index.html"}:
            self._static(FRONTEND / "index.html", "text/html; charset=utf-8")
            return
        if path == "/styles.css":
            self._static(FRONTEND / "styles.css", "text/css")
            return
        if path == "/app.js":
            self._static(FRONTEND / "app.js", "application/javascript")
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return
        if path == "/predict":
            query = str(body.get("query") or "").strip()
            if not query:
                self._json(400, {"error": "query_required"})
                return
            live = bool(body.get("live_scrape"))
            house = body.get("house")
            house_s = str(house).strip() if house else None
            result = ENGINE.predict(query, live_scrape=live, house=house_s)
            self._json(
                200,
                {
                    "query": result.query,
                    "answer": result.answer,
                    "facts": result.facts,
                    "used_xai": result.used_xai,
                    "note": result.note,
                    "analogs": result.analogs,
                    "scrape": result.scrape,
                    "live_scrape": live,
                    "house": result.house,
                },
            )
            return
        if path == "/writeback":
            try:
                out = write_row(body if isinstance(body, dict) else {})
            except (SheetsError, OAuthError) as exc:
                self._json(400, {"error": str(exc), "remote": False})
                return
            self._json(200, out)
            return
        if path == "/mcp":
            try:
                out = invoke(str(body.get("tool") or ""), body.get("arguments") or {})
            except MCPError as exc:
                self._json(400, {"error": str(exc)})
                return
            self._json(200, out)
            return
        self._json(404, {"error": "not_found"})


def main() -> None:
    settings = get_settings()
    server = ThreadingHTTPServer((settings.host, settings.port), Handler)
    print(f"prediction-engine listening on {settings.host}:{settings.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
