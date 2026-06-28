# Author: Ck.epsilon
"""Multi-agent orchestration engine.

Defines Agent roles, manages conversation context, routes messages,
and handles tool-calling loops across multiple LLM providers.
"""

import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from llm_client import LLMClient, create_client
from tools import BUILTIN_TOOLS, get_tool_schemas, execute_tool


@dataclass
class Agent:
    """An AI agent with a role, model, tools, and conversation memory."""

    name: str
    system_prompt: str
    model: str = "qwen2.5:7b"
    provider: str = "ollama"
    tools: list[str] = field(default_factory=list)
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "provider": self.provider,
            "tools": self.tools,
        }


class Orchestrator:
    """Manages multiple agents and routes messages between them.

    Supports:
    - Direct chat with a specific agent
    - Multi-turn conversation with tool-calling loops
    - Streaming output via async generator
    - Agent handoff (one agent can delegate to another)
    """

    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def create_agent(
        self,
        name: str,
        system_prompt: str,
        model: str = "qwen2.5:7b",
        provider: str = "ollama",
        tools: list[str] | None = None,
    ) -> Agent:
        agent = Agent(
            name=name,
            system_prompt=system_prompt,
            model=model,
            provider=provider,
            tools=tools or [],
        )
        self._agents[name] = agent
        return agent

    def get_agent(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[dict]:
        return [a.to_dict() for a in self._agents.values()]

    async def chat_stream(
        self,
        agent_name: str,
        user_message: str,
    ) -> AsyncIterator[dict]:
        """Stream a conversation with an agent, including tool calling loops."""
        agent = self._agents.get(agent_name)
        if not agent:
            yield {"type": "error", "message": f"Agent '{agent_name}' not found"}
            return

        client: LLMClient = create_client(agent.provider)
        agent.messages.append({"role": "user", "content": user_message})

        max_turns = 5  # Prevent infinite loops
        for _ in range(max_turns):
            tool_schemas = get_tool_schemas(agent.tools) if agent.tools else None
            tool_calls_made: list[dict] = []

            async for chunk in client.chat_stream(
                messages=agent.messages,
                model=agent.model,
                tools=tool_schemas,
            ):
                if chunk["type"] == "text":
                    yield chunk
                elif chunk["type"] == "tool_call":
                    tool_calls_made.append(chunk)
                    yield chunk
                elif chunk["type"] == "done":
                    pass

            # Process tool calls
            if not tool_calls_made:
                break

            # Execute tools and feed results back
            for tc in tool_calls_made:
                try:
                    args = tc["arguments"]
                    if isinstance(args, str):
                        args = json.loads(args)
                except (json.JSONDecodeError, TypeError):
                    args = {}

                result = await execute_tool(tc["name"], args)
                yield {
                    "type": "tool_result",
                    "name": tc["name"],
                    "result": result,
                }
                agent.messages.append({
                    "role": "tool",
                    "name": tc["name"],
                    "content": result,
                })

        yield {"type": "done", "usage": {}}
