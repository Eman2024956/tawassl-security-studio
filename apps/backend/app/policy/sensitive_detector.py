"""
Content-aware sensitive file & dotenv verification module for Tawassl Security Studio.

Prevents false positives on endpoints like `/.env` by strictly verifying response
content-type, HTML/SPA structure, and authentic dotenv syntax before classifying
any response as a confirmed security finding.
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# Regex for credible dotenv key:
# Must start with letter/underscore, followed by uppercase letters, digits, or underscores.
# Typically at least 2 characters, up to 64.
DOTENV_KEY_REGEX = re.compile(r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]{1,63})\s*=\s*(.*)$')

# High-confidence credential/configuration key names commonly found in genuine .env files
CREDIBLE_CONFIG_KEYWORDS = {
    "APP_ENV", "APP_KEY", "APP_SECRET", "APP_DEBUG", "APP_URL",
    "DATABASE_URL", "DB_CONNECTION", "DB_HOST", "DB_PORT", "DB_DATABASE", "DB_USERNAME", "DB_PASSWORD", "DB_NAME", "DB_USER", "DB_PASS",
    "REDIS_HOST", "REDIS_PASSWORD", "REDIS_PORT", "REDIS_URL",
    "API_KEY", "API_SECRET", "SECRET_KEY", "JWT_SECRET", "JWT_KEY", "SESSION_SECRET",
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION", "AWS_REGION", "AWS_BUCKET",
    "STRIPE_KEY", "STRIPE_SECRET", "MAIL_MAILER", "MAIL_HOST", "MAIL_PORT", "MAIL_USERNAME", "MAIL_PASSWORD",
    "CLIENT_ID", "CLIENT_SECRET", "AUTH_SECRET", "ENCRYPTION_KEY", "TOKEN", "PASSWORD"
}

# HTML tags and structure indicators that disqualify content from being a raw .env file
HTML_TAG_PATTERNS = [
    re.compile(r'<!DOCTYPE\s+html', re.IGNORECASE),
    re.compile(r'<html[\s>]', re.IGNORECASE),
    re.compile(r'<\/html>', re.IGNORECASE),
    re.compile(r'<head[\s>]', re.IGNORECASE),
    re.compile(r'<body[\s>]', re.IGNORECASE),
    re.compile(r'<script[\s>]', re.IGNORECASE),
    re.compile(r'<meta[\s>]', re.IGNORECASE),
    re.compile(r'<title[\s>]', re.IGNORECASE),
    re.compile(r'<div[\s>]', re.IGNORECASE),
]

# SPA Framework root elements
SPA_ROOT_PATTERNS = [
    re.compile(r'<div[^>]+id=["\'](?:root|app|__next|__nuxt|main-content)["\']', re.IGNORECASE),
    re.compile(r'window\.__NEXT_DATA__', re.IGNORECASE),
    re.compile(r'window\.__INITIAL_STATE__', re.IGNORECASE),
    re.compile(r'<noscript>', re.IGNORECASE),
]

# Login page indicators in HTML
LOGIN_PATTERNS = [
    re.compile(r'<form[^>]+>', re.IGNORECASE),
    re.compile(r'type=["\']password["\']', re.IGNORECASE),
    re.compile(r'(?:login|sign\s*in|authenticate|log\s*in)', re.IGNORECASE),
]

# Custom 404 page indicators in HTML
CUSTOM_404_PATTERNS = [
    re.compile(r'(?:404\s*not\s*found|page\s*not\s*found|could\s*not\s*be\s*found|does\s*not\s*exist)', re.IGNORECASE),
    re.compile(r'<title>[^<]*(?:404|not\s*found)[^<]*<\/title>', re.IGNORECASE),
]


@dataclass
class SensitiveFileResult:
    sensitive_file_content_verified: bool
    result_type: str  # 'passed_control' | 'observation' | 'finding' | 'inconclusive'
    confirmed_vulnerability: bool
    classification_reason: str
    spa_detected: bool
    html_detected: bool
    verified_variable_count: int
    redacted_declarations: List[str]
    title: str
    severity: str  # 'info' | 'low' | 'medium' | 'high' | 'critical'
    confidence: str  # 'confirmed' | 'probable' | 'low'
    finding_status: str  # 'confirmed' | 'observation' | 'inconclusive'
    observed_result: str
    expected_result: str
    preconditions: str
    reproduction_steps: str
    impact: Optional[str]
    remediation: Optional[str]
    metadata: Dict[str, str] = field(default_factory=dict)


def redact_dotenv_declaration(key: str, val: str) -> str:
    """Safely redacts value from KEY=VALUE assignment so secrets are never stored."""
    trimmed = val.strip()
    # Strip quotes if wrapped
    if (trimmed.startswith('"') and trimmed.endswith('"')) or (trimmed.startswith("'") and trimmed.endswith("'")):
        return f"{key}=[REDACTED]"
    return f"{key}=[REDACTED]"


def parse_dotenv_evidence(body: str) -> Tuple[List[str], List[str]]:
    """
    Parses body and extracts verified dotenv declarations.
    Returns: (raw_keys, redacted_declarations)
    
    Rejects:
    - Lines that look like HTML tags, JS code, JSON, CSS, or prose.
    - Key names that contain illegal characters.
    """
    if not body or not body.strip():
        return [], []

    raw_keys = []
    redacted_lines = []

    lines = body.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # If line contains HTML tag characters, it cannot be a clean dotenv line
        if "<" in line or ">" in line or "{" in line or "}" in line or ";" in line:
            continue

        match = DOTENV_KEY_REGEX.match(line)
        if match:
            key = match.group(1)
            val = match.group(2)
            
            # Key should be alphanumeric/underscore and typically uppercase or standard identifier
            # Avoid matching random prose like "for example = something"
            if " " in key:
                continue

            raw_keys.append(key)
            redacted_lines.append(redact_dotenv_declaration(key, val))

    return raw_keys, redacted_lines


def is_html_or_spa_response(
    content_type: str,
    body: str,
    root_body: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Detects whether the HTTP response is an HTML page or SPA routing fallback.
    Returns: (is_spa, reason_string)
    """
    ct = (content_type or "").lower()
    lower_body = (body or "").lower()

    # 1. MIME type indication
    if "text/html" in ct or "application/xhtml+xml" in ct:
        pass
    
    # 2. Structural HTML tag presence
    html_tags_matched = [p.pattern for p in HTML_TAG_PATTERNS if p.search(lower_body)]
    if len(html_tags_matched) >= 2 or "<!doctype html" in lower_body or "<html" in lower_body:
        # Check SPA root elements
        for spa_p in SPA_ROOT_PATTERNS:
            if spa_p.search(lower_body):
                return True, "HTML SPA client-side router root container detected"

        # Check Root Hash / Fingerprint similarity if root_body provided
        if root_body:
            root_hash = hashlib.sha256(root_body.strip().encode("utf-8")).hexdigest()
            current_hash = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()
            if root_hash == current_hash:
                return True, "Identical HTML hash match with root endpoint (SPA wildcard routing)"
            
            # Compare stripped length / title tag
            root_title = re.search(r'<title>([^<]+)<\/title>', root_body, re.IGNORECASE)
            curr_title = re.search(r'<title>([^<]+)<\/title>', body, re.IGNORECASE)
            if root_title and curr_title and root_title.group(1) == curr_title.group(1):
                return True, f"Identical HTML title tag matched root page: '{root_title.group(1)}'"

        return True, "HTML document template returned"

    return False, "Not an HTML/SPA response"


