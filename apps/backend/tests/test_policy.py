import pytest
import tempfile
import os
from apps.backend.app.policy.models import ScopeRule
from apps.backend.app.policy.engine import PolicyEngine
from apps.backend.app.policy.network_guard import is_ip_forbidden, validate_url_against_scope
from apps.backend.app.policy.workspace_guard import validate_workspace_path
from apps.backend.app.api.approvals import compute_proposal_hash
from apps.backend.app.core.security import redact_secrets


def test_empty_scope_denies_access():
    empty_scope = ScopeRule(authorized_domains=[], base_urls=[])
    engine = PolicyEngine(empty_scope)
    result = engine.evaluate_url("https://example.com/api")
    assert not result.allowed
    assert result.violation_code == "EMPTY_SCOPE_DENY"


def test_ssrf_prohibited_ips():
    forbidden, reason = is_ip_forbidden("127.0.0.1")
    assert forbidden
    assert "Loopback" in reason

    forbidden, reason = is_ip_forbidden("169.254.169.254")
    assert forbidden
    assert "metadata" in reason

    forbidden, reason = is_ip_forbidden("10.0.1.50")
    assert forbidden
    assert "private" in reason

    forbidden, reason = is_ip_forbidden("192.168.1.1")
    assert forbidden

    forbidden, reason = is_ip_forbidden("8.8.8.8")
    assert not forbidden


def test_suffix_trick_prevention():
    scope = ScopeRule(
        authorized_domains=["matami.tawassl.com"],
        allow_subdomains=False,
        allowed_ports=[80, 443]
    )
    # Suffix attack domain (attacker-controlled domain that ends with the target name)
    result = validate_url_against_scope("https://matami.tawassl.com.evil.com", scope)
    assert not result.allowed
    assert result.violation_code == "HOSTNAME_OUT_OF_SCOPE"


def test_userinfo_confusion_prevention():
    scope = ScopeRule(
        authorized_domains=["matami.tawassl.com"],
        allowed_ports=[80, 443]
    )
    result = validate_url_against_scope("https://matami.tawassl.com@evil.com", scope)
    assert not result.allowed
    assert result.violation_code == "USERINFO_PROHIBITED"


def test_port_restriction_enforcement():
    scope = ScopeRule(
        authorized_domains=["example.com"],
        allowed_ports=[443]
    )
    # Port 22 should be denied
    result = validate_url_against_scope("https://example.com:22/test", scope)
    assert not result.allowed
    assert result.violation_code == "PORT_NOT_PERMITTED"


def test_workspace_escape_prevention():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid file inside tmpdir
        safe_file = os.path.join(tmpdir, "app.py")
        with open(safe_file, "w") as f:
            f.write("# safe code")

        # 1. Safe access inside tmpdir
        res_safe = validate_workspace_path("app.py", tmpdir)
        assert res_safe.allowed

        # 2. Path traversal attempt (../../etc/passwd)
        res_traversal = validate_workspace_path("../../etc/passwd", tmpdir)
        assert not res_traversal.allowed
        assert res_traversal.violation_code == "WORKSPACE_ESCAPE_DETECTED"

        # 3. Direct sensitive host path access
        res_sensitive = validate_workspace_path("/etc/passwd", tmpdir)
        assert not res_sensitive.allowed
        assert res_sensitive.violation_code in ("WORKSPACE_ESCAPE_DETECTED", "SENSITIVE_HOST_PATH_DENIED")

        # 4. Null-byte injection check
        res_null = validate_workspace_path("app.py\x00.exe", tmpdir)
        assert not res_null.allowed
        assert res_null.violation_code == "NULL_BYTE_INJECTION"


def test_proposal_hash_integrity():
    args_1 = {"url": "https://example.com/api", "timeout": 10}
    args_2 = {"url": "https://example.com/api", "timeout": 20}  # Modified argument

    hash_1 = compute_proposal_hash("assess-1", "controlled_http", args_1)
    hash_2 = compute_proposal_hash("assess-1", "controlled_http", args_2)

    # Any argument change produces a different SHA-256 hash
    assert hash_1 != hash_2

    # Deterministic calculation produces identical hash
    hash_1_repeat = compute_proposal_hash("assess-1", "controlled_http", args_1)
    assert hash_1 == hash_1_repeat


def test_secret_redaction():
    text_with_token = "Request sent with Bearer ya29.a0AfH6SMBxyz1234567890abcdef and password='SuperSecretPassword123!'"
    redacted = redact_secrets(text_with_token)
    assert "ya29.a0AfH6SMB" not in redacted
    assert "[REDACTED_TOKEN]" in redacted
    assert "SuperSecretPassword123!" not in redacted
    assert "[REDACTED_PASSWORD]" in redacted


def test_mock_domain_alias_resolution():
    scope = ScopeRule(
        authorized_domains=["staging.acme.local"],
        base_urls=["http://staging.acme.local:8080"],
        allowed_ports=[80, 443, 8080]
    )
    result = validate_url_against_scope("http://staging.acme.local:8080/dashboard", scope)
    assert result.allowed
    assert "passes SSRF/DNS security checks" in result.reason
