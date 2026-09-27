import pytest
from httpx import AsyncClient, ASGITransport
from apps.backend.app.main import app
from apps.backend.app.core.database import init_db


@pytest.mark.asyncio
async def test_full_api_workflow():
    await init_db()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000",
        headers={
            "Host": "127.0.0.1",
            "Origin": "http://localhost:3000",
            "X-Tawassl-Client": "studio-test"
        }
    ) as client:
        # 1. Check Catalog
        catalog_res = await client.get("/api/catalog")
        assert catalog_res.status_code == 200
        modules = catalog_res.json()
        assert len(modules) >= 5
        assert any(m["id"] == "mod-sec-headers" for m in modules)

        # 2. Create Project
        proj_res = await client.post("/api/projects", json={
            "name": "Acme Core Platform",
            "description": "Primary internal services & external portal"
        })
        assert proj_res.status_code == 201
        project = proj_res.json()
        assert project["name"] == "Acme Core Platform"
        project_id = project["id"]

        # 3. Create Target
        target_res = await client.post("/api/targets", json={
            "project_id": project_id,
            "name": "Matami Web Platform",
            "target_type": "website",
            "environment_mode": "live",
            "authorized_domains": ["matami.tawassl.com"],
            "base_urls": ["https://matami.tawassl.com"],
            "allowed_ports": [443, 80],
            "allow_subdomains": False,
            "exclusions": ["/admin/billing", "/logout"]
        })
        assert target_res.status_code == 201
        target = target_res.json()
        assert target["authorized_domains"] == ["matami.tawassl.com"]
        assert target["environment_mode"] == "live"
        target_id = target["id"]

        # 4. Create Assessment with Observe profile and hard limits
        assess_res = await client.post("/api/assessments", json={
            "project_id": project_id,
            "target_id": target_id,
            "name": "Initial Baseline Observation",
            "profile": "observe",
            "ai_provider": "mock",
            "model_id": "mock-sec-v1",
            "max_steps": 15,
            "max_requests": 30,
            "max_tool_calls": 20
        })
        assert assess_res.status_code == 201
        assessment = assess_res.json()
        assert assessment["status"] == "queued"
        assert assessment["max_steps"] == 15
        assessment_id = assessment["id"]

        # 5. Stop Assessment
        stop_res = await client.post(f"/api/assessments/{assessment_id}/stop")
        assert stop_res.status_code == 200
        stopped = stop_res.json()
        assert stopped["status"] == "cancelled"
