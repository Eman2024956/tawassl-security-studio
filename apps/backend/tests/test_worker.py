import pytest
import sys
import os
import tempfile
from apps.backend.app.worker.runner import IsolatedWorker
from apps.backend.app.tools.ast_inspector import inspect_python_source


@pytest.mark.asyncio
async def test_worker_environment_stripping():
    # Set a sensitive dummy key in outer env
    os.environ["GEMINI_API_KEY"] = "secret_key_12345"
    worker = IsolatedWorker()

    # Run python script that prints os.environ.get('GEMINI_API_KEY')
    cmd = [sys.executable, "-c", "import os; print('KEY:', os.environ.get('GEMINI_API_KEY'))"]
    result = await worker.run(cmd)

    assert result.exit_code == 0
    assert "KEY: None" in result.stdout
    assert "secret_key_12345" not in result.stdout


@pytest.mark.asyncio
async def test_worker_timeout_enforcement():
    # Run a sleep command that exceeds 1.0 second timeout
    worker = IsolatedWorker(timeout_seconds=0.5)
    cmd = [sys.executable, "-c", "import time; time.sleep(5)"]
    result = await worker.run(cmd)

    assert result.timeout is True
    assert result.exit_code == -1


@pytest.mark.asyncio
async def test_worker_output_truncation():
    # Generate large output exceeding max buffer of 1000 bytes
    worker = IsolatedWorker(max_output_bytes=500)
    cmd = [sys.executable, "-c", "for i in range(100): print('Line of diagnostic output numbered ' + str(i))"]
    result = await worker.run(cmd)

    assert result.output_truncated is True
    assert "OUTPUT TRUNCATED" in result.stdout


def test_ast_inspector_dangerous_builtins():
    vulnerable_code = """
import subprocess

def process_user_input(cmd, expr):
    # Dangerous eval
    res = eval(expr)
    
    # Dangerous shell=True
    subprocess.run(cmd, shell=True)
    return res
"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(vulnerable_code)
        f.flush()
        temp_path = f.name

    try:
        report = inspect_python_source(temp_path)
        assert report["status"] == "success"
        findings = report["findings"]
        assert len(findings) == 2

        rule_ids = [f["rule_id"] for f in findings]
        assert "python-dangerous-eval" in rule_ids
        assert "python-subprocess-shell-true" in rule_ids
    finally:
        os.remove(temp_path)
