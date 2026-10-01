# ScopeGuard Security Studio - Architecture Specification
### (Formerly Tawassl Security Studio)
**Chief Architect & Developer:** Falah G. Salieh (AI Developer Since 1988 & Physics/Math Educator, Baghdad, Iraq 2026)  
**Live Cloud Production URL:** [https://scopeguard-seven-black.vercel.app/](https://scopeguard-seven-black.vercel.app/)

---

## 1. System Overview

**ScopeGuard Security Studio** is an original, local-first and cloud-deployable AI workspace for discovering, investigating, and documenting security vulnerabilities and functional bugs in user-authorized targets.

```
+-----------------------------------------------------------------------------------+
|                        Frontend: Next.js 16 App Router                            |
|  - Dashboard, Projects, Targets, Plans, AI Console, Command Queue, Terminal, ...  |
|  - Developer Profile (Falah G. Salieh: 38-Year Milestones, Physics/Math, Blog)   |
|  - Standalone Serverless API Route Handlers (/api/projects, /api/targets, ...)    |
|  - Brand Assets: Vector SVG Favicon, Multi-size ICO/PNG, OpenGraph Preview Banner |
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

---

## 2. Component Design

### 2.1 Next.js 16 Frontend & Serverless Edge Architecture
- **Dual Deployment Modes:**
  1. *Local-First Desktop Studio:* Communicates directly with the local Python FastAPI backend (`127.0.0.1:8000`) for non-root local sandboxed tool execution.
  2. *Cloud Serverless Mode (Vercel):* Implements native App Router route handlers (`apps/web/app/api/*`) for zero-config, highly-available deployment at `https://scopeguard-seven-black.vercel.app/`.
- **Developer Profile Module:**
  - Dedicated interactive view honoring developer Falah G. Salieh.
  - Chronological 38-year milestone visualizer (1988 — 2026).
  - Pedagogical bridge uniting theoretical physics and mathematical analysis with modern autonomous neural models.
  - Interactive publication reader modal with full articles on PINNs, mathematical proofs, and sovereign AI.
- **Brand Assets & Metadata Engine:**
  - High-res OpenGraph / Twitter preview card (`/og-image.jpg`, `/og-image.png`) highlighting platform capabilities and developer credentials.
  - Scalable vector SVG favicon (`favicon.svg`) with dark-mode neon glowing ring, plus multi-size PNG/ICO assets.
  - Webmanifest (`/site.webmanifest`) supporting PWA capabilities.

### 2.2 PolicyEngine & Network Guard
- **Zero-Trust Default:** An empty scope rejects all network traffic.
- **Target Boundary Enforcement:** Default target bound to `scopeguard-seven-black.vercel.app` and `scopeguard.vercel.app`.
- **SSRF Prevention:** Blocks loopback (`127.0.0.0/8`), private RFC1918 networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and AWS/GCP cloud metadata IPs.
- **Egress Guard on Redirects:** Follows redirects manually, verifying each redirect target against the scope and resolving DNS before issuing a request.
- **Path Traversal Guard:** Uses `os.path.realpath` and `os.path.commonpath` to ensure candidate file paths are strictly bounded inside the authorized project directory.

### 2.3 Immutable Proposals & Atomic Approvals
- Models propose typed tool calls; they can never execute commands directly.
- Proposals calculate a SHA-256 hash over `(assessment_id, tool_name, arguments)`.
- Human operator reviews proposal purpose, side-effects, and resource limits before approving.
- Tokens are consumed atomically; any change in parameters invalidates the approval.

### 2.4 Isolated Worker Sandbox
- No shell execution (`shell=False`, argv arrays only).
- Provider API keys and host credentials are scrubbed from child process environments.
- Output streams are capped (e.g. 2 MB limit) to prevent output flooding.
- Process group termination ensures no orphan child processes survive cancellations.

### 2.5 Bug Bounty Diagnostic Suite
- **Security Headers Check:** Validates Strict-Transport-Security (HSTS), Content-Security-Policy (CSP), X-Frame-Options, and X-Content-Type-Options.
- **CORS Misconfiguration Probe:** Audits cross-origin resource sharing by simulating untrusted external origins (`https://evil-attacker.example`) and checking for wildcards or reflected origins with `Access-Control-Allow-Credentials: true`.
- **Open Redirect Validation:** Probes query parameter forwarding (`?redirect=`, `?next=`) and verifies that off-domain redirections are safely caught by the scope policy engine.
- **Crawler & Endpoint Reconnaissance:** Analyzes `robots.txt` Disallow directives to catalog private administrative interfaces.
- **Dotfile & Repository Exposure:** Probes `/.git/HEAD` and `/.env`, distinguishing Single Page Application (SPA) client-side HTML fallbacks from genuine file leaks to eliminate false positives.
- **Server Version Fingerprinting:** Checks `Server` and `X-Powered-By` headers to ensure verbose backend version details are masked.

### 2.6 Live Output Terminal & History Log Exporter
- Bounded real-time event streaming with automated secret and credential redaction.
- **Clear Logs:** Resets the terminal stream for fresh test runs.
- **Export History Log:** Downloads structured `.log` audit trail files containing target scope, ISO timestamps, log severity levels, and execution events for penetration testing archives.

### 2.7 Reporting
- Exporters support Markdown, structured JSON, and OASIS SARIF v2.1.0.
- Every report explicitly documents executed tests, skipped modules, and scope limitations.
