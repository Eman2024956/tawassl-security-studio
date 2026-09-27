import pytest
from apps.backend.app.policy.sensitive_detector import (
    classify_sensitive_file_response,
    parse_dotenv_evidence,
    is_html_or_spa_response,
    redact_dotenv_declaration
)
from apps.backend.app.reports.exporter import classify_results, export_markdown_report


# 1. 200 HTML SPA fallback
def test_200_html_spa_fallback():
    headers = {"content-type": "text/html; charset=utf-8"}
    body = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Matami Portal</title>
  </head>
  <body>
    <div id="root"></div>
    <script src="/static/js/bundle.js"></script>
  </body>
</html>"""
    root_body = body  # Same template as root /

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=200,
        headers=headers,
        body=body,
        root_body=root_body
    )

    assert res.result_type == "observation"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert res.spa_detected is True
    assert res.html_detected is True
    assert "Single Page Application (SPA) HTML Fallback" in res.title
    assert "rotate disclosed secrets" not in (res.remediation or "")


# 2. 200 login page
def test_200_login_page():
    headers = {"content-type": "text/html"}
    body = """<!DOCTYPE html>
<html>
  <head><title>Sign In - Authentication</title></head>
  <body>
    <h2>User Login</h2>
    <form action="/api/login" method="POST">
      <input type="text" name="username" placeholder="Username" />
      <input type="password" name="password" placeholder="Password" />
      <button type="submit">Sign In</button>
    </form>
  </body>
</html>"""

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=200,
        headers=headers,
        body=body
    )

    assert res.result_type == "observation"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert res.html_detected is True
    assert "Authentication Portal Rendered" in res.title
    assert res.remediation is None


# 3. 200 custom 404 HTML
def test_200_custom_404_html():
    headers = {"content-type": "text/html"}
    body = """<!DOCTYPE html>
<html>
  <head><title>404 - Page Not Found</title></head>
  <body>
    <h1>404 Not Found</h1>
    <p>The requested page could not be found on this server.</p>
  </body>
</html>"""

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=200,
        headers=headers,
        body=body
    )

    assert res.result_type == "passed_control"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert res.html_detected is True
    assert "Custom 404 HTML" in res.title
    assert res.remediation is None


# 4. 403 Forbidden
def test_403_forbidden():
    headers = {"content-type": "text/plain"}
    body = "Forbidden: Access denied to dotfiles."

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=403,
        headers=headers,
        body=body
    )

    assert res.result_type == "passed_control"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert "Protected" in res.title
    assert res.remediation is None


# 5. 404 Not Found
def test_404_not_found():
    headers = {"content-type": "text/plain"}
    body = "404 Not Found"

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=404,
        headers=headers,
        body=body
    )

    assert res.result_type == "passed_control"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert "Protected" in res.title
    assert res.remediation is None


# 6. Genuine .env plaintext
def test_genuine_env_plaintext():
    headers = {"content-type": "text/plain"}
    body = """# Database Configuration
DATABASE_URL=postgres://app_user:SuperSecretP@ss123@prod-db.internal:5432/tawassl_prod
API_KEY=sample_test_key_prod_abcdef1234567890
SECRET_KEY=9b08f4c28e6e5a4d3c2b1a0f
APP_ENV=production
"""

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=200,
        headers=headers,
        body=body
    )

    assert res.result_type == "finding"
    assert res.confirmed_vulnerability is True
    assert res.sensitive_file_content_verified is True
    assert res.verified_variable_count == 4
    assert res.severity == "critical"
    assert "Exposed Sensitive Environment File" in res.title

    # Never include actual secret values in reports/logs. Redact values!
    assert "SuperSecretP@ss123" not in res.observed_result
    assert "sample_test_key_prod_abcdef1234567890" not in res.observed_result
    assert "DATABASE_URL=[REDACTED]" in res.observed_result
    assert "API_KEY=[REDACTED]" in res.observed_result

    # Remediation must be present for confirmed disclosure
    assert "rotate all disclosed credentials" in res.remediation.lower()


# 7. HTML containing strings like API_KEY=example
def test_html_containing_config_looking_strings():
    headers = {"content-type": "text/html; charset=utf-8"}
    body = """<!DOCTYPE html>
<html>
  <head>
    <title>Developer Documentation</title>
  </head>
  <body>
    <h1>API Guide</h1>
    <p>Set your key as follows:</p>
    <code>API_KEY=example_demo_key</code>
    <code>DATABASE_URL=localhost:5432</code>
  </body>
</html>"""

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=200,
        headers=headers,
        body=body
    )

    # Must NOT assume .env exposure simply because HTML contains API_KEY= or DATABASE_URL=
    assert res.result_type == "observation"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert res.verified_variable_count == 0
    assert "rotate disclosed secrets" not in (res.remediation or "")


# 8. JS bundle containing KEY=value
def test_js_bundle_containing_assignments():
    headers = {"content-type": "application/javascript"}
    body = """var a = 1; window.API_KEY = "test"; function init() { const KEY = "value"; return KEY; }"""

    res = classify_sensitive_file_response(
        path="/.env",
        status_code=200,
        headers=headers,
        body=body
    )

    assert res.result_type == "inconclusive"
    assert res.confirmed_vulnerability is False
    assert res.sensitive_file_content_verified is False
    assert "rotate disclosed secrets" not in (res.remediation or "")


# 9. Test Evidence Parser variable count integrity and redaction
def test_evidence_parser_integrity():
    body = """
# Comments should be ignored
DATABASE_URL="postgres://user:pass@db:5432/app"
API_KEY='sample_test_key_123456789'
PORT=8000
INVALID LINE WITH NO ASSIGNMENT
<div id="not_dotenv">hello</div>
"""
    raw_keys, redacted = parse_dotenv_evidence(body)
    assert raw_keys == ["DATABASE_URL", "API_KEY", "PORT"]
    assert len(redacted) == 3
    assert redacted[0] == "DATABASE_URL=[REDACTED]"
    assert redacted[1] == "API_KEY=[REDACTED]"
    assert redacted[2] == "PORT=[REDACTED]"


# 10. Test Classification filter in Exporter requires sensitive_file_content_verified = True
def test_exporter_rejects_unverified_dotenv_findings():
    fake_finding = {
        "id": "f-fake-env",
        "title": "Exposed Sensitive Environment File (/.env)",
        "category": "web_security",
        "affected_asset": "https://matami.tawassl.com/.env",
        "severity": "critical",
        "status": "confirmed",
        "result_type": "finding",
        "confirmed_vulnerability": True,
        "sensitive_file_content_verified": False,  # NOT VERIFIED!
        "observed_result": "HTTP 200 HTML returned",
        "remediation": "Rotate disclosed secrets"
    }

    classified = classify_results([fake_finding])
    # Must NOT be in finding because sensitive_file_content_verified is False
    assert len(classified["finding"]) == 0
    assert len(classified["observation"]) == 1
