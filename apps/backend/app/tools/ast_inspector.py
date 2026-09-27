import ast
import re
from typing import List, Dict, Any
from pathlib import Path


class ASTFinding(Dict[str, Any]):
    line_number: int
    rule_id: str
    severity: str
    message: str
    code_snippet: str


class DangerousASTVisitor(ast.NodeVisitor):
    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.findings: List[Dict[str, Any]] = []

    def visit_Call(self, node: ast.Call):
        # 1. Check for eval() or exec()
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                line = node.lineno
                snippet = self.source_lines[line - 1].strip() if line <= len(self.source_lines) else ""
                self.findings.append({
                    "line_number": line,
                    "rule_id": f"python-dangerous-{node.func.id}",
                    "severity": "high",
                    "message": f"Use of dynamic code execution '{node.func.id}()' detected.",
                    "code_snippet": snippet
                })

        # 2. Check for subprocess calls with shell=True
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if func_name in ("Popen", "call", "run", "check_call", "check_output"):
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        line = node.lineno
                        snippet = self.source_lines[line - 1].strip() if line <= len(self.source_lines) else ""
                        self.findings.append({
                            "line_number": line,
                            "rule_id": "python-subprocess-shell-true",
                            "severity": "high",
                            "message": f"subprocess.{func_name}() invoked with shell=True, enabling potential command injection.",
                            "code_snippet": snippet
                        })

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # 3. Check for obvious hardcoded credential variables
        secret_var_names = {"api_key", "secret", "password", "token", "private_key"}
        for target in node.targets:
            if isinstance(target, ast.Name):
                name_lower = target.id.lower()
                if any(sec in name_lower for sec in secret_var_names):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        val_str = node.value.value
                        if len(val_str) > 8 and not val_str.startswith("env:") and not val_str.startswith("test_"):
                            line = node.lineno
                            snippet = self.source_lines[line - 1].strip() if line <= len(self.source_lines) else ""
                            self.findings.append({
                                "line_number": line,
                                "rule_id": "hardcoded-secret-assignment",
                                "severity": "medium",
                                "message": f"Variable '{target.id}' assigned potential hardcoded secret literal.",
                                "code_snippet": snippet
                            })
        self.generic_visit(node)


def inspect_python_source(file_path: str) -> Dict[str, Any]:
    """Inspects a Python source file using AST parsing without executing any code."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    source_code = path.read_text(encoding="utf-8", errors="replace")
    source_lines = source_code.splitlines()

    try:
        tree = ast.parse(source_code, filename=str(path))
    except SyntaxError as e:
        return {
            "status": "syntax_error",
            "error": str(e),
            "line_number": e.lineno,
            "findings": []
        }

    visitor = DangerousASTVisitor(source_lines)
    visitor.visit(tree)

    return {
        "status": "success",
        "file": str(path),
        "total_lines": len(source_lines),
        "findings": visitor.findings
    }
