"""Ollama client adapter used by all agents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Iterable, Optional

import requests
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from config.settings import settings


@dataclass
class LLMResponse:
    content: str


class OllamaClient:
    """Minimal OpenAI-compatible Ollama client."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    def _serialize_messages(self, messages: Iterable[BaseMessage]) -> list[dict[str, str]]:
        payload: list[dict[str, str]] = []
        for message in messages:
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                role = "user"
            payload.append({"role": role, "content": str(message.content)})
        return payload

    def invoke(self, messages: Iterable[BaseMessage]) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": self._serialize_messages(messages),
            "temperature": settings.OLLAMA_TEMPERATURE,
            "max_tokens": settings.OLLAMA_MAX_TOKENS,
        }
        response = requests.post(self.base_url, json=payload, timeout=settings.OLLAMA_TIMEOUT_SECONDS)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        content = data["choices"][0]["message"]["content"]
        return LLMResponse(content=content)

    async def ainvoke(self, messages: Iterable[BaseMessage]) -> LLMResponse:
        return await asyncio.to_thread(self.invoke, list(messages))


class LocalFallbackClient:
    """A tiny deterministic local 'LLM' used for development when no server is available.

    It inspects the system prompt to guess the agent role and returns simple,
    structured outputs that let the pipeline continue.
    """

    def invoke(self, messages: Iterable[BaseMessage]) -> LLMResponse:
        msgs = list(messages)
        system = msgs[0].content.lower() if msgs else ""
        user = msgs[-1].content if msgs else ""

        # Router: return first available domain or 'generic'
        if "domain classifier" in system or "available domains" in system:
            # try to parse available domains from the system prompt
            lines = system.splitlines()
            domains = [l.strip("- ") for l in lines if l.strip().startswith("-")]
            choice = domains[0] if domains else settings.DEFAULT_DOMAIN
            return LLMResponse(content=choice)

        # Think phase: build simple XML sections
        if "perform structured reasoning" in system or "<known>" in system:
            known = f"<known>{user[:200]}</known>"
            assumptions = "<assumptions>none</assumptions>"
            missing = "<missing>none</missing>"
            return LLMResponse(content=f"{known}\n{assumptions}\n{missing}")

        # Tool selector: pick first tool listed in the user content
        if "you are a tool selector" in system:
            lines = user.splitlines()
            tools = [l.strip().lstrip("- ") for l in lines if l.strip().startswith("-")]
            choice = tools[0] if tools else "none"
            return LLMResponse(content=choice)

        # Result integrator: if 'Still missing' contains '(none)' -> proceed else loop
        if "you are an integration decision maker" in system or "decide whether to loop" in system:
            if "still missing:" in user.lower() and "(none)" in user.lower():
                return LLMResponse(content="proceed")
            # default: if the text mentions 'missing' assume need to loop
            if "missing" in user.lower():
                return LLMResponse(content="loop")
            return LLMResponse(content="proceed")

        # Materiality filter: return JSON array scoring each newline as 3
        if "materiality filter" in system or "score findings" in system:
            findings = [l for l in user.splitlines() if l.strip()]
            items = []
            for f in findings:
                text = f.strip()
                items.append({"text": text, "score": 3, "category": "generic"})
            import json

            return LLMResponse(content=json.dumps(items))

        # Default: echo back the user content (safe fallback)
        return LLMResponse(content=str(user))

    async def ainvoke(self, messages: Iterable[BaseMessage]) -> LLMResponse:
        return await asyncio.to_thread(self.invoke, list(messages))


class LLMWrapper:
    """Wrapper that prefers Ollama but can fall back to a local client.

    Behavior controlled by `settings.USE_LOCAL_FALLBACK` and `settings.FALLBACK_ON_ERROR`.
    """

    def __init__(self):
        self._ollama = OllamaClient()
        self._local = LocalFallbackClient()

    def invoke(self, messages: Iterable[BaseMessage]) -> LLMResponse:
        # Prefer an explicit local fallback
        if settings.USE_LOCAL_FALLBACK:
            return self._local.invoke(messages)

        try:
            return self._ollama.invoke(messages)
        except Exception:
            if settings.FALLBACK_ON_ERROR:
                return self._local.invoke(messages)
            raise

    async def ainvoke(self, messages: Iterable[BaseMessage]) -> LLMResponse:
        if settings.USE_LOCAL_FALLBACK:
            return await self._local.ainvoke(messages)

        try:
            return await self._ollama.ainvoke(messages)
        except Exception:
            if settings.FALLBACK_ON_ERROR:
                return await self._local.ainvoke(messages)
            raise


_client: Optional[LLMWrapper] = None


def get_llm() -> LLMWrapper:
    global _client
    if _client is None:
        _client = LLMWrapper()
    return _client
