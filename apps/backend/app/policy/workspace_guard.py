import os
from pathlib import Path
from apps.backend.app.policy.models import PolicyEvaluationResult

SENSITIVE_HOST_PATHS = [
    "/etc",
    "/root",
    "/var/run/docker.sock",
    os.path.expanduser("~/.ssh"),
    os.path.expanduser("~/.aws"),
    os.path.expanduser("~/.gnupg"),
]


def validate_workspace_path(candidate_path: str, workspace_root: str) -> PolicyEvaluationResult:
    """
    Validates that candidate_path strictly resides inside workspace_root.
    Prevents:
    - Path traversal attacks (../, %2e%2e).
    - Null-byte injection (%00, \x00).
    - Symlinks pointing outside workspace_root.
    - Access to host system credentials and Docker sockets.
    """
    if not workspace_root:
        return PolicyEvaluationResult(
            allowed=False,
            reason="Empty workspace root configuration denies all file operations.",
            violation_code="EMPTY_WORKSPACE_ROOT"
        )

    # 1. Null-byte injection check
    if "\x00" in candidate_path or "%00" in candidate_path:
        return PolicyEvaluationResult(
            allowed=False,
            reason="Null-byte characters detected in path.",
            violation_code="NULL_BYTE_INJECTION"
        )

    # 2. Canonicalize workspace root
    canonical_root = os.path.realpath(workspace_root)

    # 3. Construct absolute candidate path
    if os.path.isabs(candidate_path):
        resolved_candidate = os.path.realpath(candidate_path)
    else:
        resolved_candidate = os.path.realpath(os.path.join(canonical_root, candidate_path))

    # 4. Check if resolved candidate falls strictly within canonical_root
    try:
        common = os.path.commonpath([canonical_root, resolved_candidate])
        if common != canonical_root:
            return PolicyEvaluationResult(
                allowed=False,
                reason=f"Path traversal or symlink escape detected: '{candidate_path}' resolves outside workspace root.",
                canonical_target=resolved_candidate,
                violation_code="WORKSPACE_ESCAPE_DETECTED"
            )
    except ValueError:
        return PolicyEvaluationResult(
            allowed=False,
            reason=f"Path '{candidate_path}' is on a different drive or invalid.",
            violation_code="INVALID_PATH_DRIVE"
        )

    # 5. Check against sensitive host system paths
    for sensitive in SENSITIVE_HOST_PATHS:
        try:
            real_sensitive = os.path.realpath(sensitive)
            if os.path.commonpath([real_sensitive, resolved_candidate]) == real_sensitive:
                return PolicyEvaluationResult(
                    allowed=False,
                    reason=f"Access to sensitive host system path '{sensitive}' is strictly prohibited.",
                    canonical_target=resolved_candidate,
                    violation_code="SENSITIVE_HOST_PATH_DENIED"
                )
        except Exception:
            continue

    return PolicyEvaluationResult(
        allowed=True,
        reason="Path is safely bounded inside the authorized workspace.",
        canonical_target=resolved_candidate
    )
