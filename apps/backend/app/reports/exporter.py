import json
import hashlib
from typing import Dict, Any, List
from datetime import datetime, timezone

STANDARD_LIMITATION_NOTICE = "No confirmed vulnerabilities were identified by the tests executed within this assessment scope."


def deduplicate_findings(findings_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates findings using (target + path + category + evidence hash) or (affected_asset, category, title).
    Preserves the latest entry.
    """
    seen = set()
    unique = []
    for f in findings_list:
        ev_hash = f.get("evidence_hash")
        asset = f.get("affected_asset", "")
        cat = f.get("category", "")
        title = f.get("title", "")
        key = (asset, cat, ev_hash if ev_hash else title)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def classify_results(findings_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Separates results into:
      1. passed_control
      2. observation
      3. finding (only confirmed security vulnerabilities)
      4. inconclusive
    Enforces:
      - Only confirmed security vulnerabilities belong in 'Confirmed Security Findings' (confirmed_vulnerability=True).
      - INFO observations must NOT count as vulnerabilities/findings.
    """
    confirmed_findings = []
    observations = []
    passed_controls = []
    inconclusive_tests = []

    for f in findings_list:
        rtype = f.get("result_type")
        has_explicit_vuln = "confirmed_vulnerability" in f
        is_vuln = bool(f.get("confirmed_vulnerability", False))
        sev = str(f.get("severity", "info")).lower()
        status = str(f.get("status", "")).lower()

        if rtype == "passed_control" or status in ("passed_control", "pass"):
            passed_controls.append(f)
        elif rtype == "inconclusive" or status == "inconclusive":
            inconclusive_tests.append(f)
        elif rtype == "observation" or sev == "info":
            # INFO observations must NOT count as vulnerabilities/findings
            observations.append(f)
        elif has_explicit_vuln:
            if is_vuln and sev != "info":
                confirmed_findings.append(f)
            else:
                observations.append(f)
        else:
            # Fallback for legacy dicts: confirmed and non-info severity
            if status in ("confirmed", "suspected") and sev in ("critical", "high", "medium", "low"):
                confirmed_findings.append(f)
            else:
                observations.append(f)

    return {
        "finding": confirmed_findings,
        "observation": observations,
        "passed_control": passed_controls,
        "inconclusive": inconclusive_tests
    }


def export_markdown_report(
    assessment_data: Dict[str, Any],
    target_data: Dict[str, Any],
    findings_list: List[Dict[str, Any]],
    skipped_tests: List[str]
) -> str:
    """Generates a complete, structured Markdown security assessment report with 4 discrete sections."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    findings_list = deduplicate_findings(findings_list)
    classified = classify_results(findings_list)

    confirmed_vulns = classified["finding"]
    observations = classified["observation"]
    passed_controls = classified["passed_control"]
    inconclusive_tests = classified["inconclusive"]

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
        f"## 1. Executive Summary & Important Coverage Limitation",
        f"",
        f"> **Coverage Notice:**",
        f"> {STANDARD_LIMITATION_NOTICE}",
        f"> A report with no findings indicates that no vulnerabilities were detected by the specific tests executed within the configured limits and budget.",
        f"> It does not certify that the application is completely secure.",
        f"",
        f"### Result Breakdown Summary:",
        f"- **Confirmed Vulnerabilities:** {len(confirmed_vulns)}",
        f"- **Security Observations:** {len(observations)}",
        f"- **Passed Controls:** {len(passed_controls)}",
        f"- **Inconclusive Tests:** {len(inconclusive_tests)}",

        f"",
        f"- **Requests Made:** {assessment_data.get('requests_made', 0)} / {assessment_data.get('max_requests', 0)} budget limit",
        f"- **Agent Steps Executed:** {assessment_data.get('steps_taken', 0)} / {assessment_data.get('max_steps', 0)} limit",
        f"- **Tool Invocations:** {assessment_data.get('tool_calls_made', 0)} / {assessment_data.get('max_tool_calls', 0)} limit",
        f"",
        f"---",
        f"",
        f"## 2. Confirmed Security Findings ({len(confirmed_vulns)})",
        f""
    ]

    if not confirmed_vulns:
        md.append(f"> {STANDARD_LIMITATION_NOTICE}\n")
    else:
        for idx, f in enumerate(confirmed_vulns, 1):
            md.extend([
                f"### {idx}. [{f.get('severity', 'info').upper()}] {f.get('title')}",
                f"",
                f"- **Affected Asset:** `{f.get('affected_asset')}`",
                f"- **Category:** `{f.get('category')}`",
                f"- **Result Type:** `finding` (Confirmed Vulnerability: Yes)",
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

    md.extend([
        f"## 3. Security Observations ({len(observations)})",
        f""
    ])
    if not observations:
        md.append("No informational observations recorded.\n")
    else:
        for idx, f in enumerate(observations, 1):
            md.extend([
                f"### {idx}. [OBSERVATION / {f.get('severity', 'info').upper()}] {f.get('title')}",
                f"",
                f"- **Affected Asset:** `{f.get('affected_asset')}`",
                f"- **Category:** `{f.get('category')}`",
                f"- **Result Type:** `observation` (Confirmed Vulnerability: No)",
                f"- **Observed Behavior:** {f.get('observed_result')}",
                f"- **Context & Note:** {f.get('impact') or 'Informational reconnaissance detail. Does not represent a vulnerability.'}",
                f"",
                f"---",
                f""
            ])

    md.extend([
        f"## 4. Passed Controls ({len(passed_controls)})",
        f""
    ])
    if not passed_controls:
        md.append("No passed controls recorded.\n")
    else:
        for idx, f in enumerate(passed_controls, 1):
            md.extend([
                f"- **[PASSED]** `{f.get('title')}` on `{f.get('affected_asset')}`: {f.get('observed_result')}"
            ])
        md.append("")

    if inconclusive_tests:
        md.extend([
            f"## 5. Inconclusive Tests ({len(inconclusive_tests)})",
            f""
        ])
        for idx, f in enumerate(inconclusive_tests, 1):
            md.extend([
                f"- **[INCONCLUSIVE]** `{f.get('title')}`: {f.get('observed_result')}"
            ])
        md.append("")

    if skipped_tests:
        md.extend([
            f"## 6. Skipped Tests & Missing Prerequisites",
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
    """Generates structured JSON assessment report with distinct summary categories."""
    findings_list = deduplicate_findings(findings_list)
    classified = classify_results(findings_list)

    return {
        "metadata": {
            "application": "Tawassl Security Studio",
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope_notice": STANDARD_LIMITATION_NOTICE
        },
        "summary": {
            "confirmed_vulnerabilities": len(classified["finding"]),
            "security_observations": len(classified["observation"]),
            "passed_controls": len(classified["passed_control"]),
            "inconclusive_tests": len(classified["inconclusive"])
        },
        "assessment": assessment_data,
        "target": target_data,
        "results": {
            "confirmed_vulnerabilities": classified["finding"],
            "security_observations": classified["observation"],
            "passed_controls": classified["passed_control"],
            "inconclusive_tests": classified["inconclusive"]
        },
        "findings": findings_list,
        "skipped_tests": skipped_tests
    }


def export_sarif_report(
    assessment_data: Dict[str, Any],
    target_data: Dict[str, Any],
    findings_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates OASIS SARIF v2.1.0 formatted report with strict rule levels."""
    findings_list = deduplicate_findings(findings_list)
    classified = classify_results(findings_list)
    rules = []
    results = []

    # Findings (vulnerabilities) mapped to error/warning
    for f in classified["finding"]:
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

    # Observations mapped to note level
    for f in classified["observation"]:
        rule_id = f.get("id", "sec-rule")
        level = "note"

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