def classify_sensitive_file_response(
    path: str,
    status_code: int,
    headers: Dict[str, str],
    body: str,
    root_body: Optional[str] = None
) -> SensitiveFileResult:
    """
    Strict content-aware classifier for sensitive files (e.g., /.env).
    
    Adheres strictly to the 10 core requirements:
    - Never classify from status alone.
    - 404/403 -> PASS
    - 200 + HTML/SPA -> NOT VULNERABLE (observation or passed_control)
    - 200 + HTML with config strings -> NOT VULNERABLE
    - 200 + genuine plaintext dotenv -> CONFIRMED FINDING
    - Require sensitive_file_content_verified = True for findings
    - Never include secret values
    - No "rotate secrets" remediation unless confirmed
    """
    content_type = headers.get("content-type", "").lower()
    ct_clean = content_type.split(";")[0].strip()
    is_html, html_reason = is_html_or_spa_response(content_type, body, root_body)
    raw_keys, redacted_lines = parse_dotenv_evidence(body)

    # 1. Clean Access Restrictions (401, 403, 404)
    if status_code in (401, 403, 404):
        return SensitiveFileResult(
            sensitive_file_content_verified=False,
            result_type="passed_control",
            confirmed_vulnerability=False,
            classification_reason=f"HTTP {status_code} properly restricted access without leaking configuration.",
            spa_detected=False,
            html_detected=is_html,
            verified_variable_count=0,
            redacted_declarations=[],
            title="Sensitive Environment File Protected (/.env)",
            severity="info",
            confidence="confirmed",
            finding_status="confirmed",
            observed_result=f"Server returned HTTP {status_code}; access to sensitive file {path} is safely denied or non-existent.",
            expected_result="HTTP 403 Forbidden or HTTP 404 Not Found.",
            preconditions=f"Public HTTP request to {path}.",
            reproduction_steps=f"1. Send GET request to {path}\n2. Server returns HTTP {status_code} (Protected).",
            impact=None,
            remediation=None,
            metadata={"status_code": str(status_code), "content_type": content_type}
        )

    # 2. HTTP 200: HTML / SPA Response Handling
    if status_code == 200 and is_html:
        # Check if it's a custom 404 error page rendered as HTML
        is_custom_404 = any(p.search(body) for p in CUSTOM_404_PATTERNS)
        # Check if it's a login/portal page
        is_login_page = any(p.search(body) for p in LOGIN_PATTERNS)

        if is_custom_404:
            return SensitiveFileResult(
                sensitive_file_content_verified=False,
                result_type="passed_control",
                confirmed_vulnerability=False,
                classification_reason="Custom 404 HTML error page returned under HTTP 200.",
                spa_detected=True,
                html_detected=True,
                verified_variable_count=0,
                redacted_declarations=[],
                title="Sensitive File Safely Handled (Custom 404 HTML)",
                severity="info",
                confidence="confirmed",
                finding_status="confirmed",
                observed_result="Server responded with HTTP 200 serving a custom '404 Not Found' HTML page template rather than raw file contents.",
                expected_result="Expected 404/403 or custom 404 handler.",
                preconditions=f"Requesting non-existent path {path}.",
                reproduction_steps=f"1. Send GET request to {path}\n2. Observe custom 404 HTML error body.",
                impact=None,
                remediation=None,
                metadata={"status_code": "200", "content_type": content_type, "spa_reason": html_reason}
            )

        if is_login_page:
            return SensitiveFileResult(
                sensitive_file_content_verified=False,
                result_type="observation",
                confirmed_vulnerability=False,
                classification_reason="Application redirected/rendered login portal on sensitive path.",
                spa_detected=True,
                html_detected=True,
                verified_variable_count=0,
                redacted_declarations=[],
                title="Authentication Portal Rendered on Route (/.env)",
                severity="info",
                confidence="confirmed",
                finding_status="observation",
                observed_result="Server responded with HTTP 200 serving a login or authentication page instead of raw configuration.",
                expected_result="Access to raw dotfile denied.",
                preconditions=f"Unauthenticated request to {path}.",
                reproduction_steps=f"1. Send GET request to {path}\n2. Observe HTML login form rendered.",
                impact="Informational finding. No secrets or environment configuration disclosed.",
                remediation=None,
                metadata={"status_code": "200", "content_type": content_type}
            )

        # Standard SPA / index.html Fallback:
        # Even if HTML has text like API_KEY=example or JS bundle references, do NOT assume .env exposure!
        return SensitiveFileResult(
            sensitive_file_content_verified=False,
            result_type="observation",
            confirmed_vulnerability=False,
            classification_reason=f"SPA client-side HTML fallback: {html_reason}. No valid dotenv structure.",
            spa_detected=True,
            html_detected=True,
            verified_variable_count=0,
            redacted_declarations=[],
            title="Single Page Application (SPA) HTML Fallback on Unknown Routes",
            severity="info",
            confidence="confirmed",
            finding_status="observation",
            observed_result=f"Server responds with HTTP 200 serving client-side HTML application template ({html_reason}). No environment variables were disclosed.",
            expected_result="Expected HTTP 404 Not Found or HTTP 403 Forbidden for non-existent sensitive file paths.",
            preconditions=f"Requesting non-existent sensitive path {path} on an SPA platform.",
            reproduction_steps=f"1. Send GET request to {path}\n2. Observe HTTP 200 with Content-Type '{ct_clean}' serving HTML shell.",
            impact="Informational observation. This is normal behavior for client-side routed SPAs (React, Next.js, Vue) and does NOT represent an environment variable leak.",
            remediation="Optionally configure reverse proxy (e.g. Nginx, Cloudflare, Vercel) to return explicit 404/403 for dotfiles (e.g. .env, .git).",
            metadata={"status_code": "200", "content_type": content_type, "spa_reason": html_reason}
        )

    # 3. HTTP 200: JavaScript / JSON Application Data (Not Dotenv)
    if status_code == 200 and ("javascript" in ct_clean or "json" in ct_clean or body.strip().startswith("{") or body.strip().startswith("[")):
        return SensitiveFileResult(
            sensitive_file_content_verified=False,
            result_type="inconclusive",
            confirmed_vulnerability=False,
            classification_reason="Response is JavaScript or JSON application data, not dotenv plaintext.",
            spa_detected=False,
            html_detected=False,
            verified_variable_count=0,
            redacted_declarations=[],
            title="Non-Configuration Response on Route (/.env)",
            severity="info",
            confidence="confirmed",
            finding_status="inconclusive",
            observed_result=f"Server returned HTTP 200 with Content-Type '{ct_clean}'. Payload is application code/data, not a plaintext dotenv file.",
            expected_result="Expected 404 or 403.",
            preconditions=f"Request to {path}.",
            reproduction_steps=f"1. Request {path}\n2. Observe non-dotenv content-type: {ct_clean}",
            impact=None,
            remediation=None,
            metadata={"status_code": "200", "content_type": content_type}
        )

    # 4. HTTP 200: Genuine Dotenv Verification
    # Must NOT be HTML/SPA, and must have verified dotenv lines.
    # To confirm genuine dotenv:
    # Requires at least 2 credible dotenv declarations, OR at least 1 keyword matching known high-value configs.
    has_known_config_key = any(k.upper() in CREDIBLE_CONFIG_KEYWORDS for k in raw_keys)
    is_credible_dotenv = (len(raw_keys) >= 2) or (len(raw_keys) >= 1 and has_known_config_key)

    if status_code == 200 and not is_html and is_credible_dotenv:
        var_count = len(redacted_lines)
        return SensitiveFileResult(
            sensitive_file_content_verified=True,
            result_type="finding",
            confirmed_vulnerability=True,
            classification_reason=f"Verified genuine plaintext dotenv configuration containing {var_count} configuration variable(s).",
            spa_detected=False,
            html_detected=False,
            verified_variable_count=var_count,
            redacted_declarations=redacted_lines,
            title="Exposed Sensitive Environment File (/.env)",
            severity="critical",
            confidence="confirmed",
            finding_status="confirmed",
            observed_result=f"Server returned unmasked plaintext dotenv configuration with {var_count} verified variable declaration(s): {', '.join(k + '=[REDACTED]' for k in raw_keys[:5])}",
            expected_result="HTTP 404 Not Found or HTTP 403 Forbidden.",
            preconditions=f"Public HTTP access to {path}.",
            reproduction_steps=f"1. Send GET request to {path}\n2. Server responds with HTTP 200 and plaintext configuration lines: {', '.join(k + '=[REDACTED]' for k in raw_keys[:3])}",
            impact="Critical exposure: Database credentials, third-party API keys, and application secrets can be immediately used to compromise backend systems and infrastructure.",
            remediation="Immediately restrict public web access to .env and all dotfiles in web server configuration, and rotate all disclosed credentials and API keys.",
            metadata={"status_code": "200", "content_type": content_type, "verified_keys": ",".join(raw_keys)}
        )

    # 5. Ambiguous / Inconclusive Response
    return SensitiveFileResult(
        sensitive_file_content_verified=False,
        result_type="inconclusive",
        confirmed_vulnerability=False,
        classification_reason=f"HTTP {status_code} response with Content-Type '{ct_clean}' could not be definitively verified as dotenv configuration.",
        spa_detected=False,
        html_detected=is_html,
        verified_variable_count=0,
        redacted_declarations=[],
        title="Ambiguous Response on Sensitive Path (/.env)",
        severity="info",
        confidence="low",
        finding_status="inconclusive",
        observed_result=f"Server returned HTTP {status_code} ({ct_clean}) without verified dotenv format or explicit denial.",
        expected_result="Definitive HTTP 404 Not Found or HTTP 403 Forbidden.",
        preconditions=f"Public HTTP request to {path}.",
        reproduction_steps=f"1. Send GET request to {path}\n2. Note ambiguous response format.",
        impact=None,
        remediation="Manually inspect the endpoint to ensure no internal application data or server configuration is exposed.",
        metadata={"status_code": str(status_code), "content_type": content_type}
    )
