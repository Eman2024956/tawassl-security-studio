from typing import Dict, Any, Optional
from apps.backend.app.policy.models import ScopeRule, PolicyEvaluationResult
from apps.backend.app.policy.network_guard import validate_url_against_scope
from apps.backend.app.policy.workspace_guard import validate_workspace_path


class PolicyEngine:
    """
    Central deterministic policy and scope enforcement engine.
    Ensures that empty scope denies access and that all tool proposals
    conform strictly to authorized domains, canonical workspace bounds, and exclusions.
    """

    def __init__(self, scope: Optional[ScopeRule] = None):
        self.scope = scope or ScopeRule()

    def evaluate_url(self, url: str) -> PolicyEvaluationResult:
        """Evaluates a network URL target against current scope and SSRF boundaries."""
        return validate_url_against_scope(url, self.scope)

    def evaluate_path(self, path: str) -> PolicyEvaluationResult:
        """Evaluates a filesystem path against current workspace root."""
        return validate_workspace_path(path, self.scope.source_root or "")

    def evaluate_proposal(self, tool_name: str, arguments: Dict[str, Any]) -> PolicyEvaluationResult:
        """
        Validates whether a proposed tool call conforms to policy:
        - Network tools (e.g. controlled_http) must target valid in-scope URLs.
        - File/Source tools (e.g. source_inspector, ast_parser) must target files within authorized workspace.
        """
        if tool_name in ("controlled_http", "controlled_http_inspect", "playwright_browser"):
            url = arguments.get("url") or arguments.get("target_url")
            if not url:
                return PolicyEvaluationResult(
                    allowed=False,
                    reason=f"Tool '{tool_name}' requires a 'url' argument.",
                    violation_code="MISSING_TARGET_URL"
                )
            return self.evaluate_url(url)

        if tool_name in ("source_inspector", "ast_parser", "ast_syntax_inspector", "semgrep", "gitleaks"):
            file_path = arguments.get("file_path") or arguments.get("path") or arguments.get("source_dir")
            if not file_path:
                return PolicyEvaluationResult(
                    allowed=False,
                    reason=f"Tool '{tool_name}' requires a 'file_path' or 'path' argument.",
                    violation_code="MISSING_TARGET_PATH"
                )
            return self.evaluate_path(file_path)

        # Default fallback for unknown or unregistered tools
        return PolicyEvaluationResult(
            allowed=False,
            reason=f"Tool '{tool_name}' is not registered in the safety policy catalog.",
            violation_code="UNREGISTERED_TOOL_DENY"
        )
