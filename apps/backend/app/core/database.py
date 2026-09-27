import aiosqlite
import json
import logging
from pathlib import Path
from typing import AsyncGenerator
from apps.backend.app.core.config import settings

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS targets (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    target_type TEXT NOT NULL, -- website, api, source, combined
    environment_mode TEXT NOT NULL DEFAULT 'live', -- live, mock
    authorized_domains TEXT NOT NULL, -- JSON array of strings
    base_urls TEXT NOT NULL, -- JSON array of strings
    allowed_ports TEXT, -- JSON array of integers
    allow_subdomains INTEGER DEFAULT 0,
    exclusions TEXT, -- JSON array of strings
    source_path TEXT,
    auth_config TEXT, -- Redacted or encrypted JSON credentials reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessments (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    name TEXT NOT NULL,
    profile TEXT NOT NULL, -- observe, source_review, controlled_active, authenticated, regression
    status TEXT NOT NULL DEFAULT 'queued', -- queued, awaiting_approval, running, completed, failed, cancelled, inconclusive
    ai_provider TEXT NOT NULL DEFAULT 'mock',
    model_id TEXT NOT NULL DEFAULT 'mock-sec-v1',
    max_steps INTEGER NOT NULL,
    max_requests INTEGER NOT NULL,
    max_tool_calls INTEGER NOT NULL,
    timeout_seconds INTEGER NOT NULL,
    max_output_bytes INTEGER NOT NULL,
    steps_taken INTEGER DEFAULT 0,
    requests_made INTEGER DEFAULT 0,
    tool_calls_made INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(target_id) REFERENCES targets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    arguments_json TEXT NOT NULL,
    arguments_hash TEXT NOT NULL,
    purpose TEXT NOT NULL,
    side_effects TEXT NOT NULL,
    resource_limits_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, rejected, expired, consumed
    approved_by TEXT,
    approved_at TIMESTAMP,
    consumed_at TIMESTAMP,
    execution_result_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    affected_asset TEXT NOT NULL,
    severity TEXT NOT NULL, -- critical, high, medium, low, info
    confidence TEXT NOT NULL, -- confirmed, high, medium, low
    status TEXT NOT NULL, -- observation, suspected, confirmed, inconclusive, false_positive, fixed, retest_failed
    result_type TEXT NOT NULL DEFAULT 'finding', -- passed_control, observation, finding, inconclusive
    confirmed_vulnerability INTEGER NOT NULL DEFAULT 0, -- 0 or 1
    sensitive_file_content_verified INTEGER NOT NULL DEFAULT 0, -- 0 or 1
    evidence_hash TEXT,
    preconditions TEXT,
    reproduction_steps TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    observed_result TEXT NOT NULL,
    impact TEXT,
    remediation TEXT,
    evidence_json TEXT NOT NULL, -- list of evidence items (request, response, file snippet, log)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    assessment_id TEXT,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_targets_project ON targets(project_id);
CREATE INDEX IF NOT EXISTS idx_assessments_target ON assessments(target_id);
CREATE INDEX IF NOT EXISTS idx_proposals_assessment ON proposals(assessment_id);
CREATE INDEX IF NOT EXISTS idx_findings_assessment ON findings(assessment_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_assessment ON audit_logs(assessment_id);
"""


async def get_db_path() -> Path:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    return settings.DATABASE_PATH


async def init_db() -> None:
    """Initializes the SQLite database tables and executes migrations if needed."""
    db_path = await get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.executescript(SCHEMA_SQL)

        # Dynamic migration for targets table if needed
        async with db.execute("PRAGMA table_info(targets);") as cursor:
            target_columns = {row[1] for row in await cursor.fetchall()}

        if "environment_mode" not in target_columns:
            await db.execute("ALTER TABLE targets ADD COLUMN environment_mode TEXT NOT NULL DEFAULT 'live';")

        # Clearly separate MOCK from LIVE targets; never let acme.local be a default production target
        await db.execute(
            "UPDATE targets SET environment_mode = 'mock' WHERE authorized_domains LIKE '%acme.local%' OR base_urls LIKE '%acme.local%';"
        )
        await db.execute(
            "UPDATE targets SET environment_mode = 'live' WHERE authorized_domains LIKE '%matami.tawassl.com%';"
        )

        # Dynamic migration for findings table if needed
        async with db.execute("PRAGMA table_info(findings);") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}

        if "result_type" not in columns:
            await db.execute("ALTER TABLE findings ADD COLUMN result_type TEXT NOT NULL DEFAULT 'finding';")
        if "confirmed_vulnerability" not in columns:
            await db.execute("ALTER TABLE findings ADD COLUMN confirmed_vulnerability INTEGER NOT NULL DEFAULT 0;")
        if "sensitive_file_content_verified" not in columns:
            await db.execute("ALTER TABLE findings ADD COLUMN sensitive_file_content_verified INTEGER NOT NULL DEFAULT 0;")
        if "evidence_hash" not in columns:
            await db.execute("ALTER TABLE findings ADD COLUMN evidence_hash TEXT;")

        # Create indexes after columns are guaranteed to exist
        await db.execute("CREATE INDEX IF NOT EXISTS idx_findings_result_type ON findings(result_type);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_findings_evidence_hash ON findings(evidence_hash);")

        # Re-align existing records with classification rules
        await db.execute(
            "UPDATE findings SET result_type = 'observation', confirmed_vulnerability = 0, sensitive_file_content_verified = 0 "
            "WHERE severity = 'info' OR status = 'observation' OR title LIKE '%SPA%' OR title LIKE '%Fallback%';"
        )
        # Remediate any false positive .env findings that were marked as vulnerability without verified content
        await db.execute(
            "UPDATE findings SET result_type = 'observation', confirmed_vulnerability = 0, sensitive_file_content_verified = 0, "
            "title = 'Single Page Application (SPA) HTML Fallback on Unknown Routes', "
            "remediation = 'Optionally configure reverse proxy to return explicit 404 for sensitive file extensions.' "
            "WHERE title LIKE '%Environment File%' AND sensitive_file_content_verified = 0;"
        )
        await db.execute(
            "UPDATE findings SET result_type = 'finding', confirmed_vulnerability = 1 "
            "WHERE status = 'confirmed' AND severity IN ('critical', 'high', 'medium', 'low') "
            "AND title NOT LIKE '%SPA%' AND title NOT LIKE '%Fallback%' AND title NOT LIKE '%Robots.txt%' AND title NOT LIKE '%Environment File%';"
        )
        await db.execute(
            "UPDATE findings SET result_type = 'passed_control', confirmed_vulnerability = 0 "
            "WHERE status IN ('passed_control', 'pass') OR title LIKE '%Protected%' OR title LIKE '%Enforced%';"
        )
        await db.commit()
    logger.info("Database schema initialized and verified at %s", db_path)


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """FastAPI dependency to provide an aiosqlite database connection."""
    db_path = await get_db_path()
    db = await aiosqlite.connect(db_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON;")
    try:
        yield db
    finally:
        await db.close()
