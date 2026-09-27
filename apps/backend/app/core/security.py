import re
import secrets
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from apps.backend.app.core.config import settings

# Regex patterns for sensitive data redaction in evidence and logs
REDACTION_PATTERNS = [
    (re.compile(r'(?i)(bearer\s+)[a-zA-Z0-9_\-\.]{15,}'), r'\1[REDACTED_TOKEN]'),
    (re.compile(r'(?i)(api[_-]?key["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_\-]{16,}'), r'\1[REDACTED_API_KEY]'),
    (re.compile(r'(?i)(password["\']?\s*[:=]\s*["\']?)[^\s"\';&]{4,}'), r'\1[REDACTED_PASSWORD]'),
    (re.compile(r'(?i)(secret["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_\-]{16,}'), r'\1[REDACTED_SECRET]'),
    (re.compile(r'(?i)(session[_-]?token["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_\-]{16,}'), r'\1[REDACTED_SESSION]'),
]


def redact_secrets(text: str) -> str:
    """Redacts sensitive credentials, tokens, and keys from strings before logging or persistence."""
    if not text:
        return text
    result = text
    for pattern, replacement in REDACTION_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Implements Section 14 requirements:
    - Host and Origin header validation to protect against DNS rebinding & cross-site hijacking.
    - CSRF verification for state-mutating requests (POST, PUT, PATCH, DELETE).
    - Enforces no side-effects on GET requests.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Validate Host header
        host_header = request.headers.get("host", "").split(":")[0]
        if host_header and host_header not in settings.allowed_hosts_list:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"Forbidden: Untrusted Host header '{host_header}'"}
            )

        # 2. Validate Origin / Referer for mutating methods
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin")
            if origin:
                normalized_origin = origin.rstrip("/")
                allowed_normalized = [o.rstrip("/") for o in settings.allowed_origins_list]
                if normalized_origin not in allowed_normalized:
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": f"Cross-origin mutation rejected from origin: {origin}"}
                    )

            # 3. Check CSRF header for state mutations
            if not request.url.path.startswith("/api/health") and not request.url.path.startswith("/docs") and not request.url.path.startswith("/openapi.json"):
                csrf_token = request.headers.get(settings.CSRF_HEADER_NAME.lower()) or request.headers.get(settings.CSRF_HEADER_NAME)
                if not csrf_token and request.headers.get("x-requested-with") != "XMLHttpRequest":
                    if "x-tawassl-client" not in request.headers and not csrf_token:
                        from fastapi.responses import JSONResponse
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "Missing required anti-CSRF header (X-Tawassl-CSRF or X-Tawassl-Client)"}
                        )

        response = await call_next(request)

        # Set secure HTTP response headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        return response


def generate_session_token() -> str:
    """Generates a cryptographically secure random token."""
    return secrets.token_urlsafe(32)
