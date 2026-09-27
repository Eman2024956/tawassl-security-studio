import httpx
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from apps.backend.app.policy.models import ScopeRule
from apps.backend.app.policy.network_guard import validate_url_against_scope
from apps.backend.app.core.security import redact_secrets


class ControlledHTTPClient:
    """
    Safe HTTP client enforcing zero-trust scope and egress restrictions:
    - Verifies scope & SSRF blocklists on initial URL AND on every redirect Location.
    - TLS certificate verification strictly enabled (verify=True).
    - Captures raw header snapshots and redacts credentials before returning.
    """

    def __init__(self, scope: ScopeRule, timeout_seconds: float = 15.0):
        self.scope = scope
        self.timeout_seconds = timeout_seconds

    async def inspect_url(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = False
    ) -> Dict[str, Any]:
        """Performs controlled inspection of a single target endpoint."""
        # 1. Scope & SSRF check on initial URL
        policy_res = validate_url_against_scope(url, self.scope)
        if not policy_res.allowed:
            return {
                "status": "policy_denied",
                "url": url,
                "reason": policy_res.reason,
                "violation_code": policy_res.violation_code
            }

        req_headers = {
            "User-Agent": "TawasslSecurityStudio/0.1.0-alpha (Authorized Security Assessment)",
            **(headers or {})
        }

        async with httpx.AsyncClient(
            verify=True,
            timeout=self.timeout_seconds,
            follow_redirects=False  # Handled manually to validate redirect targets
        ) as client:
            try:
                response = await client.request(method=method, url=url, headers=req_headers)
            except Exception as e:
                return {
                    "status": "error",
                    "url": url,
                    "error": str(e)
                }

            # Check redirect location if present
            if response.is_redirect and "location" in response.headers:
                raw_loc = response.headers["location"]
                redirect_url = urljoin(url, raw_loc)
                redirect_check = validate_url_against_scope(redirect_url, self.scope)
                if not redirect_check.allowed:
                    return {
                        "status": "redirect_escape_prevented",
                        "initial_url": url,
                        "redirect_location": redirect_url,
                        "reason": f"Redirect blocked: {redirect_check.reason}",
                        "violation_code": redirect_check.violation_code
                    }

            # Analyze security headers
            res_headers = {k.lower(): v for k, v in response.headers.items()}
            missing_security_headers = []
            if "strict-transport-security" not in res_headers:
                missing_security_headers.append("Strict-Transport-Security")
            if "content-security-policy" not in res_headers:
                missing_security_headers.append("Content-Security-Policy")
            if "x-frame-options" not in res_headers:
                missing_security_headers.append("X-Frame-Options")
            if "x-content-type-options" not in res_headers:
                missing_security_headers.append("X-Content-Type-Options")

            # Analyze cookies
            cookies_info = []
            for cookie in response.cookies.jar:
                cookies_info.append({
                    "name": cookie.name,
                    "secure": cookie.secure,
                    "httponly": cookie.has_nonstandard_attr("httponly") or "httponly" in cookie._rest,
                })

            raw_body = response.text[:4096]  # bounded body snapshot
            clean_body = redact_secrets(raw_body)

            return {
                "status": "success",
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "missing_security_headers": missing_security_headers,
                "cookies": cookies_info,
                "body_preview": clean_body
            }
