# Author: Ck.epsilon
"""AI Agent Workbench — Multi-model AI development platform backend.

FastAPI application providing:
- Multi-model chat with streaming (Ollama / OpenAI / Tongyi)
- WebSocket for real-time token-by-token output
- Agent creation and management
- Function calling with tool execution
- Model listing
- Rate limiting (Premium tier)
- Task history persistence (Premium tier)
"""

import json
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from llm_client import create_client
from agent_engine import Orchestrator
from tools import BUILTIN_TOOLS, execute_tool, get_tool_schemas
from db import create_task, finish_task, add_message
from alerter import alerter


# ---------------------------------------------------------------------------
# Rate limiter setup (Premium tier)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AI Agent Workbench", version="1.1.0")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

# Pre-create default agents
orchestrator.create_agent(
    name="assistant",
    system_prompt="You are a helpful AI assistant. Use tools when appropriate to answer questions accurately.",
    model="qwen2.5:7b",
    provider="ollama",
    tools=["calculator", "get_time", "web_search"],
)

orchestrator.create_agent(
    name="coder",
    system_prompt="You are a senior software engineer. Write clean, production-ready code. Use code_executor and calculator tools when needed. Explain your reasoning briefly.",
    model="qwen2.5:7b",
    provider="ollama",
    tools=["calculator", "code_executor", "file_read"],
)

orchestrator.create_agent(
    name="researcher",
    system_prompt="You are a research analyst. Gather information, synthesize findings, and present clear conclusions. Use web_search extensively.",
    model="qwen2.5:7b",
    provider="ollama",
    tools=["web_search", "get_time", "file_read"],
)


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------
@app.get("/models")
async def list_models(provider: str = "ollama"):
    """List available models for a given provider."""
    try:
        client = create_client(provider)
        models = await client.list_models()
        return {"provider": provider, "models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/providers")
async def list_providers():
    """List available LLM providers."""
    return {
        "providers": [
            {"id": "ollama", "name": "Ollama (Local)", "requires_key": False},
            {"id": "openai", "name": "OpenAI", "requires_key": True},
            {"id": "tongyi", "name": "Tongyi Qwen", "requires_key": True},
        ]
    }


@app.get("/tools")
async def list_tools():
    """List all available tools (built-in + custom)."""
    from tools import list_registered_tools
    return {"tools": list_registered_tools()}


@app.post("/tools/register")
async def register_custom_tool(body: dict[str, Any]):
    """Register a custom tool at runtime (Premium tier).
    Body: {name, description, parameters: {...}}.
    Handler is a Python function name from sandbox.py for safety.
    """
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    description = body.get("description", "")
    parameters = body.get("parameters", {})
    if not parameters:
        raise HTTPException(status_code=400, detail="parameters (JSON Schema) required")

    try:
        from tools import register_tool
        register_tool(name, description, parameters, lambda **kw: f"Custom tool '{name}' executed with {kw}")
        return {"status": "registered", "tool": name}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/agents")
async def create_agent(body: dict[str, Any]):
    """Create a new agent with specified role, model, and tools."""
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Agent name is required")

    agent = orchestrator.create_agent(
        name=name,
        system_prompt=body.get("system_prompt", "You are a helpful assistant."),
        model=body.get("model", "qwen2.5:7b"),
        provider=body.get("provider", "ollama"),
        tools=body.get("tools", []),
    )
    return agent.to_dict()


@app.get("/agents")
async def list_agents():
    """List all configured agents."""
    return {"agents": orchestrator.list_agents()}


@app.get("/tasks")
async def list_tasks(agent_name: str | None = None, limit: int = 20):
    """List recent task history (Premium tier)."""
    from db import get_task_history
    return {"tasks": get_task_history(agent_name=agent_name, limit=limit)}


# ---------------------------------------------------------------------------
# WebSocket — real-time streaming chat
# ---------------------------------------------------------------------------
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Stream AI responses token-by-token with tool call visualization.

    Client sends JSON::

        {"agent": "assistant", "message": "Hello!", "provider": "ollama", "model": "qwen2.5:7b"}

    Server responds with streaming JSON::

        {"type": "text", "content": "He"}
        {"type": "text", "content": "llo"}
        {"type": "tool_call", "name": "calculator", "arguments": {...}}
        {"type": "tool_result", "name": "calculator", "result": "42"}
        {"type": "done", "usage": {...}}
    """
    await websocket.accept()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            agent_name = msg.get("agent", "assistant")
            user_message = msg.get("message", "")

            if not user_message:
                await websocket.send_json({"type": "error", "message": "message is required"})
                continue

            # Persist task (Premium tier)
            task_id = create_task(agent_name, user_message)
            add_message(task_id, "user", user_message)

            try:
                async for chunk in orchestrator.chat_stream(
                    agent_name=agent_name,
                    user_message=user_message,
                ):
                    if chunk["type"] == "text":
                        add_message(task_id, "assistant", chunk["content"])
                    await websocket.send_json(chunk)
                finish_task(task_id, "completed")
                alerter.notify_task_complete(task_id, agent_name, user_message[:100])
            except Exception as e:
                finish_task(task_id, "failed", str(e))
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": f"WebSocket error: {exc}"})


# ---------------------------------------------------------------------------
# REST streaming endpoint (alternative to WebSocket)
# ---------------------------------------------------------------------------
@app.post("/chat")
@limiter.limit("10/minute")
async def chat_rest(request: Request, body: dict[str, Any]):
    """Non-streaming chat endpoint. Rate limited: 10 req/min. Returns complete response."""
    agent_name = body.get("agent", "assistant")
    user_message = body.get("message", "")

    if not user_message:
        raise HTTPException(status_code=400, detail="message is required")

    task_id = create_task(agent_name, user_message)
    add_message(task_id, "user", user_message)

    full_response = ""
    tool_calls = []

    try:
        async for chunk in orchestrator.chat_stream(
            agent_name=agent_name,
            user_message=user_message,
        ):
            if chunk["type"] == "text":
                full_response += chunk["content"]
                add_message(task_id, "assistant", chunk["content"])
            elif chunk["type"] == "tool_call":
                tool_calls.append({"name": chunk["name"], "arguments": chunk["arguments"]})
        finish_task(task_id, "completed")
        alerter.notify_task_complete(task_id, agent_name, user_message[:100])
    except Exception as e:
        finish_task(task_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "agent": agent_name,
        "response": full_response,
        "tool_calls": tool_calls,
        "task_id": task_id,
    }


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}
