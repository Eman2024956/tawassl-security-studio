import json
import hashlib
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.core.models import ProposalResponse, ProposalDecision

router = APIRouter(prefix="/api/approvals", tags=["Command Proposals & Approvals"])


def compute_proposal_hash(assessment_id: str, tool_name: str, arguments: dict) -> str:
    """Computes deterministic SHA-256 hash of proposal parameters to prevent tampering."""
    serialized = json.dumps({"assessment_id": assessment_id, "tool_name": tool_name, "args": arguments}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@router.get("", response_model=List[ProposalResponse])
async def list_proposals(
    assessment_id: str | None = None,
    status_filter: str | None = None,
    db: aiosqlite.Connection = Depends(get_db)
):
    """List proposals awaiting human review or already processed."""
    query = """
    SELECT id, assessment_id, tool_name, arguments_json, arguments_hash,
           purpose, side_effects, resource_limits_json, status, approved_by,
           approved_at, consumed_at, created_at
    FROM proposals
    """
    conditions = []
    params = []
    if assessment_id:
        conditions.append("assessment_id = ?")
        params.append(assessment_id)
    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"

    async with db.execute(query, tuple(params)) as cursor:
        rows = await cursor.fetchall()
        return [
            ProposalResponse(
                id=row["id"],
                assessment_id=row["assessment_id"],
                tool_name=row["tool_name"],
                arguments=json.loads(row["arguments_json"]),
                arguments_hash=row["arguments_hash"],
                purpose=row["purpose"],
                side_effects=row["side_effects"],
                resource_limits=json.loads(row["resource_limits_json"]),
                status=row["status"],
                approved_by=row["approved_by"],
                approved_at=str(row["approved_at"]) if row["approved_at"] else None,
                consumed_at=str(row["consumed_at"]) if row["consumed_at"] else None,
                created_at=str(row["created_at"])
            )
            for row in rows
        ]


@router.post("/{proposal_id}/decide", response_model=ProposalResponse)
async def decide_proposal(
    proposal_id: str,
    decision: ProposalDecision,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Approve, reject, or stop a command proposal."""
    async with db.execute(
        "SELECT id, assessment_id, tool_name, arguments_json, arguments_hash, status FROM proposals WHERE id = ?",
        (proposal_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
        if row["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Proposal is already {row['status']}. Changed arguments require a new proposal."
            )

    now = datetime.now(timezone.utc).isoformat()
    new_status = "approved" if decision.decision == "approve" else "rejected"
    await db.execute(
        "UPDATE proposals SET status = ?, approved_by = 'local_user', approved_at = ? WHERE id = ?",
        (new_status, now, proposal_id)
    )

    # If decision is 'stop', also cancel the parent assessment
    if decision.decision == "stop":
        await db.execute(
            "UPDATE assessments SET status = 'cancelled', completed_at = ? WHERE id = ?",
            (now, row["assessment_id"])
        )

    await db.commit()

    async with db.execute(
        """
        SELECT id, assessment_id, tool_name, arguments_json, arguments_hash,
               purpose, side_effects, resource_limits_json, status, approved_by,
               approved_at, consumed_at, created_at
        FROM proposals WHERE id = ?
        """,
        (proposal_id,)
    ) as cursor:
        updated = await cursor.fetchone()
        return ProposalResponse(
            id=updated["id"],
            assessment_id=updated["assessment_id"],
            tool_name=updated["tool_name"],
            arguments=json.loads(updated["arguments_json"]),
            arguments_hash=updated["arguments_hash"],
            purpose=updated["purpose"],
            side_effects=updated["side_effects"],
            resource_limits=json.loads(updated["resource_limits_json"]),
            status=updated["status"],
            approved_by=updated["approved_by"],
            approved_at=str(updated["approved_at"]) if updated["approved_at"] else None,
            consumed_at=str(updated["consumed_at"]) if updated["consumed_at"] else None,
            created_at=str(updated["created_at"])
        )
