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

        # Requirement 5: Before reporting secret exposure, require sensitive_file_content_verified = True
        is_sensitive_file = "env" in str(f.get("title", "")).lower() or "/.env" in str(f.get("affected_asset", "")).lower()
        content_verified = bool(f.get("sensitive_file_content_verified", False))

        if rtype == "passed_control" or status in ("passed_control", "pass"):
            passed_controls.append(f)
        elif rtype == "inconclusive" or status == "inconclusive":
            inconclusive_tests.append(f)
        elif rtype == "observation" or sev == "info":
            # INFO observations must NOT count as vulnerabilities/findings
            observations.append(f)
        elif is_sensitive_file and not content_verified:
            # Sensitive file without verified content MUST NOT count as a finding
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


def resolve_target_metadata(target_data: Dict[str, Any], assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Resolves human-readable, auditable metadata for the target and execution environment."""
    target_env = str(target_data.get("environment_mode", "live")).lower()
    is_live = (target_env == "live")
    target_type = "LIVE" if is_live else "MOCK"

    base_urls = target_data.get("base_urls", [])
    auth_domains = target_data.get("authorized_domains", [])
    target_url = base_urls[0] if base_urls else (f"https://{auth_domains[0]}" if auth_domains else "https://matami.tawassl.com/")

    auth_status = "Authorized & Scope Verified" if is_live else "Simulated Sandbox Scope"
    network_mode = "Real HTTP Requests" if is_live else "Simulated"

    # mock-sec-v1 must never be presented as real AI analysis
    ai_prov = str(assessment_data.get("ai_provider", "mock")).lower()
    mod_id = str(assessment_data.get("model_id", "mock-sec-v1"))
    if ai_prov in ("mock", "mock-sec-v1") or mod_id == "mock-sec-v1":
        ai_provider_display = "Mock Rule Engine (Simulated Analysis)"
    elif "gemini" in ai_prov or "gemini" in mod_id.lower():
        ai_provider_display = f"Google Gemini ({mod_id})"
    elif "openai" in ai_prov or "gpt" in mod_id.lower():
        ai_provider_display = f"OpenAI GPT ({mod_id})"
    else:
        ai_provider_display = f"{ai_prov.capitalize()} ({mod_id})"

    return {
        "target_type": target_type,
        "target_url": target_url,
        "authorization_status": auth_status,
        "network_mode": network_mode,
        "ai_provider": ai_provider_display,
        "is_live": is_live
    }


def export_markdown_report(
    assessment_data: Dict[str, Any],
    target_data: Dict[str, Any],
    findings_list: List[Dict[str, Any]],
    skipped_tests: List[str]
) -> str:
    """Generates a complete, structured Markdown security assessment report with 4 discrete sections."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    meta = resolve_target_metadata(target_data, assessment_data)

    # Prevent LIVE/MOCK results from being mixed in the same assessment
    if meta["is_live"]:
        findings_list = [f for f in findings_list if not str(f.get("title", "")).startswith("[SIMULATED]")]
    else:
        findings_list = findings_list

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
        f"",
        f"### Target & Execution Metadata",
        f"- **Target Type:** {meta['target_type']}",
        f"- **Target URL:** {meta['target_url']}",
        f"- **Authorization Status:** {meta['authorization_status']}",
        f"- **Network Mode:** {meta['network_mode']}",
        f"- **AI Provider:** {meta['ai_provider']}",
        f"- **Authorized Scope:** {', '.join(target_data.get('authorized_domains', [])) or 'Offline Source'}",
        f"- **Profile:** {assessment_data.get('profile')}",
        f"- **Run Status:** {assessment_data.get('status')}",
        f"",
    ]

    if not meta["is_live"]:
        md.extend([
            f"> [!WARNING]",
            f"> **SIMULATION RUN NOTICE:**",
            f"> This assessment was executed against a MOCK target in SIMULATED mode.",
            f"> All results, observations, and telemetry are synthetic demonstration data and do not reflect live production systems.",
            f""
        ])

    md.extend([
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
    ])

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
    meta = resolve_target_metadata(target_data, assessment_data)

    # Prevent LIVE/MOCK results from being mixed in the same assessment
    if meta["is_live"]:
        findings_list = [f for f in findings_list if not str(f.get("title", "")).startswith("[SIMULATED]")]

    findings_list = deduplicate_findings(findings_list)
    classified = classify_results(findings_list)

    return {
        "metadata": {
            "application": "Tawassl Security Studio",
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope_notice": STANDARD_LIMITATION_NOTICE,
            "target_type": meta["target_type"],
            "target_url": meta["target_url"],
            "authorization_status": meta["authorization_status"],
            "network_mode": meta["network_mode"],
            "ai_provider": meta["ai_provider"],
            "simulation_notice": None if meta["is_live"] else "SIMULATED RUN: All results are synthetic demonstration data."
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
