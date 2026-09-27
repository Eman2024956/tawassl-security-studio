import pytest
from apps.backend.app.policy.models import ScopeRule
from apps.backend.app.tools.controlled_http import ControlledHTTPClient


@pytest.mark.asyncio
async def test_controlled_http_scope_denial():
    # Scope for matami.tawassl.com
    scope = ScopeRule(
        authorized_domains=["matami.tawassl.com"],
        base_urls=["https://matami.tawassl.com"]
    )
    client = ControlledHTTPClient(scope=scope)

    # Calling an unauthorized external domain
    res = await client.inspect_url("https://unauthorized-external-site.com/api")
    assert res["status"] == "policy_denied"
    assert "not authorized in scope" in res["reason"]


@pytest.mark.asyncio
async def test_controlled_http_ssrf_block():
    # Scope with loopback attempt
    scope = ScopeRule(
        authorized_domains=["127.0.0.1"],
        base_urls=["http://127.0.0.1:8000"],
        allowed_ports=[8000]
    )
    client = ControlledHTTPClient(scope=scope)

    # Attempting to query loopback
    res = await client.inspect_url("http://127.0.0.1:8000/api/health")
    assert res["status"] == "policy_denied"
    assert res["violation_code"] == "SSRF_PROHIBITED_IP"
