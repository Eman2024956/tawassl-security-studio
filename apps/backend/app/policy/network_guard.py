import socket
import ipaddress
from urllib.parse import urlsplit
from typing import List, Tuple, Optional
from apps.backend.app.policy.models import ScopeRule, PolicyEvaluationResult

FORBIDDEN_METADATA_IPS = {
    "169.254.169.254",  # AWS/GCP/Azure IMDS
    "fd00:ec2::254",     # AWS IPv6 IMDS
}


def is_ip_forbidden(ip_str: str) -> Tuple[bool, str]:
    """Checks whether an IP address belongs to loopback, private, link-local, or cloud metadata."""
    if ip_str in FORBIDDEN_METADATA_IPS:
        return True, "Cloud metadata endpoint is strictly prohibited"

    try:
        ip = ipaddress.ip_address(ip_str)
        # Handle IPv6-mapped IPv4 addresses (e.g. ::ffff:127.0.0.1)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped

        if ip.is_loopback:
            return True, f"Loopback address ({ip_str}) is prohibited"
        if ip.is_private:
            return True, f"Internal private IP range ({ip_str}) is prohibited"
        if ip.is_link_local:
            return True, f"Link-local address ({ip_str}) is prohibited"
        if ip.is_multicast:
            return True, f"Multicast address ({ip_str}) is prohibited"
        if ip.is_reserved:
            return True, f"Reserved address ({ip_str}) is prohibited"
        return False, ""
    except ValueError:
        return True, f"Invalid IP address format: {ip_str}"


def validate_url_against_scope(url: str, scope: ScopeRule) -> PolicyEvaluationResult:
    """
    Evaluates a candidate URL against the authorized ScopeRule.
    Enforces:
    - Empty scope denies access.
    - Scheme whitelist (http/https).
    - Userinfo confusion prevention.
    - Suffix tricks prevention.
    - Port restrictions.
    - Path exclusion rules.
    - DNS resolution to non-private IPs (preventing SSRF).
    """
    if not scope.authorized_domains and not scope.base_urls:
        return PolicyEvaluationResult(
            allowed=False,
            reason="Empty scope denies access by default.",
            violation_code="EMPTY_SCOPE_DENY"
        )

    try:
        parsed = urlsplit(url)
    except Exception as e:
        return PolicyEvaluationResult(
            allowed=False,
            reason=f"Malformed URL: {str(e)}",
            violation_code="MALFORMED_URL"
        )

    # 1. Scheme check
    if parsed.scheme.lower() not in ("http", "https"):
        return PolicyEvaluationResult(
            allowed=False,
            reason=f"Prohibited URL scheme '{parsed.scheme}'. Only http and https are permitted.",
            violation_code="INVALID_SCHEME"
        )

    # 2. Userinfo confusion check (e.g., http://victim.com@attacker.com)
    if parsed.username or parsed.password:
        return PolicyEvaluationResult(
            allowed=False,
            reason="Userinfo (username/password in URL) is prohibited to prevent authentication confusion.",
            violation_code="USERINFO_PROHIBITED"
        )

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return PolicyEvaluationResult(
            allowed=False,
            reason="URL missing valid hostname.",
            violation_code="MISSING_HOSTNAME"
        )

    # 3. Port check
    port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    allowed_ports = list(scope.allowed_ports) if scope.allowed_ports else [80, 443]

    if port not in allowed_ports:
        return PolicyEvaluationResult(
            allowed=False,
            reason=f"Port {port} is not in authorized ports list: {allowed_ports}",
            violation_code="PORT_NOT_PERMITTED"
        )

    # 4. Hostname authorized domain match & suffix trick prevention
    matched_domain = False
    auth_domains_set = {d.lower().strip() for d in scope.authorized_domains}

    for auth_clean in auth_domains_set:
        if hostname == auth_clean:
            matched_domain = True
            break
        # Subdomain match only if explicit flag is enabled
        if scope.allow_subdomains:
            if hostname.endswith("." + auth_clean):
                matched_domain = True
                break

    if not matched_domain:
        # Check base_urls prefix match
        matched_base = any(url.startswith(base.rstrip("/")) for base in scope.base_urls)
        if not matched_base:
            return PolicyEvaluationResult(
                allowed=False,
                reason=f"Hostname '{hostname}' is not authorized in scope.",
                violation_code="HOSTNAME_OUT_OF_SCOPE"
            )

    # 5. Path exclusions check
    canonical_path = parsed.path or "/"
    for exclusion in scope.exclusions:
        excl_clean = exclusion.strip()
        if excl_clean and (canonical_path == excl_clean or canonical_path.startswith(excl_clean.rstrip("/") + "/")):
            return PolicyEvaluationResult(
                allowed=False,
                reason=f"Path '{canonical_path}' matches explicit exclusion: {exclusion}",
                violation_code="EXCLUDED_PATH_MATCH"
            )

    # 6. DNS Resolution & SSRF check
    try:
        addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
        resolved_ips = set()
        for family, socktype, proto, canonname, sockaddr in addr_info:
            ip_str = sockaddr[0]
            resolved_ips.add(ip_str)
            forbidden, reason = is_ip_forbidden(ip_str)
            if forbidden:
                return PolicyEvaluationResult(
                    allowed=False,
                    reason=f"SSRF Protection: Hostname '{hostname}' resolved to prohibited IP '{ip_str}' ({reason})",
                    resolved_ip=ip_str,
                    violation_code="SSRF_PROHIBITED_IP"
                )
    except socket.gaierror as e:
        return PolicyEvaluationResult(
            allowed=False,
            reason=f"DNS resolution failed for hostname '{hostname}': {str(e)}",
            violation_code="DNS_RESOLUTION_FAILED"
        )

    return PolicyEvaluationResult(
        allowed=True,
        reason="URL conforms to authorized scope and passes SSRF/DNS security checks.",
        canonical_target=f"{parsed.scheme}://{hostname}:{port}{canonical_path}"
    )
