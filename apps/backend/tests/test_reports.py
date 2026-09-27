import pytest
from apps.backend.app.reports.exporter import export_markdown_report, export_json_report, export_sarif_report

MOCK_ASSESS = {
    "id": "assess-rep-1",
    "name": "Audit Run #1",
    "profile": "observe",
    "status": "completed",
    "ai_provider": "mock",
    "model_id": "mock-sec-v1",
    "requests_made": 5,
    "max_requests": 50,
    "steps_taken": 3,
    "max_steps": 20,
    "tool_calls_made": 2,
    "max_tool_calls": 30
}

MOCK_TARGET = {
    "name": "Matami Tawassl Web App",
    "target_type": "website",
    "authorized_domains": ["matami.tawassl.com"]
}

MOCK_FINDINGS = [
    {
        "id": "find-1",
        "title": "Missing HSTS Header",
        "category": "web_security",
        "affected_asset": "https://matami.tawassl.com",
        "severity": "medium",
        "confidence": "confirmed",
        "status": "confirmed",
        "reproduction_steps": "GET / HTTP/1.1",
        "expected_result": "Strict-Transport-Security header present",
        "observed_result": "Header missing",
        "remediation": "Add HSTS header"
    }
]


def test_markdown_report_generation():
    md = export_markdown_report(MOCK_ASSESS, MOCK_TARGET, MOCK_FINDINGS, ["mod-ssrf"])
    assert "Tawassl Security Studio - Assessment Report" in md
    assert "Important Coverage Limitation" in md
    assert "Missing HSTS Header" in md
    assert "mod-ssrf" in md


def test_json_report_generation():
    json_data = export_json_report(MOCK_ASSESS, MOCK_TARGET, MOCK_FINDINGS, [])
    assert json_data["metadata"]["application"] == "Tawassl Security Studio"
    assert len(json_data["findings"]) == 1
    assert json_data["assessment"]["id"] == "assess-rep-1"


def test_sarif_report_generation():
    sarif = export_sarif_report(MOCK_ASSESS, MOCK_TARGET, MOCK_FINDINGS)
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "Tawassl Security Studio"
    assert len(run["results"]) == 1
    assert run["results"][0]["ruleId"] == "find-1"
    assert run["results"][0]["level"] == "warning"  # medium maps to warning
