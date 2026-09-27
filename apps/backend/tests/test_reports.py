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


def test_four_result_types_classification():
    from apps.backend.app.reports.exporter import classify_results

    mixed_results = [
        {
            "id": "c1",
            "title": "CORS Origin Rejection Enforced",
            "category": "web_security",
            "affected_asset": "https://matami.tawassl.com",
            "severity": "info",
            "status": "confirmed",
            "result_type": "passed_control",
            "confirmed_vulnerability": False
        },
        {
            "id": "o1",
            "title": "SPA Fallback on /.env",
            "category": "web_security",
            "affected_asset": "https://matami.tawassl.com/.env",
            "severity": "info",
            "status": "observation",
            "result_type": "observation",
            "confirmed_vulnerability": False
        },
        {
            "id": "v1",
            "title": "Open Redirect via Query Parameter",
            "category": "web_security",
            "affected_asset": "https://matami.tawassl.com/?redirect=https://evil.example",
            "severity": "high",
            "status": "confirmed",
            "result_type": "finding",
            "confirmed_vulnerability": True
        },
        {
            "id": "i1",
            "title": "Rate Limit Resilience",
            "category": "api_security",
            "affected_asset": "https://matami.tawassl.com/api",
            "severity": "low",
            "status": "inconclusive",
            "result_type": "inconclusive",
            "confirmed_vulnerability": False
        }
    ]

    classified = classify_results(mixed_results)
    assert len(classified["passed_control"]) == 1
    assert len(classified["observation"]) == 1
    assert len(classified["finding"]) == 1
    assert len(classified["inconclusive"]) == 1

    # Ensure INFO observations do NOT count as vulnerabilities
    assert classified["finding"][0]["id"] == "v1"
    assert classified["finding"][0]["confirmed_vulnerability"] is True


def test_report_summary_four_categories_and_exact_phrasing():
    mixed_results = [
        {
            "id": "c1",
            "title": "HTTP Redirection Enforced",
            "category": "web_security",
            "affected_asset": "http://matami.tawassl.com",
            "severity": "info",
            "result_type": "passed_control",
            "confirmed_vulnerability": False,
            "observed_result": "Redirects to HTTPS"
        },
        {
            "id": "o1",
            "title": "SPA Fallback on Unknown Routes",
            "category": "web_security",
            "affected_asset": "https://matami.tawassl.com/.env",
            "severity": "info",
            "result_type": "observation",
            "confirmed_vulnerability": False,
            "observed_result": "200 with HTML"
        }
    ]

    # Zero confirmed vulnerabilities case
    md = export_markdown_report(MOCK_ASSESS, MOCK_TARGET, mixed_results, [])
    # Must use required phrase: "No confirmed vulnerabilities were identified by the tests executed within this assessment scope."
    assert "No confirmed vulnerabilities were identified by the tests executed within this assessment scope." in md
    # Never claim "site is secure"
    assert "site is secure" not in md.lower()

    # Must separately show the 4 categories
    assert "**Confirmed Vulnerabilities:** 0" in md
    assert "**Security Observations:** 1" in md
    assert "**Passed Controls:** 1" in md
    assert "**Inconclusive Tests:** 0" in md


    # JSON report check
    json_data = export_json_report(MOCK_ASSESS, MOCK_TARGET, mixed_results, [])
    assert json_data["summary"]["confirmed_vulnerabilities"] == 0
    assert json_data["summary"]["security_observations"] == 1
    assert json_data["summary"]["passed_controls"] == 1
    assert json_data["summary"]["inconclusive_tests"] == 0
    assert json_data["metadata"]["scope_notice"] == "No confirmed vulnerabilities were identified by the tests executed within this assessment scope."


def test_deduplication_by_target_path_category_evidence_hash():
    from apps.backend.app.reports.exporter import deduplicate_findings

    dups = [
        {
            "id": "1",
            "affected_asset": "https://matami.tawassl.com/.env",
            "category": "web_security",
            "evidence_hash": "hash-abc-123",
            "title": "SPA Fallback",
            "result_type": "observation"
        },
        {
            "id": "2",
            "affected_asset": "https://matami.tawassl.com/.env",
            "category": "web_security",
            "evidence_hash": "hash-abc-123",
            "title": "SPA Fallback",
            "result_type": "observation"
        }
    ]

    unique = deduplicate_findings(dups)
    assert len(unique) == 1
    assert unique[0]["id"] == "1"


def test_target_metadata_in_reports():
    live_target = {
        "name": "Matami Tawassl Production",
        "target_type": "website",
        "environment_mode": "live",
        "authorized_domains": ["matami.tawassl.com"],
        "base_urls": ["https://matami.tawassl.com"]
    }
    mock_target = {
        "name": "Demo Sandbox",
        "target_type": "website",
        "environment_mode": "mock",
        "authorized_domains": ["demo.mock-target.local"],
        "base_urls": ["https://demo.mock-target.local"]
    }

    # 1. Live target report metadata
    live_md = export_markdown_report(MOCK_ASSESS, live_target, [], [])
    assert "- **Target Type:** LIVE" in live_md
    assert "- **Target URL:** https://matami.tawassl.com" in live_md
    assert "- **Authorization Status:** Authorized & Scope Verified" in live_md
    assert "- **Network Mode:** Real HTTP Requests" in live_md
    assert "- **AI Provider:** Mock Rule Engine (Simulated Analysis)" in live_md
    assert "mock-sec-v1" not in live_md  # Never presented as real AI model

    # 2. Mock target report metadata & simulation notice
    mock_md = export_markdown_report(MOCK_ASSESS, mock_target, [], [])
    assert "- **Target Type:** MOCK" in mock_md
    assert "- **Network Mode:** Simulated" in mock_md
    assert "SIMULATION RUN NOTICE" in mock_md

    # 3. JSON metadata verification
    live_json = export_json_report(MOCK_ASSESS, live_target, [], [])
    assert live_json["metadata"]["target_type"] == "LIVE"
    assert live_json["metadata"]["network_mode"] == "Real HTTP Requests"
    assert live_json["metadata"]["authorization_status"] == "Authorized & Scope Verified"
    assert live_json["metadata"]["ai_provider"] == "Mock Rule Engine (Simulated Analysis)"

    mock_json = export_json_report(MOCK_ASSESS, mock_target, [], [])
    assert mock_json["metadata"]["target_type"] == "MOCK"
    assert mock_json["metadata"]["network_mode"] == "Simulated"
    assert mock_json["metadata"]["simulation_notice"] is not None

