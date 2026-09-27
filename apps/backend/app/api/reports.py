import json
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse, JSONResponse
import aiosqlite
from apps.backend.app.core.database import get_db
from apps.backend.app.reports.exporter import export_markdown_report, export_json_report, export_sarif_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{assessment_id}")
async def get_assessment_report(
    assessment_id: str,
    format: str = Query("markdown", pattern="^(markdown|json|sarif)$"),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Generates and exports an assessment report in Markdown, JSON, or SARIF 2.1.0."""
    # 1. Fetch assessment
    async with db.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)) as cursor:
        assess_row = await cursor.fetchone()
        if not assess_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
        assessment_data = dict(assess_row)

    # 2. Fetch target
    async with db.execute("SELECT * FROM targets WHERE id = ?", (assessment_data["target_id"],)) as cursor:
        target_row = await cursor.fetchone()
        target_data = dict(target_row) if target_row else {}
        if target_data.get("authorized_domains"):
            target_data["authorized_domains"] = json.loads(target_data["authorized_domains"])

    # 3. Fetch findings
    async with db.execute("SELECT * FROM findings WHERE assessment_id = ?", (assessment_id,)) as cursor:
        findings_rows = await cursor.fetchall()
        findings_list = [dict(r) for r in findings_rows]
        for f in findings_list:
            if f.get("evidence_json"):
                f["evidence"] = json.loads(f["evidence_json"])

    skipped = ["mod-ssrf-validation (Not implemented in v0.1)", "mod-csrf-state (Prerequisites missing)"]

    if format == "markdown":
        content = export_markdown_report(assessment_data, target_data, findings_list, skipped)
        return PlainTextResponse(content=content, media_type="text/markdown")
    elif format == "json":
        data = export_json_report(assessment_data, target_data, findings_list, skipped)
        return JSONResponse(content=data)
    else:  # sarif
        sarif_data = export_sarif_report(assessment_data, target_data, findings_list)
        return JSONResponse(content=sarif_data)
