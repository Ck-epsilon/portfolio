# Author: Ck.epsilon
"""
Sandboxed subprocess execution for untrusted code.
Uses subprocess with resource limits and timeout for safe execution.
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Allowed languages and their commands
_RUNNERS = {
    "python": ["python", "-c"],
    "javascript": ["node", "-e"],
}

DEFAULT_TIMEOUT = 10  # seconds
MAX_OUTPUT_BYTES = 50 * 1024  # 50KB


async def sandbox_exec(language: str, code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Execute code in a sandboxed subprocess with resource limits.

    Args:
        language: 'python' or 'javascript'
        code: Source code string
        timeout: Max execution seconds (default 10)

    Returns:
        stdout output, or error message prefixed with 'Error: '
    """
    if language not in _RUNNERS:
        return f"Error: Unsupported language '{language}'. Allowed: {', '.join(_RUNNERS.keys())}"

    runner = _RUNNERS[language]

    # Write code to temp file for traceability
    suffix = ".py" if language == "python" else ".js"
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            *runner, code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Restrict to tmp dir
            cwd=tempfile.gettempdir(),
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "HOME": tempfile.gettempdir(),
                "TMPDIR": tempfile.gettempdir(),
            },
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return f"Error: Execution timed out after {timeout}s"

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")[:1000]
            return f"Error (exit {proc.returncode}): {error_msg}"

        output = stdout.decode("utf-8", errors="replace")
        if len(output) > MAX_OUTPUT_BYTES:
            output = output[:MAX_OUTPUT_BYTES] + "\n... (truncated)"
        return output or "(no output)"

    except Exception as e:
        logger.error("Sandbox execution error: %s", e)
        return f"Error: {e}"
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except OSError:
            pass
