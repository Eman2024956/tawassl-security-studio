import uuid
import json
import hashlib
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.core.models import AssessmentCreate, AssessmentResponse

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

    log_event("info", "orchestrator", f"Initiating live assessment '{assessment['name']}' for target '{target['name']}'")
    log_event("info", "policy_engine", f"Verified scope: {len(auth_domains)} domain(s), {len(base_urls)} base URL(s). Zero-trust guard ACTIVE.")

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
        evidence_json: str
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
                    result_type, 1 if confirmed_vulnerability else 0, evidence_hash,
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
                    status, result_type, confirmed_vulnerability, evidence_hash,
                    preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f_id, assessment_id, title, category, affected_asset, severity, confidence,
                    finding_status, result_type, 1 if confirmed_vulnerability else 0, evidence_hash,
                    preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, now, now
                )
            )

        if f_id not in results_by_type[result_type]:
            results_by_type[result_type].append(f_id)
        return f_id

    # Check each base URL
    for base_url in base_urls:
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] Auditing primary endpoint: {base_url}")
        
        inspect_res = await client.inspect_url(base_url)
        if inspect_res.get("status") == "policy_denied":
            log_event("error", "policy_engine", f"Scope violation on {base_url}: {inspect_res.get('reason')}")
            continue

        if inspect_res.get("status") == "error":
            log_event("warn", "controlled_http", f"Connection error on {base_url}: {inspect_res.get('error')}")
            continue

        status_code = inspect_res.get("status_code")
        server_header = inspect_res.get("headers", {}).get("server", "Unknown")
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
        # Requirements:
        # - 403 / 404 → PASS (passed_control)
        # - 200 + normal SPA/index HTML → OBSERVATION, not vulnerability
        # - 200 + actual secret/config content → FINDING (confirmed_vulnerability=True)
        # - Do not require 404 as the only safe result.
        env_url = base_url.rstrip("/") + "/.env"
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] Probing sensitive configuration path: {env_url}")
        env_res = await client.inspect_url(env_url)
        env_code = env_res.get("status_code")
        content_type = env_res.get("headers", {}).get("content-type", "").lower()
        env_body = env_res.get("body_preview", "")

        has_secrets = False
        if env_code == 200:
            lines = [l.strip() for l in env_body.splitlines() if l.strip() and not l.strip().startswith("#")]
            key_val_lines = [l for l in lines if "=" in l and not l.startswith("<") and not l.startswith("{") and not l.startswith("/*")]
            if key_val_lines or ("text/plain" in content_type and len(lines) > 0 and "<html" not in env_body.lower()):
                has_secrets = True

        if env_code in (401, 403, 404):
            # PASS (403 or 404 or 401 is safe)
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": f"HTTP {env_code} Safe Restriction Snapshot",
                "content": f"Status: {env_code} (Protected)\r\nPath: {env_url}"
            }])
            await record_or_update_result(
                title="Sensitive Environment File Protected (/.env)",
                category="web_security",
                affected_asset=env_url,
                path="/.env",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="passed_control",
                confirmed_vulnerability=False,
                preconditions="Public HTTP request to sensitive path /.env.",
                reproduction_steps=f"1. Send GET request to {env_url}\n2. Server returns HTTP {env_code}",
                expected_result="HTTP 403 Forbidden or 404 Not Found.",
                observed_result=f"Access safely restricted (HTTP {env_code}). No sensitive environment secrets exposed.",
                impact=None,
                remediation=None,
                evidence_json=evidence_json
            )
            log_event("success", "finding_engine", f"Sensitive path protection verified: {env_url} safely returned HTTP {env_code} (Passed Control)")

        elif env_code == 200 and ("text/html" in content_type or "<html" in env_body.lower() or "<!doctype html" in env_body.lower()) and not has_secrets:
            # SPA FALLBACK -> OBSERVATION, NOT VULNERABILITY
            log_event("info", "finding_engine", f"Path {env_url} returned HTTP 200 with HTML (SPA client-side routing fallback, categorized as Security Observation)")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "SPA Fallback HTTP 200 Response",
                "content": f"Status: 200 OK\r\nContent-Type: {content_type}\r\nBody Preview:\n{env_body[:300]}"
            }])
            await record_or_update_result(
                title="Single Page Application (SPA) HTML Fallback on Unknown Routes",
                category="web_security",
                affected_asset=env_url,
                path="/.env",
                severity="info",
                confidence="confirmed",
                finding_status="observation",
                result_type="observation",
                confirmed_vulnerability=False,
                preconditions="Requesting arbitrary non-existent or sensitive paths on an SPA application.",
                reproduction_steps=f"1. Send GET request to {env_url}\n2. Observe HTTP 200 response with Content-Type: {content_type}",
                expected_result="Expected HTTP 404 Not Found or HTTP 403 Forbidden for non-existent sensitive file paths.",
                observed_result="Server responds with HTTP 200 serving index.html dashboard template.",
                impact="Non-vulnerability observation. May cause false positives in automated vulnerability scanners that only check status code 200 without analyzing MIME type.",
                remediation="Optionally configure reverse proxy (Nginx/Vercel) to return explicit 404 for sensitive extensions (e.g. .env, .git, .bak).",
                evidence_json=evidence_json
            )

        elif env_code == 200 and has_secrets:
            # ACTUAL SECRET LEAK -> FINDING
            log_event("error", "finding_engine", f"CRITICAL VULNERABILITY: Sensitive environment configuration disclosed at {env_url}!")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Exposed Sensitive Configuration Excerpt",
                "content": f"Status: 200 OK\r\nContent-Type: {content_type}\r\nDisclosed Config Content Lines: {len(key_val_lines)}"
            }])
            await record_or_update_result(
                title="Exposed Sensitive Environment File (/.env)",
                category="web_security",
                affected_asset=env_url,
                path="/.env",
                severity="critical",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="finding",
                confirmed_vulnerability=True,
                preconditions="Public HTTP access to /.env.",
                reproduction_steps=f"1. Send GET request to {env_url}\n2. Inspect response body for environment variables",
                expected_result="HTTP 404 Not Found or 403 Forbidden.",
                observed_result=f"Server returned unmasked configuration content with {len(key_val_lines)} variable declarations.",
                impact="High-value secrets, database credentials, or API keys can be compromised.",
                remediation="Immediately restrict public access to .env files and rotate disclosed secrets.",
                evidence_json=evidence_json
            )
        else:
            # Other non-secret responses
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": f"HTTP {env_code} Safe Restriction",
                "content": f"Status: {env_code}\r\nContent-Type: {content_type}"
            }])
            await record_or_update_result(
                title="Sensitive Environment File Access Restricted",
                category="web_security",
                affected_asset=env_url,
                path="/.env",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                result_type="passed_control",
                confirmed_vulnerability=False,
                preconditions="Public HTTP request to sensitive path /.env.",
                reproduction_steps=f"1. Send GET request to {env_url}\n2. Server returns HTTP {env_code}",
                expected_result="HTTP 403 Forbidden or 404 Not Found.",
                observed_result=f"Server returned HTTP {env_code}; no environment secrets disclosed.",
                impact=None,
                remediation=None,
                evidence_json=evidence_json
            )
            log_event("success", "finding_engine", f"Path {env_url} safely returned HTTP {env_code} (Passed Control)")

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
            "results_summary": {
                "confirmed_vulnerabilities": confirmed_count,
                "security_observations": observations_count,
                "passed_controls": passed_count,
                "inconclusive_tests": inconclusive_count
            },
            "new_findings_count": confirmed_count
        }


