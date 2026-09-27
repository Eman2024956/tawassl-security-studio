Act as a senior software architect, full-stack engineer, and application-security engineer.

BUILD AN ORIGINAL PROJECT FROM SCRATCH.

PROJECT NAME
Tawassl Security Studio

GITHUB REPOSITORY NAME
tawassl-security-studio

Do not clone, fork, import, or base the architecture on PentesterFlow or another security-agent repository.

Use established libraries and security tools through documented adapters. Create our own interface, orchestration, policy engine, data model, reporting, and workflows.

GOAL

Build a local-first AI workspace for discovering, investigating, and documenting functional bugs and security vulnerabilities in user-authorized websites, domains, APIs, and source-code projects.

Support arbitrary user-configured targets. Never hardcode a particular domain.

Use Gemini and OpenAI GPT models to plan tests, interpret results, propose follow-up checks, explain evidence, and suggest fixes.

Do not promise to find every vulnerability. Report actual coverage, limitations, skipped tests, and confidence.

## 1. Technology stack

- Next.js App Router, TypeScript, Tailwind CSS.
- Python FastAPI and Pydantic.
- SQLite with migrations for the single-user MVP.
- Official OpenAI and Google Gen AI SDKs.
- Separate isolated execution worker.
- Authenticated SSE or WebSocket for live events.
- pytest and Playwright.
- MockProvider and local fixtures for development without API keys.

Verify current official documentation before choosing SDK methods. Pin tested dependencies and commit lockfiles.

## 2. Target onboarding

Provide a “New Assessment” wizard:

1. Project name.
2. Target type:
   - Website/domain.
   - API.
   - Local source-code project.
   - Combined source and running application.
3. Authorized domains, URLs, ports, and optional subdomains.
4. Explicit exclusions.
5. Authentication configuration using dedicated test accounts.
6. Testing profile and permitted operations.
7. Request, duration, concurrency, and cost limits.
8. Review and start.

Every assessment requires an explicit scope.

Do not interpret ownership of one domain as authorization for:
- Its hosting provider.
- Shared IP infrastructure.
- Third-party payment services.
- Unlisted subdomains.
- External services linked from the website.

Keep production and staging assessments separate.

## 3. Assessment profiles

Implement profiles with clear effects:

A. Observe
- Public-page inspection.
- Headers and cookie attributes.
- TLS checks.
- Limited endpoint inventory from supplied pages and specifications.
- No state-changing requests.

B. Source Review
- Source analysis.
- Dependency and secret-scanning adapters.
- Configuration review.
- No execution of project code unless separately approved and isolated.

C. Controlled Active Testing
- Explicitly selected vulnerability checks.
- Approved endpoints and request budgets.
- Dedicated test data.
- Human review before mutations.

D. Authenticated Testing
- User-provided test accounts and roles.
- Authorization and session checks.
- Reversible operations with state verification and cleanup.

E. Regression
- Re-run selected previously verified tests after fixes.

Changing profiles must not silently expand scope or permissions.

## 4. Coverage catalog

Build an extensible test catalog covering these categories.

Web and API security:
- Authentication and session handling.
- Broken access control, IDOR/BOLA, and role enforcement.
- CSRF.
- XSS.
- SQL/NoSQL and command injection.
- SSRF.
- Path traversal and file access.
- File-upload validation.
- CORS and security headers.
- TLS and cookie configuration.
- JWT and token validation.
- Redirect handling.
- Sensitive-information exposure.
- API schema and input validation.
- GraphQL authorization and query limits.
- Business-logic flaws.
- Rate-limit behavior using bounded tests, not load attacks.
- Race conditions only in explicitly approved test environments.
- Dependency vulnerabilities and exposed secrets.
- Framework and infrastructure configuration.

Functional reliability:
- Broken navigation and unexpected errors.
- Form validation.
- Incorrect calculations.
- API contract violations.
- Incorrect role-based UI behavior.
- Failed loading/error/empty states.
- Regressions in supplied test scenarios.

Do not claim these categories are fully implemented merely because they appear in the UI.

Each test module must declare:
- Implementation status.
- Required target information.
- Authentication requirements.
- Supported technologies.
- Side effects and risk.
- Tool dependencies.
- Verification method.
- Expected evidence.
- Known limitations.

