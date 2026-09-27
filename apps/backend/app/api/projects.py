import uuid
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.core.models import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: aiosqlite.Connection = Depends(get_db)):
    """List all workspace projects."""
    async with db.execute("SELECT id, name, description, created_at, updated_at FROM projects ORDER BY created_at DESC") as cursor:
        rows = await cursor.fetchall()
        return [
            ProjectResponse(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"])
            )
            for row in rows
        ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Create a new project."""
    project_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO projects (id, name, description) VALUES (?, ?, ?)",
        (project_id, data.name, data.description)
    )
    await db.commit()

    async with db.execute("SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?", (project_id,)) as cursor:
        row = await cursor.fetchone()
        return ProjectResponse(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """Get project details by ID."""
    async with db.execute("SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?", (project_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectResponse(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )
