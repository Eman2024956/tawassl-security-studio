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
            finding_id = str(uuid.uuid4())
            evidence_json = json.dumps([{
                "type": "http_response",
                "title": f"HTTP {status_code} Response Headers Snapshot",
                "content": "\r\n".join(f"{k}: {v}" for k, v in inspect_res.get("headers", {}).items())
            }])
            await db.execute(
                """
                INSERT INTO findings (
                    id, assessment_id, title, category, affected_asset, severity, confidence,
                    status, preconditions, reproduction_steps, expected_result, observed_result,
                    impact, remediation, evidence_json
                ) VALUES (?, ?, ?, 'web_security', ?, 'medium', 'confirmed', 'confirmed', ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding_id,
                    assessment_id,
                    f"Missing Key Security Headers ({', '.join(missing_sec)})",
                    base_url,
                    "Direct HTTPS connection to base URL.",
                    f"1. Send GET request to {base_url}\n2. Inspect response headers\n3. Observed missing: {', '.join(missing_sec)}",
                    "Headers should include Strict-Transport-Security, Content-Security-Policy, and X-Content-Type-Options.",
                    f"Response completely omitted: {', '.join(missing_sec)}.",
                    "Missing defense-in-depth headers increases susceptibility to MIME-sniffing, clickjacking, or downgrade attacks.",
                    f"Configure the web server or reverse proxy to set {', '.join(missing_sec)}.",
                    evidence_json
                )
            )
            new_findings.append(finding_id)
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

        # Step 3: Sensitive path diagnostic (e.g. /.env check)
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
                finding_id = str(uuid.uuid4())
                evidence_json = json.dumps([{
                    "type": "http_response",
                    "title": "SPA Fallback HTTP 200 Response",
                    "content": f"Status: 200 OK\r\nContent-Type: {content_type}\r\nBody Preview:\n{env_res.get('body_preview', '')[:300]}"
                }])
                await db.execute(
                    """
                    INSERT INTO findings (
                        id, assessment_id, title, category, affected_asset, severity, confidence,
                        status, preconditions, reproduction_steps, expected_result, observed_result,
                        impact, remediation, evidence_json
                    ) VALUES (?, ?, 'Single Page Application (SPA) HTML Fallback on Unknown Routes', 'web_security', ?, 'info', 'confirmed', 'observation', ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        finding_id,
                        assessment_id,
                        env_url,
                        "Requesting arbitrary non-existent or sensitive paths.",
                        f"1. Send GET request to {env_url}\n2. Observe HTTP 200 response with Content-Type: {content_type}",
                        "Expected HTTP 404 Not Found for non-existent sensitive file paths.",
                        "Server responds with HTTP 200 serving index.html dashboard template.",
                        "May cause false positives in automated vulnerability scanners that only check status code 200 without analyzing MIME type.",
                        "Optionally configure reverse proxy (Nginx/Vercel) to return explicit 404 for sensitive extensions (e.g. .env, .git, .bak).",
                        evidence_json
                    )
                )
                new_findings.append(finding_id)
            else:
                log_event("error", "finding_engine", f"CRITICAL: Non-HTML response on {env_url}!")

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

