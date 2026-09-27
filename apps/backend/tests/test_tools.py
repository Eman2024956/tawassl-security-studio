import pytest
import os
import tempfile
from apps.backend.app.tools.patch_engine import generate_unified_diff, apply_patch_with_backup, revert_patch
from apps.backend.app.tools.secret_scanner import scan_file_for_secrets


def test_unified_diff_generation():
    orig = "def hello():\n    return 'world'\n"
    mod = "def hello():\n    return 'tawassl security'\n"
    diff = generate_unified_diff(orig, mod, filename="test.py")
    assert "--- a/test.py" in diff
    assert "+++ b/test.py" in diff
    assert "-    return 'world'" in diff
    assert "+    return 'tawassl security'" in diff


def test_patch_apply_and_revert():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("X = 1\n")
        f.flush()
        temp_path = f.name

    try:
        # Apply patch
        patch_res = apply_patch_with_backup(temp_path, "X = 2\n")
        assert patch_res["status"] == "patched"
        assert os.path.exists(patch_res["backup"])

        with open(temp_path) as f:
            assert f.read() == "X = 2\n"

        # Revert patch
        revert_res = revert_patch(temp_path)
        assert revert_res["status"] == "reverted"
        assert not os.path.exists(patch_res["backup"])

        with open(temp_path) as f:
            assert f.read() == "X = 1\n"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_secret_scanner_detection():
    source_with_keys = """
AWS_KEY = "AKIA1234567890ABCDEF"
GH_TOKEN = "ghp_123456789012345678901234567890123456"
"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(source_with_keys)
        f.flush()
        temp_path = f.name

    try:
        findings = scan_file_for_secrets(temp_path)
        assert len(findings) >= 2
        rule_names = [f["rule_name"] for f in findings]
        assert "AWS Access Key" in rule_names
        assert "GitHub Personal Access Token" in rule_names
    finally:
        os.remove(temp_path)
