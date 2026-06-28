# Fiverr Gig #5: AI Agent Workbench — Multi-Agent AI Platform

> **Author:** Ck.epsilon & Chaos (AI Programming Assistant)
> **Stack:** Python · FastAPI · WebSocket · Ollama · OpenAI API · Tongyi · Docker
> **Portfolio:** [github.com/ck-epsilon](https://github.com/ck-epsilon) *(new account, portfolio growing — live previews available on request)*
> **Live demo:** Contact me for a live walkthrough — I'll share a private demo link.

## Gig 基本信息

| 字段 | 内容 |
|------|------|
| **Title** | Build a multi-agent AI workbench with LLM integration and streaming chat |
| **Category** | Programming & Tech → AI Development → AI Chatbot Development |
| **Service Type** | Custom AI Application Development |
| **Price Tiers** | Basic $120 / Standard $250 / Premium $600 |
| **Delivery Time** | 3 / 5 / 10 days |

## Gig Description

**I'll build your AI agent workbench — multi-agent orchestration, streaming chat, and a clean web UI.**

This isn't a ChatGPT wrapper. It's a full AI development platform: plug in any LLM (Ollama/OpenAI/Tongyi), create role-based agents with tools, and watch them collaborate in real time via WebSocket streaming. Three-column dashboard: your agents on the left, streaming chat in the center, tool calls visualized on the right.

**What you get:**
- Multi-provider LLM integration (Ollama, OpenAI-compatible, Tongyi)
- 5 built-in tools: calculator ✓, time ✓, web search (simulated*), code executor (simulated*), file reader ✓ — real tools marked ✓, simulated ones ready for upgrade
- Custom tool creation — define your own Function Calling tools
- Multi-agent orchestration with role assignment and context memory
- WebSocket streaming — token-by-token real-time output
- Tool call visualization — see exactly what each agent is doing
- Zero-dependency single-file frontend (no npm install needed)
- Clean, responsive UI — dark theme, mobile-friendly

*\*web_search and code_executor are simulated in the included demo. They can be upgraded to real implementations (API keys for SerpAPI, sandboxed execution environment) — included in Premium tier.*

**Why this instead of LangChain / CrewAI / off-the-shelf frameworks?**
- **Zero framework lock-in** — no LangChain dependency. Pure Python + FastAPI. You understand every line.
- **Self-contained** — runs on your machine with Ollama (no cloud API costs for Basic/Standard tiers). Or plug in OpenAI/Tongyi.
- **Visual and interactive** — not a terminal script. Real-time streaming UI with tool call visualization. See agents think.
- **Lighter than CrewAI** — no 200+ dependency tree. Single `requirements.txt`, single HTML file.

**What you need to provide:**
- LLM preference: local Ollama (free, CPU-only OK) or cloud API keys (OpenAI/Tongyi)
- Agent roles and goals — e.g., "Researcher agent that searches the web and summarizes findings"
- Custom tool descriptions if you need tools beyond the built-in 5

**Not sure what you need?** Message me first. I'll help you scope it in 1-2 questions.

---

## Price Tiers

### Basic ($120) — 3 Days · ⭐ Single Agent Starter
- Single-agent setup with Ollama (local LLM, no API costs)
- 3 built-in tools (calculator ✓, web search*, time ✓)
- REST API endpoint for chat
- Frontend with chat interface
- README with setup instructions
- One model: qwen2.5:7b or your choice

### Standard ($250) — 5 Days · 🔥 Multi-Agent Team
- Multi-agent orchestration (2-3 agents with roles)
- 5 built-in tools (add code executor*, file reader ✓)
- WebSocket streaming with tool call visualization
- Three-column frontend dashboard
- Custom agent roles and system prompts
- Docker + docker-compose
- Model switching UI

### Premium ($600) — 10 Days · 🚀 Production Platform
- Multi-provider integration (Ollama + OpenAI + Tongyi)
- 10+ custom Function Calling tools (including real web search & code executor)
- Agent-to-agent conversation chaining
- Persistent conversation history (SQLite/PostgreSQL)
- Streaming token usage tracking
- Custom branding (your logo/colors)
- CI/CD pipeline (GitHub Actions)
- Deployment guide to your server or cloud
- Optional: LangChain/LlamaIndex integration

---

## FAQ

**Q: Do I need a GPU?**
A: No. CPU-only works fine with Ollama (expect 2-3x slower generation vs GPU). For OpenAI/Tongyi, you just need an API key — no local hardware needed at all.

**Q: Can I use my own API keys for OpenAI?**
A: Yes. The platform supports OpenAI-compatible endpoints. You provide the key, it stays in your `.env` file. Never sent to any third party.

**Q: What kind of custom tools can you build?**
A: Anything with Function Calling — database queries, API integrations, file processing, email, Slack, custom calculations. Describe your use case and I'll scope it.

**Q: Is my data safe? Do you train on my conversations?**
A: **Your data never leaves your server.** All processing happens locally (Ollama) or via your own API keys (OpenAI/Tongyi). No telemetry, no logging to external services, no training on your data. The code is fully open — you can audit every line.

**Q: Can you integrate with an existing app?**
A: Yes. The backend is a standard FastAPI app with REST + WebSocket endpoints. Easy to embed into any existing system.

**Q: Is this like LangChain or CrewAI?**
A: This is a lightweight, self-contained platform that demonstrates the same concepts — multi-agent orchestration, tool calling, streaming — without the framework overhead. ~500 lines of core logic vs. thousands in LangChain. Easy to understand, modify, and extend.

**Q: Can I run multiple models simultaneously?**
A: Yes. The orchestrator can assign different models to different agents (e.g., "Researcher" uses GPT-4, "Summarizer" uses local qwen2.5).

**Q: What happens after delivery?**
A: You get full source code + git history. Each tier includes 2 rounds of revisions. 7 days post-delivery bug-fix support. Premium includes deployment guide. Ongoing feature development available on retainer.

**Q: Can the simulated tools (web search ★, code executor ★) be made real?**
A: Yes — included in the Premium tier:

| Tool | Basic/Standard | Premium |
|------|:---:|:---:|
| Calculator | ✅ Real | ✅ Real |
| Time/Date | ✅ Real | ✅ Real |
| File Reader | ✅ Real | ✅ Real |
| Web Search | ★ Simulated | ✅ Real (SerpAPI) |
| Code Executor | ★ Simulated | ✅ Real (sandboxed subprocess) |

Or I can upgrade just those tools à la carte — message me.

---

## Code Template (Deliverable Preview)

```
ai-workbench/
├── backend/
│   ├── main.py            # FastAPI app + WebSocket + REST
│   ├── llm_client.py      # Multi-model client (Ollama/OpenAI/Tongyi)
│   ├── agent_engine.py    # Multi-agent orchestrator
│   ├── tools.py           # Function Calling tool registry
│   └── requirements.txt
├── frontend/
│   └── index.html         # Single-file three-column workbench
├── docker-compose.yml
├── Dockerfile
└── README.md
```

**Sample `agent_engine.py` (multi-agent orchestrator):**
```python
from dataclasses import dataclass, field
from typing import Any, AsyncIterator
from llm_client import LLMClient, create_client
from tools import BUILTIN_TOOLS, get_tool_schemas, execute_tool

@dataclass
class Agent:
    name: str
    system_prompt: str
    model: str = "qwen2.5:7b"
    provider: str = "ollama"
    tools: list[str] = field(default_factory=list)
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]

class Orchestrator:
    def __init__(self, llm_client: LLMClient = None):
        self.agents: dict[str, Agent] = {}
        self.llm = llm_client or create_client("ollama")

    def add_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    async def chat(self, agent_name: str, user_input: str) -> AsyncIterator[str]:
        agent = self.agents[agent_name]
        agent.messages.append({"role": "user", "content": user_input})
        tools = get_tool_schemas(agent.tools)

        response = self.llm.chat(
            model=agent.model,
            messages=agent.messages,
            tools=tools or None,
            stream=True
        )
        async for chunk in response:
            yield chunk.get("content", "")

    async def execute_tool(self, agent_name: str, tool_name: str, args: dict) -> str:
        return await execute_tool(tool_name, args)

    def list_agents(self) -> list[dict]:
        return [a.to_dict() for a in self.agents.values()]
```
