import pytest
from httpx import AsyncClient, ASGITransport
from apps.backend.app.main import app
from apps.backend.app.core.config import settings


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000",
        headers={"Host": "127.0.0.1"}
    ) as client:
        # Trigger startup lifespan manually or request endpoint
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["app_name"] == "Tawassl Security Studio"
        assert data["version"] == settings.APP_VERSION
        assert "database" in data
        assert "safety_defaults" in data
        assert data["safety_defaults"]["max_steps"] == 20


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000",
        headers={"Host": "127.0.0.1"}
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tawassl Security Studio"


@pytest.mark.asyncio
async def test_host_header_validation():
    # Attempting to access with an untrusted host header (e.g., DNS rebinding attempt)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://attacker-controlled.site",
        headers={"Host": "attacker-controlled.site"}
    ) as client:
        response = await client.get("/api/health")
        assert response.status_code == 403
        assert "Untrusted Host" in response.text
