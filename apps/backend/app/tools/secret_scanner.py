import re
import math
from typing import List, Dict, Any
from pathlib import Path
from apps.backend.app.core.security import redact_secrets

SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r'(?i)\b(AKIA[0-9A-Z]{16})\b')),
    ("GitHub Personal Access Token", re.compile(r'\b(gh[pous]_[a-zA-Z0-9]{36})\b')),
    ("Slack Token", re.compile(r'\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b')),
    ("Generic API Key Assignment", re.compile(r'(?i)(?:api[_-]?key|secret|password)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']')),
    ("RSA/OpenSSH Private Key", re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
]


def calculate_shannon_entropy(data: str) -> float:
    """Calculates Shannon entropy to detect high-entropy random secrets."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    for x in set(data):
        p_x = float(data.count(x)) / length
        entropy += - p_x * math.log(p_x, 2)
    return entropy


def scan_file_for_secrets(file_path: str) -> List[Dict[str, Any]]:
    """Scans a target source file for exposed secrets and credentials."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    findings = []

    for line_idx, line in enumerate(lines, 1):
        for rule_name, pattern in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                matched_str = match.group(0)
                findings.append({
                    "line_number": line_idx,
                    "rule_name": rule_name,
                    "severity": "high",
                    "code_snippet": redact_secrets(line.strip()),
                    "message": f"Potential exposed secret detected: {rule_name}"
                })

    return findings