Mark unavailable tests as “Not implemented” or “Prerequisites missing.”

## 5. AI providers

Implement independent Gemini and OpenAI adapters.

Features:
- Provider and model selection.
- Configurable model IDs.
- Connection testing.
- Streaming where supported.
- Timeouts and bounded retries.
- Usage tracking.
- MockProvider.
- Optional evidence review by a second provider.

Keep credentials on the backend.

Do not automatically send data to another provider during failover.

Models propose typed tool calls. They never execute shell commands directly, approve themselves, modify scope, or decide their own permissions.

Preserve provider-specific tool-call IDs and required context metadata.

Disable automatic execution of model-selected Python callables.

## 6. Agent execution loop

Implement:

Objective
→ Assessment plan
→ Test proposal
→ Scope and policy validation
→ Required approval
→ Isolated execution
→ Evidence collection
→ Result verification
→ Next action or report

Enforce hard, persistent limits for:
- Agent steps.
- Tool calls.
- Target requests.
- Run duration.
- Output size.
- Concurrent processes.

Retries consume budgets.

Stop when a limit is reached. Never silently reset the budget.

Treat webpages, repository files, captured requests, and scanner output as untrusted data rather than instructions.

Do not expose hidden model reasoning. Show concise action rationales and evidence summaries.

## 7. Scope enforcement

Implement a server-side PolicyEngine.

Validate:
- Exact hostnames and explicit subdomain rules.
- Schemes and ports.
- HTTP methods.
- Canonical paths.
- Workspace boundaries.
- Exclusions and expiration.
- Per-target request limits.

Empty scope denies access.

Prevent:
- Hostname suffix tricks.
- Userinfo confusion.
- Redirect escapes.
- DNS rebinding.
- Unauthorized internal-network access.
- Workspace traversal and symlink escapes.

Use controlled transport or enforced egress restrictions. A hostname check before an unrestricted network request is insufficient.

Keep TLS verification enabled.

Scope restrictions must also cover network activity initiated by command-line tools.

## 8. Command interface and worker

Build a command proposal system with:

- Tool name.
- Validated arguments.
- Target.
- Working directory.
- Purpose.
- Expected side effects.
- Resource limits.
- Rendered command preview.
- Approve once, Reject, and Stop.

Use registered command presets and structured arguments.

Do not pass model-generated strings to shell=True, eval, or unrestricted bash -c.

Validate executable arguments, configuration paths, output paths, and environment variables.

Store immutable proposals. Bind approvals to:
- User.
- Assessment.
- Arguments hash.
- Policy version.
- Expiration.

Consume approval once, atomically. Changed arguments require a new approval.

Run tools in an isolated worker with:
- Non-root identity.
- No provider API keys.
- No host home directory or SSH agent.
- No Docker socket inside the worker.
- Read-only snapshots where practical.
- Restricted network access.
- CPU, RAM, process, time, disk, and output limits.
- Bounded streaming.
- Process-tree cancellation.

If isolation is unavailable, disable tools that require it. Never fall back silently to unrestricted execution.

## 9. Tool integrations

Implement adapters incrementally for:
- Controlled HTTP inspection.
- Source-file reading and searching.
- Python syntax checks.
- Semgrep.
- Gitleaks.
- Dependency-audit tools appropriate to the project.
- Playwright browser checks.
- Approved test suites.
- OpenAPI import.
- Sanitized HAR import.
- Optional OWASP ZAP integration with explicitly selected scan policy.

Pin tool versions and validate their output.

Do not enable every scanner or active rule by default.

Installing dependencies, executing tests, and loading project plugins may execute untrusted code and must be isolated.

## 10. Authenticated assessments

Support secure references to test credentials rather than embedding them in prompts.

Provide:
- Test-account labels and roles.
- Session-expiration handling.
- Credential redaction.
- Separate account contexts.
- Reversible test operations.
- Cleanup tracking.

For authorization testing, compare resources created by dedicated test accounts.

For CSRF, require a real state-changing endpoint and browser-realistic validation. Confirm actual state changes, not merely HTTP status.

