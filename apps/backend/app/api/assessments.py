import uuid
import json
import hashlib
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.core.models import AssessmentCreate, AssessmentResponse
from apps.backend.app.policy.sensitive_detector import classify_sensitive_file_response

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])



@router.get("", response_model=List[AssessmentResponse])
async def list_assessments(target_id: str | None = None, db: aiosqlite.Connection = Depends(get_db)):
    """List all assessments, optionally filtered by target_id."""
    query = """
    SELECT id, project_id, target_id, name, profile, status, ai_provider, model_id,
           max_steps, max_requests, max_tool_calls, timeout_seconds, max_output_bytes,
           steps_taken, requests_made, tool_calls_made, started_at, completed_at, error_message, created_at
    FROM assessments
    """
    params = ()
    if target_id:
        query += " WHERE target_id = ?"
        params = (target_id,)
    query += " ORDER BY created_at DESC"

    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [
            AssessmentResponse(
                id=row["id"],
                project_id=row["project_id"],
                target_id=row["target_id"],
                name=row["name"],
                profile=row["profile"],
                status=row["status"],
                ai_provider=row["ai_provider"],
                model_id=row["model_id"],
                max_steps=row["max_steps"],
                max_requests=row["max_requests"],
                max_tool_calls=row["max_tool_calls"],
                timeout_seconds=row["timeout_seconds"],
                max_output_bytes=row["max_output_bytes"],
                steps_taken=row["steps_taken"],
                requests_made=row["requests_made"],
                tool_calls_made=row["tool_calls_made"],
                started_at=str(row["started_at"]) if row["started_at"] else None,
                completed_at=str(row["completed_at"]) if row["completed_at"] else None,
                error_message=row["error_message"],
                created_at=str(row["created_at"])
            )
            for row in rows
        ]


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(data: AssessmentCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Start or queue a new security assessment with explicit profile and hard limits."""
    # Verify target exists
    async with db.execute("SELECT id FROM targets WHERE id = ?", (data.target_id,)) as cursor:
        if not await cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    assessment_id = str(uuid.uuid4())
    await db.execute(
        """
        INSERT INTO assessments (
            id, project_id, target_id, name, profile, status, ai_provider, model_id,
            max_steps, max_requests, max_tool_calls, timeout_seconds, max_output_bytes
        ) VALUES (?, ?, ?, ?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            assessment_id,
            data.project_id,
            data.target_id,
            data.name,
            data.profile,
            data.ai_provider or "mock",
            data.model_id or "mock-sec-v1",
            data.max_steps or 20,
            data.max_requests or 50,
            data.max_tool_calls or 30,
            data.timeout_seconds or 300,
            data.max_output_bytes or (2 * 1024 * 1024)
        )
    )
    await db.commit()

    async with db.execute(
        """
        SELECT id, project_id, target_id, name, profile, status, ai_provider, model_id,
               max_steps, max_requests, max_tool_calls, timeout_seconds, max_output_bytes,
               steps_taken, requests_made, tool_calls_made, started_at, completed_at, error_message, created_at
        FROM assessments WHERE id = ?
        """,
        (assessment_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return AssessmentResponse(
            id=row["id"],
            project_id=row["project_id"],
            target_id=row["target_id"],
            name=row["name"],
            profile=row["profile"],
            status=row["status"],
            ai_provider=row["ai_provider"],
            model_id=row["model_id"],
            max_steps=row["max_steps"],
            max_requests=row["max_requests"],
            max_tool_calls=row["max_tool_calls"],
            timeout_seconds=row["timeout_seconds"],
            max_output_bytes=row["max_output_bytes"],
            steps_taken=row["steps_taken"],
            requests_made=row["requests_made"],
            tool_calls_made=row["tool_calls_made"],
            started_at=str(row["started_at"]) if row["started_at"] else None,
            completed_at=str(row["completed_at"]) if row["completed_at"] else None,
            error_message=row["error_message"],
            created_at=str(row["created_at"])
        )


@router.post("/{assessment_id}/stop", response_model=AssessmentResponse)
async def stop_assessment(assessment_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """Immediately stop and cancel an active assessment."""
    async with db.execute("SELECT id, status FROM assessments WHERE id = ?", (assessment_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE assessments SET status = 'cancelled', completed_at = ? WHERE id = ?",
        (now, assessment_id)
    )
    await db.commit()

    async with db.execute(
        """
        SELECT id, project_id, target_id, name, profile, status, ai_provider, model_id,
               max_steps, max_requests, max_tool_calls, timeout_seconds, max_output_bytes,
               steps_taken, requests_made, tool_calls_made, started_at, completed_at, error_message, created_at
        FROM assessments WHERE id = ?
        """,
        (assessment_id,)
    ) as cursor:
        updated = await cursor.fetchone()
        return AssessmentResponse(
            id=updated["id"],
            project_id=updated["project_id"],
            target_id=updated["target_id"],
            name=updated["name"],
            profile=updated["profile"],
            status=updated["status"],
            ai_provider=updated["ai_provider"],
            model_id=updated["model_id"],
            max_steps=updated["max_steps"],
            max_requests=updated["max_requests"],
            max_tool_calls=updated["max_tool_calls"],
            timeout_seconds=updated["timeout_seconds"],
            max_output_bytes=updated["max_output_bytes"],
            steps_taken=updated["steps_taken"],
            requests_made=updated["requests_made"],
            tool_calls_made=updated["tool_calls_made"],
            started_at=str(updated["started_at"]) if updated["started_at"] else None,
            completed_at=str(updated["completed_at"]) if updated["completed_at"] else None,
            error_message=updated["error_message"],
            created_at=str(updated["created_at"])
        )


@router.post("/{assessment_id}/run")
async def run_assessment_live(assessment_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """Executes live diagnostic assessment on authorized target domain with real-time debug events."""
    from apps.backend.app.policy.models import ScopeRule
    from apps.backend.app.tools.controlled_http import ControlledHTTPClient

    async with db.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)) as cursor:
        assess_row = await cursor.fetchone()
        if not assess_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
        assessment = dict(assess_row)

    async with db.execute("SELECT * FROM targets WHERE id = ?", (assessment["target_id"],)) as cursor:
        target_row = await cursor.fetchone()
        if not target_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        target = dict(target_row)

    auth_domains = json.loads(target["authorized_domains"]) if target.get("authorized_domains") else []
    base_urls = json.loads(target["base_urls"]) if target.get("base_urls") else []
    allowed_ports = json.loads(target["allowed_ports"]) if target.get("allowed_ports") else [80, 443]
    exclusions = json.loads(target["exclusions"]) if target.get("exclusions") else []

    scope = ScopeRule(
        authorized_domains=auth_domains,
        base_urls=base_urls,
        allowed_ports=allowed_ports,
        allow_subdomains=bool(target.get("allow_subdomains")),
        exclusions=exclusions
    )

    started_at = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE assessments SET status = 'running', started_at = ? WHERE id = ?",
        (started_at, assessment_id)
    )
    await db.commit()

    debug_logs = []
    def log_event(level: str, source: str, message: str):
        debug_logs.append({
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "level": level,
            "source": source,
            "message": message
        })

    target_env_mode = str(target.get("environment_mode", "live")).lower()
    is_live = (target_env_mode == "live")
    target_type_label = "LIVE" if is_live else "MOCK"
    primary_target_url = base_urls[0] if base_urls else (f"https://{auth_domains[0]}" if auth_domains else "https://matami.tawassl.com/")
    auth_status_label = "Authorized & Scope Verified" if is_live else "Simulated Sandbox Scope"
    network_mode_label = "Real HTTP Requests" if is_live else "Simulated"

    ai_provider_val = str(assessment.get("ai_provider", "mock")).lower()
    model_id_val = str(assessment.get("model_id", "mock-sec-v1"))
    if ai_provider_val in ("mock", "mock-sec-v1") or model_id_val == "mock-sec-v1":
        ai_provider_display = "Mock Rule Engine (Simulated Analysis)"
    elif "gemini" in ai_provider_val or "gemini" in model_id_val.lower():
        ai_provider_display = f"Google Gemini ({model_id_val})"
    elif "openai" in ai_provider_val or "gpt" in model_id_val.lower():
        ai_provider_display = f"OpenAI GPT ({model_id_val})"
    else:
        ai_provider_display = f"{ai_provider_val.capitalize()} ({model_id_val})"

    # Prevent LIVE/MOCK results from being mixed in the same assessment
    await db.execute("DELETE FROM findings WHERE assessment_id = ?", (assessment_id,))
    await db.commit()

    log_event("info", "orchestrator", f"Initiating {target_type_label} assessment '{assessment['name']}' for target '{target['name']}'")
    log_event("info", "orchestrator", f"Target Type: {target_type_label} | Network Mode: {network_mode_label} | AI Provider: {ai_provider_display}")
    log_event("info", "orchestrator", f"Target URL: {primary_target_url} | Authorization Status: {auth_status_label}")
    if is_live:
        log_event("info", "policy_engine", f"Verified scope: {len(auth_domains)} domain(s), {len(base_urls)} base URL(s). Zero-trust guard ACTIVE.")
    else:
        log_event("warn", "policy_engine", "[SIMULATED] Mock target detected. Egress disabled; running deterministic sandbox simulation.")

    client = ControlledHTTPClient(scope=scope, timeout_seconds=15.0)
    requests_count = 0
    steps_count = 0
    tool_calls_count = 0

    results_by_type = {
        "finding": [],
        "observation": [],
        "passed_control": [],
        "inconclusive": []
    }

    async def record_or_update_result(
        title: str,
        category: str,
        affected_asset: str,
        path: str,
        severity: str,
        confidence: str,
        finding_status: str,
        result_type: str,
        confirmed_vulnerability: bool,
        preconditions: str,
        reproduction_steps: str,
        expected_result: str,
        observed_result: str,
        impact: str | None,
        remediation: str | None,
        evidence_json: str,
        sensitive_file_content_verified: bool = False
    ) -> str:
        # Prevent duplicate findings using target + path + category + evidence hash
        raw_sig = f"{target['id']}:{path}:{category}:{observed_result}"
        evidence_hash = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()

        async with db.execute(
            """
            SELECT id FROM findings 
            WHERE assessment_id = ? AND (evidence_hash = ? OR (affected_asset = ? AND category = ? AND title = ?))
            """,
            (assessment_id, evidence_hash, affected_asset, category, title)
        ) as cur:
            row = await cur.fetchone()
        
        now = datetime.now(timezone.utc).isoformat()
        if row:
            f_id = row["id"]
            await db.execute(
                """
                UPDATE findings SET
                    category = ?,
                    severity = ?,
                    confidence = ?,
                    status = ?,
                    result_type = ?,
                    confirmed_vulnerability = ?,
                    sensitive_file_content_verified = ?,
                    evidence_hash = ?,
                    preconditions = ?,
                    reproduction_steps = ?,
                    expected_result = ?,
                    observed_result = ?,
                    impact = ?,
                    remediation = ?,
                    evidence_json = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    category, severity, confidence, finding_status,
                    result_type, 1 if confirmed_vulnerability else 0,
                    1 if sensitive_file_content_verified else 0, evidence_hash,
                    preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, now, f_id
                )
            )
        else:
            f_id = str(uuid.uuid4())
            await db.execute(
                """
                INSERT INTO findings (
                    id, assessment_id, title, category, affected_asset, severity, confidence,
                    status, result_type, confirmed_vulnerability, sensitive_file_content_verified, evidence_hash,
                    preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f_id, assessment_id, title, category, affected_asset, severity, confidence,
                    finding_status, result_type, 1 if confirmed_vulnerability else 0,
                    1 if sensitive_file_content_verified else 0, evidence_hash,
                    preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, now, now
                )
            )

        if f_id not in results_by_type[result_type]:
            results_by_type[result_type].append(f_id)
        return f_id

    if not is_live:
        # TARGET TYPE = MOCK (Simulated execution, zero network egress)
        log_event("warn", "orchestrator", "[SIMULATED] Mock target execution active. Real HTTP egress is disabled. Running deterministic sandbox simulation.")
        sim_url = primary_target_url

        # Step 1: Simulated Security Headers
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "simulation_engine", f"[Step {steps_count}] [SIMULATED] Auditing baseline security headers on {sim_url}")
        ev_headers = json.dumps([{
            "type": "simulated_http_response",
            "title": "[SIMULATED] Baseline Headers Snapshot (Demo)",
            "content": "Strict-Transport-Security: max-age=31536000\r\nContent-Security-Policy: default-src 'self'\r\nX-Frame-Options: DENY\r\nX-Content-Type-Options: nosniff"
        }])
        await record_or_update_result(
            title="[SIMULATED] Security Headers Policy Enforced (Demo)",
            category="web_security",
            affected_asset=sim_url,
            path="/",
            severity="info",
            confidence="confirmed",
            finding_status="confirmed",
            result_type="passed_control",
            confirmed_vulnerability=False,
            preconditions="Simulated sandboxed test target.",
            reproduction_steps=f"1. Send simulated GET request to {sim_url}\n2. Inspect simulated response headers",
            expected_result="Recommended baseline security headers present.",
            observed_result="[SIMULATED] Recommended baseline security headers verified in sandbox simulation.",
            impact=None,
            remediation=None,
            evidence_json=ev_headers
        )

        # Step 2: Simulated HTTPS Redirection
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "simulation_engine", f"[Step {steps_count}] [SIMULATED] Verifying plaintext HTTP redirection on {sim_url}")
        ev_redir = json.dumps([{
            "type": "simulated_http_response",
            "title": "[SIMULATED] Redirection Snapshot (Demo)",
            "content": f"HTTP Status: 301 Moved Permanently\r\nLocation: {sim_url}"
        }])
        await record_or_update_result(
            title="[SIMULATED] HTTP to HTTPS Redirection Enforced (Demo)",
            category="web_security",
            affected_asset=sim_url,
            path="/",
            severity="info",
            confidence="confirmed",
            finding_status="confirmed",
            result_type="passed_control",
            confirmed_vulnerability=False,
            preconditions="Simulated plaintext HTTP connection.",
            reproduction_steps=f"1. Request plaintext endpoint\n2. Verify 301 redirect to {sim_url}",
            expected_result="Redirect to HTTPS.",
            observed_result="[SIMULATED] Server strictly upgrades plaintext traffic to HTTPS in simulation.",
            impact=None,
            remediation=None,
            evidence_json=ev_redir
        )

        # Step 3: Simulated CORS Origin Isolation
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "simulation_engine", f"[Step {steps_count}] [SIMULATED] Probing CORS preflight isolation on {sim_url}")
        ev_cors = json.dumps([{
            "type": "simulated_http_response",
            "title": "[SIMULATED] CORS Isolation Snapshot (Demo)",
            "content": "Tested Origin: https://untrusted-demo.example\r\nAccess-Control-Allow-Origin: None (Rejected)"
        }])
        await record_or_update_result(
            title="[SIMULATED] CORS Origin Isolation Enforced (Demo)",
            category="web_security",
            affected_asset=sim_url,
            path="/",
            severity="info",
            confidence="confirmed",
            finding_status="confirmed",
            result_type="passed_control",
            confirmed_vulnerability=False,
            preconditions="Simulated cross-origin preflight.",
            reproduction_steps=f"1. Send OPTIONS with untrusted origin\n2. Observe origin rejection",
            expected_result="Untrusted origin rejected.",
            observed_result="[SIMULATED] External untrusted origin safely rejected in simulation.",
            impact=None,
            remediation=None,
            evidence_json=ev_cors
        )

        # Step 4: Simulated Sensitive Path Probe (.env SPA Fallback)
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        env_sim_url = sim_url.rstrip("/") + "/.env"
        log_event("agent", "simulation_engine", f"[Step {steps_count}] [SIMULATED] Testing sensitive path {env_sim_url}")
        ev_env = json.dumps([{
            "type": "simulated_http_response",
            "title": "[SIMULATED] SPA Fallback Snapshot (Demo)",
            "content": "HTTP 200 OK\r\nContent-Type: text/html\r\n<!DOCTYPE html><html><head><title>Dashboard</title></head>..."
        }])
        await record_or_update_result(
            title="[SIMULATED] Single Page Application (SPA) HTML Fallback on Unknown Routes (Demo)",
            category="web_security",
            affected_asset=env_sim_url,
            path="/.env",
            severity="info",
            confidence="confirmed",
            finding_status="observation",
            result_type="observation",
            confirmed_vulnerability=False,
            preconditions="Requesting non-existent or sensitive routes on SPA application.",
            reproduction_steps=f"1. Send GET request to {env_sim_url}\n2. Observe HTTP 200 with HTML body",
            expected_result="HTTP 404 or 403 Forbidden.",
            observed_result="[SIMULATED] Server responds with HTTP 200 serving client-side routing template in simulation.",
            impact="Informational observation. Does not represent a vulnerability.",
            remediation="Optionally configure reverse proxy to return explicit 404 for sensitive extensions.",
            evidence_json=ev_env
        )

        # Step 5: Simulated Server Technology Banner
        steps_count += 1
        tool_calls_count += 1
        log_event("agent", "simulation_engine", f"[Step {steps_count}] [SIMULATED] Checking server technology disclosure on {sim_url}")
        ev_server = json.dumps([{
            "type": "simulated_http_response",
            "title": "[SIMULATED] Server Banner Snapshot (Demo)",
            "content": "Server: Hidden/Generic"
        }])
        await record_or_update_result(
            title="[SIMULATED] Server Technology Banner Obscured (Demo)",
            category="web_security",
            affected_asset=sim_url,
            path="/",
            severity="info",
            confidence="confirmed",
            finding_status="confirmed",
            result_type="passed_control",
            confirmed_vulnerability=False,
            preconditions="Direct request to simulated base URL.",
            reproduction_steps="1. Inspect Server header",
            expected_result="No version information disclosed.",
            observed_result="[SIMULATED] Server technology banner safely obscured in simulation.",
            impact=None,
            remediation=None,
            evidence_json=ev_server
        )
        live_targets = []
    else:
        # TARGET TYPE = LIVE (Real controlled HTTP requests against authorized scope)
        live_targets = base_urls if base_urls else ([f"https://{d}" for d in auth_domains] if auth_domains else ["https://matami.tawassl.com/"])

    # Execute controlled requests only against authorized live target scope
    for base_url in live_targets:
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] [LIVE Network] Auditing primary endpoint: {base_url}")
        
        inspect_res = await client.inspect_url(base_url)
        if inspect_res.get("status") == "policy_denied":
            log_event("error", "policy_engine", f"Scope violation on {base_url}: {inspect_res.get('reason')}")
            continue

        if inspect_res.get("status") == "error":
            log_event("warn", "controlled_http", f"Connection error on {base_url}: {inspect_res.get('error')}")
            continue

        status_code = inspect_res.get("status_code")
        server_header = inspect_res.get("headers", {}).get("server", "Unknown")
        root_preview = inspect_res.get("body_preview", "")
        log_event("success", "controlled_http", f"Connected to {base_url} (HTTP {status_code}) - Server: {server_header}")

        # Step 1: Check security headers
        missing_sec = inspect_res.get("missing_security_headers", [])
        if missing_sec:
            log_event("warn", "finding_engine", f"Flagged missing security headers on {base_url}: {', '.join(missing_sec)}")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": f"HTTP {status_code} Response Headers Snapshot",
                "content": "\r\n".join(f"{k}: {v}" for k, v in inspect_res.get("headers", {}).items())
            }])
            await record_or_update_result(
                title=f"Missing Key Security Headers ({', '.join(missing_sec)})",
                category="web_security",
                affected_asset=base_url,
                path="/",
                severity="medium",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="finding",
                confirmed_vulnerability=True,
                preconditions="Direct HTTPS connection to base URL.",
                reproduction_steps=f"1. Send GET request to {base_url}\n2. Inspect response headers\n3. Observed missing: {', '.join(missing_sec)}",
                expected_result="Headers should include Strict-Transport-Security, Content-Security-Policy, and X-Content-Type-Options.",
                observed_result=f"Response completely omitted: {', '.join(missing_sec)}.",
                impact="Missing defense-in-depth headers increases susceptibility to MIME-sniffing, clickjacking, or downgrade attacks.",
                remediation=f"Configure the web server or reverse proxy to set {', '.join(missing_sec)}.",
                evidence_json=evidence_json
            )
        else:
            log_event("success", "finding_engine", f"Security headers validation passed on {base_url} (HSTS, CSP, X-Frame-Options all verified)")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": f"HTTP {status_code} Headers Snapshot",
                "content": "\r\n".join(f"{k}: {v}" for k, v in inspect_res.get("headers", {}).items())
            }])
            await record_or_update_result(
                title="Security Headers Policy Enforced",
                category="web_security",
                affected_asset=base_url,
                path="/",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="passed_control",
                confirmed_vulnerability=False,
                preconditions="Standard HTTPS connection.",
                reproduction_steps=f"1. Send GET request to {base_url}\n2. Inspect response headers",
                expected_result="Baseline security headers present.",
                observed_result="All recommended baseline security headers are correctly configured (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).",
                impact=None,
                remediation=None,
                evidence_json=evidence_json
            )

        # Step 2: HTTP to HTTPS Redirect check
        if base_url.startswith("https://"):
            http_url = "http://" + base_url[len("https://"):]
            steps_count += 1
            tool_calls_count += 1
            requests_count += 1
            log_event("agent", "controlled_http", f"[Step {steps_count}] Checking HTTP->HTTPS redirection on {http_url}")
            http_res = await client.inspect_url(http_url)
            http_code = http_res.get("status_code")
            location = http_res.get("headers", {}).get("location")
            if http_code in (301, 308) and location and location.startswith("https://"):
                log_event("success", "controlled_http", f"Proper redirect enforced: HTTP {http_code} -> {location}")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "TLS Redirection Headers Snapshot",
                    "content": f"HTTP Status: {http_code}\r\nLocation: {location}"
                }])
                await record_or_update_result(
                    title="HTTP to HTTPS Redirection Enforced",
                    category="web_security",
                    affected_asset=http_url,
                    path="/",
                    severity="info",
                    confidence="confirmed",
                    finding_status="confirmed",
                    result_type="passed_control",
                    confirmed_vulnerability=False,
                    preconditions="Insecure HTTP client request.",
                    reproduction_steps=f"1. Send GET request to {http_url}\n2. Observe 301/308 redirect location",
                    expected_result="Server responds with 301/308 redirect to https:// scheme.",
                    observed_result=f"Server strictly enforces TLS upgrade (HTTP {http_code} -> {location}).",
                    impact=None,
                    remediation=None,
                    evidence_json=evidence_json
                )
            else:
                log_event("warn", "controlled_http", f"Insecure or missing redirect on {http_url}: Status {http_code}, Location: {location}")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "Insecure HTTP Response Headers",
                    "content": f"Status: {http_code}\r\nLocation: {location or 'None'}"
                }])
                await record_or_update_result(
                    title="Insecure HTTP Transport (Missing Redirection)",
                    category="web_security",
                    affected_asset=http_url,
                    path="/",
                    severity="medium",
                    confidence="confirmed",
                    finding_status="confirmed",
                    result_type="finding",
                    confirmed_vulnerability=True,
                    preconditions="Plaintext HTTP connection.",
                    reproduction_steps=f"1. Send GET request to {http_url}\n2. Check if connection is automatically upgraded to HTTPS",
                    expected_result="HTTP 301 redirect to HTTPS.",
                    observed_result=f"Server returned HTTP {http_code} without strict HTTPS upgrade redirect.",
                    impact="Users accessing the application via HTTP could have their traffic intercepted.",
                    remediation="Configure the web server / load balancer to redirect all HTTP traffic to HTTPS.",
                    evidence_json=evidence_json
                )

        # Step 3: CORS Misconfiguration Probe (Bug Bounty Check)
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        cors_test_origin = "https://evil-attacker.example"
        log_event("agent", "controlled_http", f"[Step {steps_count}] Auditing CORS policy with untrusted origin: {cors_test_origin}")
        cors_res = await client.inspect_url(
            base_url,
            method="OPTIONS",
            headers={
                "Origin": cors_test_origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type"
            }
        )
        if cors_res.get("status") == "success":
            cors_headers = {k.lower(): v for k, v in cors_res.get("headers", {}).items()}
            allow_origin = cors_headers.get("access-control-allow-origin")
            allow_creds = cors_headers.get("access-control-allow-credentials", "false").lower() == "true"
            
            if allow_origin == cors_test_origin and allow_creds:
                log_event("error", "finding_engine", f"CRITICAL: CORS origin reflection with credentials allowed on {base_url}!")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "CORS Reflected Origin with Credentials Snapshot",
                    "content": f"Access-Control-Allow-Origin: {allow_origin}\r\nAccess-Control-Allow-Credentials: true"
                }])
                await record_or_update_result(
                    title="CORS Misconfiguration: Arbitrary Origin Reflected with Credentials",
                    category="web_security",
                    affected_asset=base_url,
                    path="/",
                    severity="high",
                    confidence="confirmed",
                    finding_status="confirmed",
                    result_type="finding",
                    confirmed_vulnerability=True,
                    preconditions="Cross-origin browser request from unauthorized domain.",
                    reproduction_steps=f"1. Send OPTIONS request to {base_url} with Origin: {cors_test_origin}\n2. Inspect Access-Control-Allow-Origin and Access-Control-Allow-Credentials",
                    expected_result="Origin should be restricted to trusted domains, or credentials disallowed.",
                    observed_result=f"Reflected origin {allow_origin} with credentials=true.",
                    impact="Enables malicious sites to perform authenticated cross-origin reads of sensitive API responses.",
                    remediation="Replace reflected origin with a strict whitelist of authorized domain origins.",
                    evidence_json=evidence_json
                )
            elif allow_origin == "*":
                log_event("info", "finding_engine", f"Wildcard CORS allowed on {base_url} (credentials={allow_creds})")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "Wildcard CORS Snapshot",
                    "content": f"Access-Control-Allow-Origin: *\r\nAccess-Control-Allow-Credentials: {allow_creds}"
                }])
                await record_or_update_result(
                    title="Public CORS Policy (Wildcard Access-Control-Allow-Origin)",
                    category="web_security",
                    affected_asset=base_url,
                    path="/",
                    severity="info",
                    confidence="confirmed",
                    finding_status="observation",
                    result_type="observation",
                    confirmed_vulnerability=False,
                    preconditions="Cross-origin request to public resource.",
                    reproduction_steps=f"1. Send OPTIONS request to {base_url} with arbitrary Origin\n2. Note wildcard header",
                    expected_result="Explicit origins or intended public resource.",
                    observed_result="Server responds with Access-Control-Allow-Origin: *.",
                    impact="Safe for public static assets; ensure authenticated API routes do not share this policy.",
                    remediation="Verify whether wildcard access is intended for this specific endpoint.",
                    evidence_json=evidence_json
                )
            else:
                log_event("success", "finding_engine", f"CORS protection verified: External untrusted origin '{cors_test_origin}' safely rejected or unreflected.")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "CORS Defense Validation Snapshot",
                    "content": f"Tested Origin: {cors_test_origin}\r\nObserved Allow-Origin: {allow_origin or 'None (Rejected)'}"
                }])
                await record_or_update_result(
                    title="CORS Origin Isolation Enforced",
                    category="web_security",
                    affected_asset=base_url,
                    path="/",
                    severity="info",
                    confidence="confirmed",
                    finding_status="confirmed",
                    result_type="passed_control",
                    confirmed_vulnerability=False,
                    preconditions="Cross-origin preflight request from unauthorized origin.",
                    reproduction_steps=f"1. Send OPTIONS request with Origin: {cors_test_origin}\n2. Observe rejection of unapproved origin",
                    expected_result="Unauthorized origin rejected or omitted from Access-Control-Allow-Origin.",
                    observed_result=f"External untrusted origin '{cors_test_origin}' was safely rejected or not reflected.",
                    impact=None,
                    remediation=None,
                    evidence_json=evidence_json
                )

        # Step 4: Open Redirect Vulnerability Probe (Bug Bounty Check)
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        redirect_test_url = base_url.rstrip("/") + "/?redirect=https://evil-bounty-target.example&next=https://evil-bounty-target.example"
        log_event("agent", "controlled_http", f"[Step {steps_count}] Testing Open Redirect parameters: {redirect_test_url}")
        redir_res = await client.inspect_url(redirect_test_url)
        if redir_res.get("status") == "redirect_escape_prevented":
            raw_target = redir_res.get("raw_location", "")
            if "evil-bounty-target.example" in raw_target:
                log_event("error", "finding_engine", f"CRITICAL: Open Redirect confirmed to {raw_target}!")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "Open Redirect Response Headers",
                    "content": f"Status: {redir_res.get('status_code')}\r\nLocation: {raw_target}"
                }])
                await record_or_update_result(
                    title="Open Redirect via Query Parameter",
                    category="web_security",
                    affected_asset=redirect_test_url,
                    path="/?redirect=...",
                    severity="high",
                    confidence="confirmed",
                    finding_status="confirmed",
                    result_type="finding",
                    confirmed_vulnerability=True,
                    preconditions="Unauthenticated user clicking crafted redirect link.",
                    reproduction_steps=f"1. Navigate to {redirect_test_url}\n2. Observe server issuing 3xx redirect to external location",
                    expected_result="Application should validate redirect target against internal domain whitelist.",
                    observed_result=f"Server attempted redirect to {raw_target}",
                    impact="Attackers can leverage open redirects in phishing campaigns that appear to originate from the trusted domain.",
                    remediation="Implement strict URL validation and reject off-site redirection parameters.",
                    evidence_json=evidence_json
                )
        else:
            log_event("success", "finding_engine", "Open Redirect validation passed: External redirection parameters safely ignored.")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Redirect Sanitization Snapshot",
                "content": f"Tested URL: {redirect_test_url}\r\nResult: Parameter ignored or sanitized."
            }])
            await record_or_update_result(
                title="Open Redirect Parameter Validation Passed",
                category="web_security",
                affected_asset=redirect_test_url,
                path="/?redirect=...",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="passed_control",
                confirmed_vulnerability=False,
                preconditions="Request with unvalidated redirect/next parameters.",
                reproduction_steps=f"1. Send GET request with external redirect target: {redirect_test_url}\n2. Observe server ignoring external destination",
                expected_result="External redirection parameters ignored or sanitized.",
                observed_result="External redirection parameters were safely rejected or sanitized.",
                impact=None,
                remediation=None,
                evidence_json=evidence_json
            )

        # Step 5: Robots.txt & Sensitive Paths Reconnaissance (Bug Bounty Check)
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        robots_url = base_url.rstrip("/") + "/robots.txt"
        log_event("agent", "controlled_http", f"[Step {steps_count}] Probing crawler directives: {robots_url}")
        robots_res = await client.inspect_url(robots_url)
        if robots_res.get("status_code") == 200 and "text/plain" in robots_res.get("headers", {}).get("content-type", ""):
            disallows = [line.strip() for line in robots_res.get("body_preview", "").splitlines() if line.lower().startswith("disallow:")]
            if disallows:
                log_event("info", "finding_engine", f"Cataloged {len(disallows)} Disallow directives in robots.txt ({', '.join(disallows[:3])}...)")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "robots.txt Directives Snapshot",
                    "content": robots_res.get("body_preview", "")[:1000]
                }])
                await record_or_update_result(
                    title="Robots.txt Disallow Directives Cataloged",
                    category="web_security",
                    affected_asset=robots_url,
                    path="/robots.txt",
                    severity="info",
                    confidence="confirmed",
                    finding_status="observation",
                    result_type="observation",
                    confirmed_vulnerability=False,
                    preconditions="Public HTTP request to /robots.txt.",
                    reproduction_steps=f"1. Send GET request to {robots_url}\n2. Review Disallow rules for internal paths",
                    expected_result="Public robots.txt should not catalog sensitive internal administration routes.",
                    observed_result=f"Found disallow entries: {', '.join(disallows[:5])}",
                    impact="Search engines respect disallow, but malicious crawlers use it as an endpoint discovery roadmap.",
                    remediation="Avoid relying on robots.txt for security. Protect private routes with proper authentication.",
                    evidence_json=evidence_json
                )
            else:
                log_event("info", "finding_engine", "robots.txt present but contains no Disallow restrictions.")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "Clean robots.txt Snapshot",
                    "content": robots_res.get("body_preview", "")[:500]
                }])
                await record_or_update_result(
                    title="Robots.txt Endpoint Isolation Verified",
                    category="web_security",
                    affected_asset=robots_url,
                    path="/robots.txt",
                    severity="info",
                    confidence="confirmed",
                    finding_status="confirmed",
                    result_type="passed_control",
                    confirmed_vulnerability=False,
                    preconditions="Public HTTP request to /robots.txt.",
                    reproduction_steps=f"1. Inspect {robots_url}",
                    expected_result="No sensitive internal paths disclosed.",
                    observed_result="No internal paths or sensitive endpoints disclosed via crawler directives.",
                    impact=None,
                    remediation=None,
                    evidence_json=evidence_json
                )
        else:
            log_event("info", "finding_engine", f"No public robots.txt discovered on {base_url}.")

        # Step 6: Git Repository Exposure Check (Bug Bounty Check)
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        git_url = base_url.rstrip("/") + "/.git/HEAD"
        log_event("agent", "controlled_http", f"[Step {steps_count}] Probing exposed Git repository: {git_url}")
        git_res = await client.inspect_url(git_url)
        git_preview = git_res.get("body_preview", "").strip()
        git_code = git_res.get("status_code")
        if git_code == 200 and ("ref: refs/" in git_preview or (len(git_preview) == 40 and all(c in "0123456789abcdef" for c in git_preview.lower()))):
            log_event("error", "finding_engine", f"CRITICAL VULNERABILITY: Exposed .git repository at {git_url}!")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Exposed Git HEAD Contents",
                "content": git_preview
            }])
            await record_or_update_result(
                title="Exposed Git Repository Metadata (/.git/HEAD)",
                category="web_security",
                affected_asset=git_url,
                path="/.git/HEAD",
                severity="critical",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="finding",
                confirmed_vulnerability=True,
                preconditions="Public HTTP access to /.git/HEAD.",
                reproduction_steps=f"1. Send GET request to {git_url}\n2. Inspect response body for Git branch pointer",
                expected_result="HTTP 404 or 403 Forbidden.",
                observed_result=f"Returned Git pointer: {git_preview}",
                impact="Complete source code repository and commit history can be downloaded by an attacker.",
                remediation="Block access to dotfiles like .git in web server / reverse proxy configuration.",
                evidence_json=evidence_json
            )
        else:
            log_event("success", "finding_engine", "Git repository exposure probe clean (/.git/HEAD safely blocked).")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Git Access Block Snapshot",
                "content": f"Status: {git_code}"
            }])
            await record_or_update_result(
                title="Git Repository Metadata Access Restricted",
                category="web_security",
                affected_asset=git_url,
                path="/.git/HEAD",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="passed_control",
                confirmed_vulnerability=False,
                preconditions="Public HTTP request to /.git/HEAD.",
                reproduction_steps=f"1. Send GET request to {git_url}\n2. Observe access blocked",
                expected_result="Access to /.git metadata denied or not found.",
                observed_result=f"Access to /.git/HEAD safely restricted (HTTP {git_code}).",
                impact=None,
                remediation=None,
                evidence_json=evidence_json
            )

        # Step 7: Sensitive Configuration & Environment File Probe (/.env)
        # Content-Aware Verification enforcing:
        # - Never classify /.env from HTTP status alone
        # - 404 / 403 -> PASS
        # - 200 + text/html + SPA/index/login/error page -> NOT VULNERABLE
        # - 200 + HTML containing JS/config-looking text -> do NOT assume .env exposure
        # - 200 + genuine plaintext dotenv -> CONFIRMED FINDING (sensitive_file_content_verified = True)
        # - Ambiguous content -> inconclusive
        # - Never include actual secret values in reports/logs; redact values
        # - Never report variable count unless parser verifies actual dotenv lines
        # - Only show "rotate disclosed secrets" remediation when confirmed
        env_url = base_url.rstrip("/") + "/.env"
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] Probing sensitive configuration path: {env_url}")
        env_res = await client.inspect_url(env_url)
        env_code = env_res.get("status_code", 0)
        env_headers = env_res.get("headers", {})
        env_body = env_res.get("body_preview", "")

        detected = classify_sensitive_file_response(
            path="/.env",
            status_code=env_code,
            headers=env_headers,
            body=env_body,
            root_body=root_preview
        )

        evidence_content = (
            f"Status: {env_code}\r\n"
            f"Content-Type: {env_headers.get('content-type', 'unknown')}\r\n"
            f"Classification Reason: {detected.classification_reason}\r\n"
            f"Sensitive Content Verified: {detected.sensitive_file_content_verified}\r\n"
        )
        if detected.sensitive_file_content_verified:
            evidence_content += f"Verified Declarations ({detected.verified_variable_count}):\r\n" + "\r\n".join(detected.redacted_declarations[:10])
        else:
            evidence_content += f"Body Preview:\r\n{env_body[:300]}"

        evidence_json = json.dumps([{
            "type": "http_response",
            "title": f"Sensitive Path Verification Snapshot ({detected.result_type.upper()})",
            "content": evidence_content,
            "sensitive_file_content_verified": detected.sensitive_file_content_verified,
            "spa_detected": detected.spa_detected,
            "verified_variable_count": detected.verified_variable_count
        }])

        await record_or_update_result(
            title=detected.title,
            category="web_security",
            affected_asset=env_url,
            path="/.env",
            severity=detected.severity,
            confidence=detected.confidence,
            finding_status=detected.finding_status,
            result_type=detected.result_type,
            confirmed_vulnerability=detected.confirmed_vulnerability,
            sensitive_file_content_verified=detected.sensitive_file_content_verified,
            preconditions=detected.preconditions,
            reproduction_steps=detected.reproduction_steps,
            expected_result=detected.expected_result,
            observed_result=detected.observed_result,
            impact=detected.impact,
            remediation=detected.remediation,
            evidence_json=evidence_json
        )

        if detected.confirmed_vulnerability and detected.sensitive_file_content_verified:
            log_event("error", "finding_engine", f"CRITICAL VULNERABILITY: Verified sensitive environment file exposed at {env_url} ({detected.verified_variable_count} variables)")
        elif detected.result_type == "observation":
            log_event("info", "finding_engine", f"Observation on {env_url}: {detected.observed_result}")
        elif detected.result_type == "passed_control":
            log_event("success", "finding_engine", f"Passed control on {env_url}: {detected.observed_result}")
        else:
            log_event("warn", "finding_engine", f"Inconclusive response on {env_url}: {detected.observed_result}")

        # Step 8: Server Banner & Technology Fingerprinting
        steps_count += 1
        tool_calls_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] Auditing server banner and technology fingerprinting...")
        server_raw = inspect_res.get("headers", {}).get("server", "")
        if any(char.isdigit() for char in server_raw):
            log_event("warn", "finding_engine", f"Verbose server version string disclosed: {server_raw}")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Server Banner Snapshot",
                "content": f"Server: {server_raw}"
            }])
            await record_or_update_result(
                title="Verbose Server Version Disclosed",
                category="web_security",
                affected_asset=base_url,
                path="/",
                severity="low",
                confidence="confirmed",
                finding_status="observation",
                result_type="observation",
                confirmed_vulnerability=False,
                preconditions="Direct HTTP request to base URL.",
                reproduction_steps=f"1. Send GET request to {base_url}\n2. Inspect 'Server' response header",
                expected_result="Server header should be omitted or generic without version numbers.",
                observed_result=f"Server disclosed exact software version: {server_raw}",
                impact="Disclosing exact server versions aids attackers in targeting known CVE vulnerabilities.",
                remediation="Configure server software (e.g., server_tokens off in Nginx) to conceal version details.",
                evidence_json=evidence_json
            )
        else:
            log_event("success", "finding_engine", f"Server banner safely obscured (Banner: '{server_raw or 'Hidden'}'). No version leaks.")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Server Banner Snapshot",
                "content": f"Server: {server_raw or 'Hidden'}"
            }])
            await record_or_update_result(
                title="Server Technology Banner Obscured",
                category="web_security",
                affected_asset=base_url,
                path="/",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="passed_control",
                confirmed_vulnerability=False,
                preconditions="Direct HTTP request to base URL.",
                reproduction_steps=f"1. Inspect Server header on {base_url}",
                expected_result="No version information disclosed.",
                observed_result="Server technology banner safely obscured. No version leaks detected.",
                impact=None,
                remediation=None,
                evidence_json=evidence_json
            )

    completed_at = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """
        UPDATE assessments SET
            status = 'completed',
            completed_at = ?,
            steps_taken = steps_taken + ?,
            requests_made = requests_made + ?,
            tool_calls_made = tool_calls_made + ?
        WHERE id = ?
        """,
        (completed_at, steps_count, requests_count, tool_calls_count, assessment_id)
    )
    await db.commit()

    confirmed_count = len(results_by_type["finding"])
    observations_count = len(results_by_type["observation"])
    passed_count = len(results_by_type["passed_control"])
    inconclusive_count = len(results_by_type["inconclusive"])

    if confirmed_count == 0:
        log_event("info", "finding_engine", "No confirmed vulnerabilities were identified by the tests executed within this assessment scope.")

    log_event(
        "success", "orchestrator",
        f"Assessment completed: {confirmed_count} Confirmed Vulnerabilities, {observations_count} Observations, {passed_count} Passed Controls, {inconclusive_count} Inconclusive."
    )

    # Return updated assessment
    async with db.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)) as cursor:
        updated = await cursor.fetchone()
        return {
            "assessment": AssessmentResponse(
                id=updated["id"],
                project_id=updated["project_id"],
                target_id=updated["target_id"],
                name=updated["name"],
                profile=updated["profile"],
                status=updated["status"],
                ai_provider=updated["ai_provider"],
                model_id=updated["model_id"],
                max_steps=updated["max_steps"],
                max_requests=updated["max_requests"],
                max_tool_calls=updated["max_tool_calls"],
                timeout_seconds=updated["timeout_seconds"],
                max_output_bytes=updated["max_output_bytes"],
                steps_taken=updated["steps_taken"],
                requests_made=updated["requests_made"],
                tool_calls_made=updated["tool_calls_made"],
                started_at=str(updated["started_at"]) if updated["started_at"] else None,
                completed_at=str(updated["completed_at"]) if updated["completed_at"] else None,
                error_message=updated["error_message"],
                created_at=str(updated["created_at"])
            ),
            "debug_logs": debug_logs,
            "target_metadata": {
                "target_type": target_type_label,
                "target_url": primary_target_url,
                "authorization_status": auth_status_label,
                "network_mode": network_mode_label,
                "ai_provider": ai_provider_display
            },
            "results_summary": {
                "confirmed_vulnerabilities": confirmed_count,
                "security_observations": observations_count,
                "passed_controls": passed_count,
                "inconclusive_tests": inconclusive_count
            },
            "new_findings_count": confirmed_count
        }


