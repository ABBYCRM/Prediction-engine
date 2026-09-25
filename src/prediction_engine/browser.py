"""Deterministic HTML snapshotter (no headless browser binary required)."""

from __future__ import annotations

from html.parser import HTMLParser


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


def chrome_available() -> bool:
    from shutil import which

    return bool(which("google-chrome") or which("chromium") or which("chromium-browser"))


def dump_dom(html: str | None = None, limit: int = 4000) -> dict:
    """Local Chrome path when a binary exists; otherwise snapshot-only."""
    text = snapshot_html(html or "", limit=limit)
    return {
        "chrome": chrome_available(),
        "fetched": False,
        "note": "chrome_present" if chrome_available() else "chrome_absent_snapshot_only",
        "text": text,
    }


def snapshot_html(html: str, limit: int = 4000) -> str:
    parser = _TextExtractor()
    parser.feed(html or "")
    return parser.text()[:limit]
