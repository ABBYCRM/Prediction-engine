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


def snapshot_html(html: str, limit: int = 4000) -> str:
    parser = _TextExtractor()
    parser.feed(html or "")
    return parser.text()[:limit]
