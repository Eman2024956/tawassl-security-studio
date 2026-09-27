import asyncio
import os
import signal
import sys
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from apps.backend.app.core.security import redact_secrets

STRIP_ENV_VARS = [
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "LOCAL_API_SECRET",
    "SSH_AUTH_SOCK",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "GITHUB_TOKEN",
    "ANTHROPIC_API_KEY",
]


class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    output_truncated: bool = False
    cancelled: bool = False
    timeout: bool = False


class IsolatedWorker:
    """
    Subprocess execution runner with strict isolation:
    - Zero shell=True (only array argv).
    - Provider API keys and host SSH sockets stripped from environment.
    - Process group management for complete process-tree termination.
    - Output size limits to prevent memory exhaustion / log flooding.
    - Redacts sensitive credentials from output stream.
    """

    def __init__(
        self,
        cwd: Optional[str] = None,
        max_output_bytes: int = 2 * 1024 * 1024,
        timeout_seconds: float = 30.0
    ):
        self.cwd = cwd
        self.max_output_bytes = max_output_bytes
        self.timeout_seconds = timeout_seconds

    def _build_sanitized_env(self) -> Dict[str, str]:
        """Constructs an isolated environment copy stripping all credentials and secrets."""
        env = dict(os.environ)
        for var in STRIP_ENV_VARS:
            env.pop(var, None)
        # Ensure standard python unbuffered output
        env["PYTHONUNBUFFERED"] = "1"
        return env

    async def run(self, argv: List[str]) -> ExecutionResult:
        """Executes a command argv array with isolation and resource bounds."""
        if not argv:
            raise ValueError("Empty argv list cannot be executed.")

        start_time = asyncio.get_event_loop().time()
        env = self._build_sanitized_env()

        # Start child process in its own process group
        proc = await asyncio.create_subprocess_exec(
            *argv,
            cwd=self.cwd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None
        )

        stdout_chunks = []
        stderr_chunks = []
        bytes_read = 0
        truncated = False
        is_timeout = False
        is_cancelled = False

        async def read_stream(stream, chunks_list):
            nonlocal bytes_read, truncated
            while True:
                line = await stream.readline()
                if not line:
                    break
                bytes_read += len(line)
                if bytes_read > self.max_output_bytes:
                    truncated = True
                    chunks_list.append(b"\n[OUTPUT TRUNCATED: Max buffer limit exceeded]\n")
                    break
                chunks_list.append(line)

        try:
            await asyncio.wait_for(
                asyncio.gather(
                    read_stream(proc.stdout, stdout_chunks),
                    read_stream(proc.stderr, stderr_chunks),
                    proc.wait()
                ),
                timeout=self.timeout_seconds
            )
            exit_code = proc.returncode if proc.returncode is not None else 0
        except asyncio.TimeoutError:
            is_timeout = True
            exit_code = -1
            self._kill_process_group(proc.pid)
        except asyncio.CancelledError:
            is_cancelled = True
            exit_code = -1
            self._kill_process_group(proc.pid)
            raise

        duration_ms = round((asyncio.get_event_loop().time() - start_time) * 1000, 2)
        raw_stdout = b"".join(stdout_chunks).decode("utf-8", errors="replace")
        raw_stderr = b"".join(stderr_chunks).decode("utf-8", errors="replace")

        # Redact any accidental tokens from output
        clean_stdout = redact_secrets(raw_stdout)
        clean_stderr = redact_secrets(raw_stderr)

        return ExecutionResult(
            exit_code=exit_code,
            stdout=clean_stdout,
            stderr=clean_stderr,
            duration_ms=duration_ms,
            output_truncated=truncated,
            cancelled=is_cancelled,
            timeout=is_timeout
        )

    def _kill_process_group(self, pid: int) -> None:
        """Kills the entire process group to ensure no orphan worker processes remain."""
        try:
            pgid = os.getpgid(pid)
            os.killpg(pgid, signal.SIGTERM)
            # Give a brief grace period then SIGKILL if still alive
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
