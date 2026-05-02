"""Qwen provider using DashScope OpenAI-compatible API."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.config import settings
from app.core.exceptions import bad_request
from app.services.llm.base import BaseLLMProvider, LLMMessage


class QwenProvider(BaseLLMProvider):
    """LLM provider implementation for qwen-plus."""

    def __init__(self) -> None:
        if not settings.LLM_API_KEY:
            raise bad_request("未配置 LLM_API_KEY，无法调用对话模型")

    @property
    def _chat_url(self) -> str:
        return f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _message_payload(messages: list[LLMMessage]) -> list[dict[str, str]]:
        return [{"role": item.role, "content": item.content} for item in messages]

    async def chat(
        self,
        *,
        messages: list[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> str:
        payload = {
            "model": settings.LLM_MODEL,
            "messages": self._message_payload(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(self._chat_url, headers=self._headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

    async def stream_chat(
        self,
        *,
        messages: list[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> AsyncIterator[str]:
        payload = {
            "model": settings.LLM_MODEL,
            "messages": self._message_payload(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            async with client.stream(
                "POST",
                self._chat_url,
                headers=self._headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_text = line.removeprefix("data:").strip()
                    if data_text == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_text)
                    except json.JSONDecodeError:
                        continue
                    delta = (
                        chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    if delta:
                        yield delta
