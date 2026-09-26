"""Deterministic HTML snapshotter. Optional local Chrome --dump-dom."""

from __future__ import annotations

import subprocess
from html.parser import HTMLParser
from shutil import which


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = " ".join(data.split())
        if text:
            self._chunks.append(text)

    def text(self) -> str:
        return " ".join(self._chunks)


def chrome_binary() -> str | None:
    return which("google-chrome") or which("chromium") or which("chromium-browser") or which("chrome")


def chrome_available() -> bool:
    return bool(chrome_binary())


def snapshot_html(html: str, limit: int = 4000) -> str:
    parser = _TextExtractor()
    parser.feed(html or "")
    return parser.text()[:limit]


def dump_dom(html: str | None = None, limit: int = 4000) -> dict:
    """Local Chrome path when a binary exists; otherwise snapshot-only."""
    text = snapshot_html(html or "", limit=limit)
    return {
        "chrome": chrome_available(),
        "fetched": False,
        "note": "chrome_present" if chrome_available() else "chrome_absent_snapshot_only",
        "text": text,
    }


def chrome_dump_dom(url: str, timeout: float = 20.0, limit: int = 4000) -> dict:
    """Run local Chrome headless --dump-dom. Caller must SSRF-check first."""
    binary = chrome_binary()
    if not binary:
        return {
            "url": url,
            "chrome": False,
            "fetched": False,
            "note": "chrome_absent_snapshot_only",
            "text": "",
        }
    cmd = [
        binary,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        url,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "url": url,
            "chrome": True,
            "fetched": False,
            "note": f"chrome_failed:{type(exc).__name__}",
            "text": "",
        }
    html = proc.stdout or ""
    return {
        "url": url,
        "chrome": True,
        "fetched": proc.returncode == 0 and bool(html),
        "note": "chrome_dump_dom" if proc.returncode == 0 else f"chrome_exit:{proc.returncode}",
        "text": snapshot_html(html, limit=limit),
    }
