"""Provider selector for LLM calls."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.config import settings
from app.core.exceptions import bad_request
from app.services.llm.base import BaseLLMProvider, LLMMessage
from app.services.llm.qwen_provider import QwenProvider


class LLMService:
    """Facade for model calls with provider fallback handling."""

    def __init__(self) -> None:
        self.provider: BaseLLMProvider | None = None

    @staticmethod
    def _build_provider() -> BaseLLMProvider:
        provider = settings.LLM_PROVIDER.lower().strip()
        if provider == "qwen":
            return QwenProvider()
        raise bad_request(f"不支持的 LLM provider: {settings.LLM_PROVIDER}")

    async def chat(
        self,
        *,
        messages: list[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 512,
        fallback_text: str = "我在整理思路，先给你一个简短方向：先把题目信息再描述得具体一点。",
    ) -> str:
        try:
            provider = self.provider or self._build_provider()
            self.provider = provider
            return await provider.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception:
            return fallback_text

    async def stream_chat(
        self,
        *,
        messages: list[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 512,
        fallback_text: str = "我在整理思路，先给你一个简短方向：把不懂的点和你卡住的步骤再说一遍。",
    ) -> AsyncIterator[str]:
        try:
            provider = self.provider or self._build_provider()
            self.provider = provider
            async for chunk in provider.stream_chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                yield chunk
            return
        except Exception:
            pass
        yield fallback_text
