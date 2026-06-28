# Author: Ck.epsilon
"""Multi-model LLM client with unified streaming interface.

Supports Ollama (local), OpenAI-compatible, and Tongyi Qwen models
through a single ``chat_stream()`` async generator API.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional

import httpx


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------
class LLMClient(ABC):
    """Abstract base for LLM providers."""

    provider: str = ""

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        tools: Optional[list[dict]] = None,
    ) -> AsyncIterator[dict]:
        """Yield streaming response chunks.

        Each chunk is a dict with at least::

            {"type": "text", "content": "..."}
            {"type": "tool_call", "name": "...", "arguments": {...}}
            {"type": "done", "usage": {...}}
        """
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        """Return available model names.

        Raises:
            RuntimeError: If the provider is unreachable.
        """
        ...


# ---------------------------------------------------------------------------
# Ollama (local)
# ---------------------------------------------------------------------------
class OllamaClient(LLMClient):
    provider = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "qwen2.5:7b",
        tools: Optional[list[dict]] = None,
    ) -> AsyncIterator[dict]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                buffer = ""
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if chunk.get("done"):
                        yield {"type": "done", "usage": chunk.get("total_duration", 0)}
                        break

                    msg = chunk.get("message", {})
                    content = msg.get("content", "")
                    if content:
                        buffer += content
                        yield {"type": "text", "content": content}

                    # Tool calls from Ollama
                    tool_calls = msg.get("tool_calls", [])
                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        yield {
                            "type": "tool_call",
                            "name": fn.get("name", ""),
                            "arguments": fn.get("arguments", {}),
                        }

    async def list_models(self) -> list[str]:
        """Query Ollama for installed models. Raises if unreachable."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]


# ---------------------------------------------------------------------------
# OpenAI-compatible (GPT-4, QwenPaw, any OpenAI API)
# ---------------------------------------------------------------------------
class OpenAIClient(LLMClient):
    provider = "openai"

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
    ):
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def api_key(self) -> str:
        """Lazy-read API key from env if not provided at init."""
        return self._api_key or os.environ.get("OPENAI_API_KEY", "sk-local")

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4o-mini",
        tools: Optional[list[dict]] = None,
    ) -> AsyncIterator[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                tool_calls_buffer: list[dict] = []
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        yield {"type": "done", "usage": {}}
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    delta = chunk.get("choices", [{}])[0].get("delta", {})

                    content = delta.get("content", "")
                    if content:
                        yield {"type": "text", "content": content}

                    tc = delta.get("tool_calls", [])
                    for t in tc:
                        idx = t.get("index", 0)
                        while len(tool_calls_buffer) <= idx:
                            tool_calls_buffer.append(
                                {"id": "", "name": "", "arguments": ""}
                            )
                        buf = tool_calls_buffer[idx]
                        if "id" in t:
                            buf["id"] = t["id"]
                        if t.get("function", {}).get("name"):
                            buf["name"] = t["function"]["name"]
                        if t.get("function", {}).get("arguments"):
                            buf["arguments"] += t["function"]["arguments"]

                # Flush tool calls
                for buf in tool_calls_buffer:
                    if buf["name"]:
                        yield {
                            "type": "tool_call",
                            "name": buf["name"],
                            "arguments": buf["arguments"],
                        }

    async def list_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]


# ---------------------------------------------------------------------------
# Tongyi Qwen (DashScope)
# ---------------------------------------------------------------------------
class TongyiClient(LLMClient):
    provider = "tongyi"

    def __init__(self, api_key: str = ""):
        self._api_key = api_key

    @property
    def api_key(self) -> str:
        """Lazy-read API key from env if not provided at init."""
        return self._api_key or os.environ.get("DASHSCOPE_API_KEY", "sk-local")

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "qwen-plus",
        tools: Optional[list[dict]] = None,
    ) -> AsyncIterator[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {
                "result_format": "message",
                "incremental_output": True,
            },
        }
        if tools:
            payload["parameters"]["tools"] = tools

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        yield {"type": "done", "usage": {}}
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield {"type": "text", "content": content}

    async def list_models(self) -> list[str]:
        return ["qwen-plus", "qwen-max", "qwen-turbo"]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def create_client(provider: str) -> LLMClient:
    """Create an LLM client by provider name.

    Creates a fresh instance each call — no shared mutable state.
    """
    clients = {
        "ollama": OllamaClient,
        "openai": OpenAIClient,
        "tongyi": TongyiClient,
    }
    cls = clients.get(provider)
    if not cls:
        raise ValueError(
            f"Unknown provider: {provider}. Available: {list(clients.keys())}"
        )
    return cls()