Never invent endpoints, account credentials, or resource ownership.

## 11. Interface

Create a professional Arabic/English security workspace.

- RTL prose and LTR code.
- Dark/light themes.
- Accessible keyboard navigation.
- Resizable panels.
- Responsive layout.

Navigation:
Dashboard
Projects
Targets & Scope
Assessment Plans
AI Agent
Command Queue
Live Output
Findings
Evidence
Reports
Settings

Header:
Target, profile, provider, model, run status, request budget, usage, Stop.

Use clear states:
Queued, Awaiting Approval, Running, Completed, Failed, Cancelled, Inconclusive, Skipped.

Never present fabricated findings, fake scan activity, or an invented security percentage.

The terminal is initially a sanitized output viewer, not an unrestricted interactive host shell.

## 12. Findings and evidence

Use statuses:
Observation
Suspected
Confirmed
Inconclusive
False Positive
Fixed
Retest Failed

Each finding contains:
- Title.
- Category.
- Affected asset.
- Severity and rationale.
- Confidence.
- Preconditions.
- Reproduction steps.
- Expected and observed results.
- Evidence references.
- Impact.
- Suggested remediation.
- Retest history.

Model agreement does not confirm a vulnerability.

Do not confirm:
- XSS from reflection alone.
- CSRF from missing token hints alone.
- IDOR from HTTP 200 alone.
- A secret leak from a public configuration identifier alone.

Require evidence validation appropriate to the finding type.

Record skipped tests and missing prerequisites.

## 13. Fix proposals

For supplied source projects:
- Generate a reviewable Diff.
- Preserve existing user changes.
- Require approval before applying patches.
- Run relevant tests in isolation.
- Show actual results.
- Support reverting the specific patch.

Do not automatically push, merge, deploy, or alter production configuration.

## 14. Security of our own application

Protect the tool itself with:
- Authenticated local sessions.
- Host and Origin validation.
- CSRF protection for approvals and mutations.
- Per-project authorization.
- No side effects on GET.
- Safe Markdown and terminal rendering.
- Secret redaction.
- No credentials in URL query parameters.
- Auditable approval and execution history.

Loopback binding alone is not sufficient protection against browser-origin attacks.

## 15. Reports

Export Markdown and JSON first, then validated SARIF.

Include:
- Authorized scope.
- Assessment profile.
- Tool and model versions.
- Tests actually executed.
- Confirmed findings.
- Suspected findings and observations.
- Evidence.
- Skipped tests.
- Coverage limitations.
- Remediation.
- Retest results.

No findings means “no findings detected by these tests,” not “the application is secure.”

## 16. Testing requirements

Use fixtures and MockProvider.

Test:
- Scope bypass attempts.
- Redirect and DNS-rebinding controls.
- Approval tampering, replay, and concurrency.
- Workspace escapes.
- Malformed model tool calls.
- Output flooding.
- Cancellation and process cleanup.
- Hard-budget exhaustion.
- Secret redaction.
- Prompt injection.
- Cross-origin approval requests.
- Provider errors.
- Evidence-based finding status transitions.
- Complete UI-to-worker-to-report workflow.

Do not scan real websites during development or CI.

## 17. Delivery and implementation

First inspect the workspace, then implement working vertical slices:

1. Scaffold, database, and health endpoint.
2. Complete UI flow using clearly labeled mock data.
3. Scope and approval engine.
4. Isolated worker with one offline tool.
5. Gemini and GPT adapters.
6. Agent orchestration with hard limits.
7. Controlled network testing.
8. Findings and reports.
9. Scanner and browser integrations.
10. Fix-and-retest workflow.

Deliver:
- Working source code.
- Arabic and English README.
- Environment template without secrets.
- Installation and startup commands.
- Architecture and threat model.
- Tests and CI.
- Example policies and fixtures.
- Implemented-versus-pending matrix.
- Real verification results.

Do not stop at a plan or static interface. Implement the core workflow end to end.

If provider credentials are missing, complete and test the workflow using MockProvider and clearly mark live-provider tests as not run.

Prepare the repository as tawassl-security-studio. Do not claim that a GitHub remote exists until it has actually been created.

Start implementation now.