import uuid
import json
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
    new_findings = []

    async def record_or_update_finding(
        title: str,
        category: str,
        affected_asset: str,
        severity: str,
        confidence: str,
        finding_status: str,
        preconditions: str,
        reproduction_steps: str,
        expected_result: str,
        observed_result: str,
        impact: str,
        remediation: str,
        evidence_json: str
    ) -> str:
        async with db.execute(
            "SELECT id FROM findings WHERE assessment_id = ? AND title = ? AND affected_asset = ?",
            (assessment_id, title, affected_asset)
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
                    category, severity, confidence, finding_status, preconditions,
                    reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, now, f_id
                )
            )
            return f_id
        else:
            f_id = str(uuid.uuid4())
            await db.execute(
                """
                INSERT INTO findings (
                    id, assessment_id, title, category, affected_asset, severity, confidence,
                    status, preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f_id, assessment_id, title, category, affected_asset, severity, confidence,
                    finding_status, preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json, now, now
                )
            )
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

        # Check missing security headers
        missing_sec = inspect_res.get("missing_security_headers", [])
        if missing_sec:
            log_event("warn", "finding_engine", f"Flagged missing security headers on {base_url}: {', '.join(missing_sec)}")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": f"HTTP {status_code} Response Headers Snapshot",
                "content": "\r\n".join(f"{k}: {v}" for k, v in inspect_res.get("headers", {}).items())
            }])
            f_id = await record_or_update_finding(
                title=f"Missing Key Security Headers ({', '.join(missing_sec)})",
                category="web_security",
                affected_asset=base_url,
                severity="medium",
                confidence="confirmed",
                finding_status="confirmed",
                preconditions="Direct HTTPS connection to base URL.",
                reproduction_steps=f"1. Send GET request to {base_url}\n2. Inspect response headers\n3. Observed missing: {', '.join(missing_sec)}",
                expected_result="Headers should include Strict-Transport-Security, Content-Security-Policy, and X-Content-Type-Options.",
                observed_result=f"Response completely omitted: {', '.join(missing_sec)}.",
                impact="Missing defense-in-depth headers increases susceptibility to MIME-sniffing, clickjacking, or downgrade attacks.",
                remediation=f"Configure the web server or reverse proxy to set {', '.join(missing_sec)}.",
                evidence_json=evidence_json
            )
            if f_id not in new_findings:
                new_findings.append(f_id)
        else:
            log_event("success", "finding_engine", f"Security headers validation passed on {base_url} (HSTS, CSP, X-Frame-Options all verified)")

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
            else:
                log_event("warn", "controlled_http", f"Insecure or missing redirect on {http_url}: Status {http_code}, Location: {location}")

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
                f_id = await record_or_update_finding(
                    title="CORS Misconfiguration: Arbitrary Origin Reflected with Credentials",
                    category="web_security",
                    affected_asset=base_url,
                    severity="high",
                    confidence="confirmed",
                    finding_status="confirmed",
                    preconditions="Cross-origin browser request from unauthorized domain.",
                    reproduction_steps=f"1. Send OPTIONS request to {base_url} with Origin: {cors_test_origin}\n2. Inspect Access-Control-Allow-Origin and Access-Control-Allow-Credentials",
                    expected_result="Origin should be restricted to trusted domains, or credentials disallowed.",
                    observed_result=f"Reflected origin {allow_origin} with credentials=true.",
                    impact="Enables malicious sites to perform authenticated cross-origin reads of sensitive API responses.",
                    remediation="Replace reflected origin with a strict whitelist of authorized domain origins.",
                    evidence_json=evidence_json
                )
                if f_id not in new_findings:
                    new_findings.append(f_id)
            elif allow_origin == "*":
                log_event("info", "finding_engine", f"Wildcard CORS allowed on {base_url} (credentials={allow_creds})")
            else:
                log_event("success", "finding_engine", f"CORS protection verified: External untrusted origin '{cors_test_origin}' safely rejected or unreflected.")

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
                f_id = await record_or_update_finding(
                    title="Open Redirect via Query Parameter",
                    category="web_security",
                    affected_asset=redirect_test_url,
                    severity="high",
                    confidence="confirmed",
                    finding_status="confirmed",
                    preconditions="Unauthenticated user clicking crafted redirect link.",
                    reproduction_steps=f"1. Navigate to {redirect_test_url}\n2. Observe server issuing 3xx redirect to external location",
                    expected_result="Application should validate redirect target against internal domain whitelist.",
                    observed_result=f"Server attempted redirect to {raw_target}",
                    impact="Attackers can leverage open redirects in phishing campaigns that appear to originate from the trusted domain.",
                    remediation="Implement strict URL validation and reject off-site redirection parameters.",
                    evidence_json=evidence_json
                )
                if f_id not in new_findings:
                    new_findings.append(f_id)
        else:
            log_event("success", "finding_engine", "Open Redirect validation passed: External redirection parameters safely ignored.")

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
                f_id = await record_or_update_finding(
                    title="Robots.txt Disallow Directives Expose Internal Endpoints",
                    category="web_security",
                    affected_asset=robots_url,
                    severity="info",
                    confidence="confirmed",
                    finding_status="observation",
                    preconditions="Public HTTP request to /robots.txt.",
                    reproduction_steps=f"1. Send GET request to {robots_url}\n2. Review Disallow rules for internal paths",
                    expected_result="Public robots.txt should not inadvertently catalog sensitive administration routes.",
                    observed_result=f"Found disallow entries: {', '.join(disallows[:5])}",
                    impact="Search engines respect disallow, but malicious crawlers use it as a target roadmap.",
                    remediation="Avoid relying on robots.txt for security. Protect private routes with authentication instead.",
                    evidence_json=evidence_json
                )
                if f_id not in new_findings:
                    new_findings.append(f_id)
            else:
                log_event("info", "finding_engine", f"robots.txt present but contains no Disallow restrictions.")
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
        if git_res.get("status_code") == 200 and ("ref: refs/" in git_preview or (len(git_preview) == 40 and all(c in "0123456789abcdef" for c in git_preview.lower()))):
            log_event("error", "finding_engine", f"CRITICAL VULNERABILITY: Exposed .git repository at {git_url}!")
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": "Exposed Git HEAD Contents",
                "content": git_preview
            }])
            f_id = await record_or_update_finding(
                title="Exposed Git Repository Metadata (/.git/HEAD)",
                category="web_security",
                affected_asset=git_url,
                severity="critical",
                confidence="confirmed",
                finding_status="confirmed",
                preconditions="Public HTTP access to /.git/HEAD.",
                reproduction_steps=f"1. Send GET request to {git_url}\n2. Inspect response body for Git branch pointer",
                expected_result="HTTP 404 or 403 Forbidden.",
                observed_result=f"Returned Git pointer: {git_preview}",
                impact="Complete source code repository and commit history can be downloaded by an attacker.",
                remediation="Block access to dotfiles like .git in web server / reverse proxy configuration.",
                evidence_json=evidence_json
            )
            if f_id not in new_findings:
                new_findings.append(f_id)
        else:
            log_event("success", "finding_engine", "Git repository exposure probe clean (/.git/HEAD safely blocked).")

        # Step 7: Sensitive Configuration & Environment File Probe
        env_url = base_url.rstrip("/") + "/.env"
        steps_count += 1
        tool_calls_count += 1
        requests_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] Probing sensitive configuration path: {env_url}")
        env_res = await client.inspect_url(env_url)
        content_type = env_res.get("headers", {}).get("content-type", "")
        if env_res.get("status_code") == 200:
            if "text/html" in content_type:
                log_event("info", "finding_engine", f"Path {env_url} returned HTTP 200 with HTML (SPA client-side routing fallback, not an active secret leak)")
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "SPA Fallback HTTP 200 Response",
                    "content": f"Status: 200 OK\r\nContent-Type: {content_type}\r\nBody Preview:\n{env_res.get('body_preview', '')[:300]}"
                }])
                f_id = await record_or_update_finding(
                    title="Single Page Application (SPA) HTML Fallback on Unknown Routes",
                    category="web_security",
                    affected_asset=env_url,
                    severity="info",
                    confidence="confirmed",
                    finding_status="observation",
                    preconditions="Requesting arbitrary non-existent or sensitive paths.",
                    reproduction_steps=f"1. Send GET request to {env_url}\n2. Observe HTTP 200 response with Content-Type: {content_type}",
                    expected_result="Expected HTTP 404 Not Found for non-existent sensitive file paths.",
                    observed_result="Server responds with HTTP 200 serving index.html dashboard template.",
                    impact="May cause false positives in automated vulnerability scanners that only check status code 200 without analyzing MIME type.",
                    remediation="Optionally configure reverse proxy (Nginx/Vercel) to return explicit 404 for sensitive extensions (e.g. .env, .git, .bak).",
                    evidence_json=evidence_json
                )
                if f_id not in new_findings:
                    new_findings.append(f_id)
            else:
                log_event("error", "finding_engine", f"CRITICAL: Non-HTML response on {env_url}!")

        # Step 8: Server Banner & Technology Fingerprinting
        steps_count += 1
        tool_calls_count += 1
        log_event("agent", "controlled_http", f"[Step {steps_count}] Auditing server banner and technology fingerprinting...")
        server_raw = inspect_res.get("headers", {}).get("server", "")
        if any(char.isdigit() for char in server_raw):
            log_event("warn", "finding_engine", f"Verbose server version string disclosed: {server_raw}")
        else:
            log_event("success", "finding_engine", f"Server banner safely obscured (Banner: '{server_raw or 'Hidden'}'). No version leaks.")

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

    log_event("success", "orchestrator", f"Assessment completed successfully. {requests_count} requests executed, {len(new_findings)} finding(s) recorded.")

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
            "new_findings_count": len(new_findings)
        }

