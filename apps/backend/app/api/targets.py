import uuid
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.core.models import TargetCreate, TargetResponse

router = APIRouter(prefix="/api/targets", tags=["Targets"])


@router.get("", response_model=List[TargetResponse])
async def list_targets(project_id: str | None = None, db: aiosqlite.Connection = Depends(get_db)):
    """List all registered assessment targets, optionally filtered by project_id."""
    query = "SELECT id, project_id, name, target_type, authorized_domains, base_urls, allowed_ports, allow_subdomains, exclusions, source_path, created_at FROM targets"
    params = ()
    if project_id:
        query += " WHERE project_id = ?"
        params = (project_id,)
    query += " ORDER BY created_at DESC"

    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [
            TargetResponse(
                id=row["id"],
                project_id=row["project_id"],
                name=row["name"],
                target_type=row["target_type"],
                authorized_domains=json.loads(row["authorized_domains"]),
                base_urls=json.loads(row["base_urls"]),
                allowed_ports=json.loads(row["allowed_ports"]) if row["allowed_ports"] else [80, 443],
                allow_subdomains=bool(row["allow_subdomains"]),
                exclusions=json.loads(row["exclusions"]) if row["exclusions"] else [],
                source_path=row["source_path"],
                created_at=str(row["created_at"])
            )
            for row in rows
        ]


@router.post("", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(data: TargetCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Register an assessment target with an explicit, validated scope."""
    # Ensure parent project exists
    async with db.execute("SELECT id FROM projects WHERE id = ?", (data.project_id,)) as cursor:
        if not await cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent project does not exist")

    target_id = str(uuid.uuid4())
    await db.execute(
        """
        INSERT INTO targets (
            id, project_id, name, target_type, authorized_domains, base_urls,
            allowed_ports, allow_subdomains, exclusions, source_path, auth_config
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            target_id,
            data.project_id,
            data.name,
            data.target_type,
            json.dumps(data.authorized_domains),
            json.dumps(data.base_urls),
            json.dumps(data.allowed_ports or [80, 443]),
            1 if data.allow_subdomains else 0,
            json.dumps(data.exclusions or []),
            data.source_path,
            json.dumps(data.auth_config) if data.auth_config else None
        )
    )
    await db.commit()

    async with db.execute(
        "SELECT id, project_id, name, target_type, authorized_domains, base_urls, allowed_ports, allow_subdomains, exclusions, source_path, created_at FROM targets WHERE id = ?",
        (target_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return TargetResponse(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            target_type=row["target_type"],
            authorized_domains=json.loads(row["authorized_domains"]),
            base_urls=json.loads(row["base_urls"]),
            allowed_ports=json.loads(row["allowed_ports"]),
            allow_subdomains=bool(row["allow_subdomains"]),
            exclusions=json.loads(row["exclusions"]),
            source_path=row["source_path"],
            created_at=str(row["created_at"])
        )
