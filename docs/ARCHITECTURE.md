# Tawassl Security Studio - Architecture Specification

## 1. System Overview

**Tawassl Security Studio** (`tawassl-security-studio`) is an original, local-first AI workspace for discovering, investigating, and documenting security vulnerabilities and functional bugs in user-authorized targets.

```
+-----------------------------------------------------------------------------------+
|                        Frontend: Next.js App Router                                |
|  - Dashboard, Projects, Targets, Plans, AI Console, Command Queue, Terminal, ...  |
|  - Bilingual i18n (Arabic RTL / English LTR) & Dark/Light Cybersecurity Themes     |
+-----------------------------------------------------------------------------------+
                                         │
                         (Authenticated Local REST / SSE)
                                         ▼
+-----------------------------------------------------------------------------------+
|                        Backend: Python FastAPI Core                               |
|  - Host/Origin & Anti-CSRF Security Middleware                                    |
|  - SQLite Database with Foreign Key Integrity & Migrations                        |
|  - Deterministic PolicyEngine (SSRF, Subdomain Rules, Workspace Escape Guard)     |
|  - Immutable Proposal Registry & One-Time Atomic Approval Engine                  |
|  - Hard Safety Budget Manager (Steps, Requests, Timeouts, Output Capping)         |
|  - AI Provider Layer: Gemini, OpenAI GPT, and Deterministic Offline MockProvider  |
+-----------------------------------------------------------------------------------+
                                         │
                                (Non-Root Sandboxed Exec)
                                         ▼
+-----------------------------------------------------------------------------------+
|                     Isolated Execution Worker (Subprocess Guard)                  |
|  - Process Group Termination (Process-Tree Cleanup)                               |
|  - Stripped Provider Keys & Host SSH Credentials                                  |
|  - Controlled HTTP Client (Manual Redirect Verification & Security Headers Audit) |
|  - Offline Python AST Syntax Inspector (eval, exec, subprocess shell=True)        |
|  - Secret Scanner with Shannon Entropy Analysis (AWS, GitHub, Slack tokens)       |
|  - Patch Engine (Unified Diff Generation with .bak Revert Mechanism)               |
+-----------------------------------------------------------------------------------+
```

## 2. Component Design

### 2.1 PolicyEngine & Network Guard
- **Zero-Trust Default:** An empty scope rejects all network traffic.
- **SSRF Prevention:** Blocks loopback (`127.0.0.0/8`), private RFC1918 networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and AWS/GCP cloud metadata IPs.
- **Egress Guard on Redirects:** Follows redirects manually, verifying each redirect target against the scope and resolving DNS before issuing a request.
- **Path Traversal Guard:** Uses `os.path.realpath` and `os.path.commonpath` to ensure candidate file paths are strictly bounded inside the authorized project directory.

### 2.2 Immutable Proposals & Atomic Approvals
- Models propose typed tool calls; they can never execute commands directly.
- Proposals calculate a SHA-256 hash over `(assessment_id, tool_name, arguments)`.
- Human operator reviews proposal purpose, side-effects, and resource limits before approving.
- Tokens are consumed atomically; any change in parameters invalidates the approval.

### 2.3 Isolated Worker Sandbox
- No shell execution (`shell=False`, argv arrays only).
- Provider API keys and host credentials are scrubbed from child process environments.
- Output streams are capped (e.g. 2 MB limit) to prevent output flooding.
- Process group termination ensures no orphan child processes survive cancellations.

### 2.4 Reporting
- Exporters support Markdown, structured JSON, and OASIS SARIF v2.1.0.
- Every report explicitly documents executed tests, skipped modules, and scope limitations.
