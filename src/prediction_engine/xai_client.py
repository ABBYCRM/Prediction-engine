"""Minimal xAI chat client. Calls api.x.ai only when XAI_API_KEY is set."""

from __future__ import annotations

from typing import Any

import httpx

from urllib.parse import urlparse

from prediction_engine.config import ALLOWED_XAI_HOSTS, Settings, get_settings


class XAIError(RuntimeError):
    pass


class XAIClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def available(self) -> bool:
        return bool(self.settings.xai_api_key)

    def host_guard(self) -> dict[str, Any]:
        host = (urlparse(self.settings.xai_base_url).hostname or "").lower()
        return {
            "ok": host in ALLOWED_XAI_HOSTS,
            "host": host,
            "allowed_hosts": sorted(ALLOWED_XAI_HOSTS),
            "key_set": bool(self.settings.xai_api_key),
            "will_call": bool(self.settings.xai_api_key) and host in ALLOWED_XAI_HOSTS,
        }

    def chat(
        self,
        messages: list[dict[str, str]],
        timeout: float = 30.0,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        if not self.settings.xai_api_key:
            raise XAIError("XAI_API_KEY is not set; refusing to call any LLM host")
        url = f"{self.settings.xai_base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.settings.xai_model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
        headers = {
            "Authorization": f"Bearer {self.settings.xai_api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise XAIError(f"unexpected xAI payload: {exc}") from exc

    @staticmethod
    def search_tools() -> list[dict[str, Any]]:
        return [
            {"type": "web_search"},
            {"type": "x_search"},
        ]
