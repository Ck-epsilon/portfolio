# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Function Calling tool registry for AI Agent Workbench.

Provides a set of built-in tools that AI agents can invoke during
conversation. Each tool has a JSON Schema definition for LLM function
calling and a callable handler.
"""

import datetime
import json
import math
from typing import Any


class Tool:
    """A callable tool with JSON Schema definition for LLM function calling."""

    def __init__(self, name: str, description: str, parameters: dict, handler):
        self.name = name
        self.description = description
        self.parameters = parameters
        self._handler = handler

    @property
    def schema(self) -> dict:
        """Return OpenAI-compatible function definition."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    async def execute(self, **kwargs) -> str:
        """Invoke the tool and return its string result."""
        return await self._handler(**kwargs)


# ---------------------------------------------------------------------------
# Built-in tools
# ---------------------------------------------------------------------------
async def _calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    allowed = set("0123456789+-*/().% eExxpPi inctasrhqldgoubfym")
    cleaned = "".join(c for c in expression if c in allowed)
    if not cleaned:
        return "Invalid expression"
    try:
        result = eval(cleaned, {"__builtins__": {}}, {
            "math": math, "pi": math.pi, "e": math.e,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "pow": math.pow,
        })
        return f"{result}"
    except Exception as e:
        return f"Error: {e}"


async def _get_time(timezone: str = "UTC") -> str:
    """Return the current date and time."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")


async def _web_search(query: str) -> str:
    """Simulated web search. Returns a summary for demo purposes."""
    # In production, this would call a real search API
    return json.dumps({
        "query": query,
        "results": [
            {"title": f"Result for '{query}'", "snippet": f"This is a simulated search result for: {query}. Connect a real search API for live results."}
        ],
        "note": "Simulated search. Connect Tavily/SerpAPI for real results."
    }, ensure_ascii=False)


async def _file_read(path: str) -> str:
    """Read a file from the local filesystem. (Sandboxed for demo.)"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(2000)
        return content + ("..." if len(content) >= 2000 else "")
    except Exception as e:
        return f"Error reading file: {e}"


async def _code_executor(language: str, code: str) -> str:
    """Simulated code execution. Returns sample output."""
    return json.dumps({
        "language": language,
        "code_length": len(code),
        "output": f"[Simulated] Code executed in {language}. In production, run in a sandboxed environment.",
    }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
BUILTIN_TOOLS: dict[str, Tool] = {
    "calculator": Tool(
        name="calculator",
        description="Evaluate a mathematical expression. Supports +,-,*,/,**,sqrt,sin,cos,log,etc.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '2+2*3' or 'sqrt(16)'",
                }
            },
            "required": ["expression"],
        },
        handler=_calculator,
    ),
    "get_time": Tool(
        name="get_time",
        description="Get the current date and time in UTC.",
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone, defaults to UTC",
                    "default": "UTC",
                }
            },
        },
        handler=_get_time,
    ),
    "web_search": Tool(
        name="web_search",
        description="Search the web for information. (Simulated in demo mode.)",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            "required": ["query"],
        },
        handler=_web_search,
    ),
    "file_read": Tool(
        name="file_read",
        description="Read the contents of a local file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                }
            },
            "required": ["path"],
        },
        handler=_file_read,
    ),
    "code_executor": Tool(
        name="code_executor",
        description="Execute code in a specified language. (Simulated in demo mode.)",
        parameters={
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Programming language, e.g. 'python', 'javascript'",
                },
                "code": {
                    "type": "string",
                    "description": "The source code to execute",
                },
            },
            "required": ["language", "code"],
        },
        handler=_code_executor,
    ),
}


def get_tool_schemas(tool_names: list[str]) -> list[dict]:
    """Return OpenAI-compatible function definitions for named tools."""
    return [BUILTIN_TOOLS[name].schema for name in tool_names if name in BUILTIN_TOOLS]


async def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool by name with given arguments."""
    tool = BUILTIN_TOOLS.get(name)
    if not tool:
        return f"Unknown tool: {name}"
    try:
        return await tool.execute(**arguments)
    except Exception as e:
        return f"Tool execution error: {e}"
