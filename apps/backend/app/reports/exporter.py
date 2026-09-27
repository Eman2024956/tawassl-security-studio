import json
from typing import Dict, Any, List
from datetime import datetime, timezone


def export_markdown_report(
    assessment_data: Dict[str, Any],
    target_data: Dict[str, Any],
    findings_list: List[Dict[str, Any]],
    skipped_tests: List[str]
) -> str:
    """Generates a complete, structured Markdown security assessment report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md = [
        f"# Tawassl Security Studio - Assessment Report",
        f"",
        f"**Assessment Name:** {assessment_data.get('name')}",
        f"**Generated At:** {now}",
        f"**Target:** {target_data.get('name')} ({target_data.get('target_type')})",
        f"**Authorized Scope:** {', '.join(target_data.get('authorized_domains', [])) or 'Offline Source'}",
        f"**Profile:** {assessment_data.get('profile')}",
        f"**AI Provider & Model:** {assessment_data.get('ai_provider')} ({assessment_data.get('model_id')})",
        f"**Run Status:** {assessment_data.get('status')}",
        f"",
        f"---",
        f"",
        f"## 1. Executive Summary & Coverage Notice",
        f"",
        f"> **Important Coverage Limitation:**",
        f"> A report with no findings indicates that **no vulnerabilities were detected by the specific tests executed within the configured limits and budget**.",
        f"> It does not constitute a guarantee that the application or target is free of security vulnerabilities.",
        f"",
        f"- **Requests Made:** {assessment_data.get('requests_made', 0)} / {assessment_data.get('max_requests', 0)} limit",
        f"- **Agent Steps Executed:** {assessment_data.get('steps_taken', 0)} / {assessment_data.get('max_steps', 0)} limit",
        f"- **Tool Invocations:** {assessment_data.get('tool_calls_made', 0)} / {assessment_data.get('max_tool_calls', 0)} limit",
        f"",
        f"---",
        f"",
        f"## 2. Discovered Findings & Evidence",
        f""
    ]

    if not findings_list:
        md.append("No security vulnerabilities or bugs detected within the executed test profile.\n")
    else:
        for idx, f in enumerate(findings_list, 1):
            md.extend([
                f"### {idx}. [{f.get('severity', 'info').upper()}] {f.get('title')}",
                f"",
                f"- **Affected Asset:** `{f.get('affected_asset')}`",
                f"- **Category:** `{f.get('category')}`",
                f"- **Status:** **{f.get('status')}** (Confidence: {f.get('confidence')})",
                f"",
                f"**Preconditions:** {f.get('preconditions') or 'None specified'}",
                f"",
                f"**Reproduction Steps:**",
                f"```",
                f"{f.get('reproduction_steps', '')}",
                f"```",
                f"",
                f"**Expected Result:** {f.get('expected_result')}",
                f"",
                f"**Observed Result:** {f.get('observed_result')}",
                f"",
                f"**Impact:** {f.get('impact') or 'Not specified'}",
                f"",
                f"**Suggested Remediation:**",
                f"{f.get('remediation') or 'Remediation guidance pending review.'}",
                f"",
                f"---",
                f""
            ])

    if skipped_tests:
        md.extend([
            f"## 3. Skipped Tests & Missing Prerequisites",
            f""
        ])
        for skipped in skipped_tests:
            md.append(f"- {skipped}")
        md.append("")

    return "\n".join(md)


def export_json_report(
    assessment_data: Dict[str, Any],
    target_data: Dict[str, Any],
    findings_list: List[Dict[str, Any]],
    skipped_tests: List[str]
) -> Dict[str, Any]:
    """Generates structured JSON assessment report."""
    return {
        "metadata": {
            "application": "Tawassl Security Studio",
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope_notice": "No findings detected by these tests does not imply system is secure."
        },
        "assessment": assessment_data,
        "target": target_data,
        "findings": findings_list,
        "skipped_tests": skipped_tests
    }


def export_sarif_report(
    assessment_data: Dict[str, Any],
    target_data: Dict[str, Any],
    findings_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates OASIS SARIF v2.1.0 formatted report."""
    rules = []
    results = []

    for f in findings_list:
        rule_id = f.get("id", "sec-rule")
        severity = f.get("severity", "medium").lower()
        level = "error" if severity in ("critical", "high") else "warning" if severity == "medium" else "note"

        rules.append({
            "id": rule_id,
            "name": f.get("title"),
            "shortDescription": {"text": f.get("title")},
            "fullDescription": {"text": f.get("observed_result")},
            "defaultConfiguration": {"level": level}
        })

        results.append({
            "ruleId": rule_id,
            "level": level,
            "message": {"text": f.get("observed_result")},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": f.get("affected_asset", "unknown")}
                    }
                }
            ]
        })

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Tawassl Security Studio",
                        "version": "0.1.0",
                        "rules": rules
                    }
                },
                "results": results
            }
        ]
    }
