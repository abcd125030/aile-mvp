"""Common LLM provider interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass(slots=True)
class LLMMessage:
    role: str
    content: str


class BaseLLMProvider(ABC):
    """Provider-agnostic LLM interface."""

    @abstractmethod
    async def chat(
        self,
        *,
        messages: list[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> str:
        """Return the full assistant text."""

    @abstractmethod
    async def stream_chat(
        self,
        *,
        messages: list[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> AsyncIterator[str]:
        """Yield assistant text chunks."""
