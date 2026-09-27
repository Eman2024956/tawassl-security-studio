import uuid
import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.core.models import FindingResponse
from apps.backend.app.core.security import redact_secrets

router = APIRouter(prefix="/api/findings", tags=["Findings & Evidence"])

VALID_STATUSES = [
    "observation", "suspected", "confirmed",
    "inconclusive", "false_positive", "fixed", "retest_failed"
]


@router.get("", response_model=List[FindingResponse])
async def list_findings(
    assessment_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_db)
):
    """List findings with severity, confidence, and associated evidence references."""
    query = """
    SELECT id, assessment_id, title, category, affected_asset, severity,
           confidence, status, preconditions, reproduction_steps, expected_result,
           observed_result, impact, remediation, evidence_json, created_at, updated_at
    FROM findings
    """
    conditions = []
    params = []
    if assessment_id:
        conditions.append("assessment_id = ?")
        params.append(assessment_id)
    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)
    if severity_filter:
        conditions.append("severity = ?")
        params.append(severity_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"

    async with db.execute(query, tuple(params)) as cursor:
        rows = await cursor.fetchall()
        return [
            FindingResponse(
                id=row["id"],
                assessment_id=row["assessment_id"],
                title=row["title"],
                category=row["category"],
                affected_asset=row["affected_asset"],
                severity=row["severity"],
                confidence=row["confidence"],
                status=row["status"],
                preconditions=row["preconditions"],
                reproduction_steps=row["reproduction_steps"],
                expected_result=row["expected_result"],
                observed_result=row["observed_result"],
                impact=row["impact"],
                remediation=row["remediation"],
                evidence=json.loads(row["evidence_json"]),
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"])
            )
            for row in rows
        ]


@router.patch("/{finding_id}/status", response_model=FindingResponse)
async def update_finding_status(
    finding_id: str,
    new_status: str,
    retest_rationale: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Transition finding status based on verification or retest evidence."""
    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    async with db.execute("SELECT id FROM findings WHERE id = ?", (finding_id,)) as cursor:
        if not await cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE findings SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, finding_id)
    )
    await db.commit()

    async with db.execute(
        """
        SELECT id, assessment_id, title, category, affected_asset, severity,
               confidence, status, preconditions, reproduction_steps, expected_result,
               observed_result, impact, remediation, evidence_json, created_at, updated_at
        FROM findings WHERE id = ?
        """,
        (finding_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return FindingResponse(
            id=row["id"],
            assessment_id=row["assessment_id"],
            title=row["title"],
            category=row["category"],
            affected_asset=row["affected_asset"],
            severity=row["severity"],
            confidence=row["confidence"],
            status=row["status"],
            preconditions=row["preconditions"],
            reproduction_steps=row["reproduction_steps"],
            expected_result=row["expected_result"],
            observed_result=row["observed_result"],
            impact=row["impact"],
            remediation=row["remediation"],
            evidence=json.loads(row["evidence_json"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )
