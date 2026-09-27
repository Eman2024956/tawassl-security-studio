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
