export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

export interface Target {
  id: string;
  project_id: string;
  name: string;
  target_type: 'website' | 'api' | 'source' | 'combined';
  authorized_domains: string[];
  base_urls: string[];
  allowed_ports: number[];
  allow_subdomains: boolean;
  exclusions: string[];
  source_path?: string;
  created_at: string;
}

export interface Assessment {
  id: string;
  project_id: string;
  target_id: string;
  name: string;
  profile: 'observe' | 'source_review' | 'controlled_active' | 'authenticated' | 'regression';
  status: 'queued' | 'awaiting_approval' | 'running' | 'completed' | 'failed' | 'cancelled' | 'inconclusive';
  ai_provider: string;
  model_id: string;
  max_steps: number;
  max_requests: number;
  max_tool_calls: number;
  timeout_seconds: number;
  max_output_bytes: number;
  steps_taken: number;
  requests_made: number;
  tool_calls_made: number;
  started_at: string;
  completed_at?: string;
}

export interface Proposal {
  id: string;
  assessment_id: string;
  tool_name: string;
  arguments: Record<string, any>;
  arguments_hash: string;
  purpose: string;
  side_effects: string;
  resource_limits: {
    timeout_sec: number;
    max_output_kb: number;
    network_restricted: boolean;
  };
  status: 'pending' | 'approved' | 'rejected' | 'consumed';
  created_at: string;
}

export interface Finding {
  id: string;
  assessment_id: string;
  title: string;
  category: string;
  affected_asset: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  confidence: 'confirmed' | 'high' | 'medium' | 'low';
  status: 'observation' | 'suspected' | 'confirmed' | 'inconclusive' | 'false_positive' | 'fixed' | 'retest_failed';
  preconditions?: string;
  reproduction_steps: string;
  expected_result: string;
  observed_result: string;
  impact?: string;
  remediation?: string;
  evidence: Array<{
    type: 'http_request' | 'http_response' | 'code_snippet' | 'log';
    title: string;
    content: string;
  }>;
  created_at: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success' | 'agent';
  message: string;
  source: string;
}

export const MOCK_PROJECTS: Project[] = [
  {
    id: "proj-acme-prod",
    name: "Acme Fintech Platform",
    description: "Multi-tenant banking & payment settlement platform",
    created_at: "2026-09-20 10:00:00 UTC",
  },
  {
    id: "proj-tawassl-internal",
    name: "Tawassl Internal Services",
    description: "Microservices and internal employee portals",
    created_at: "2026-09-22 14:30:00 UTC",
  }
];

export const MOCK_TARGETS: Target[] = [
  {
    id: "target-acme-web",
    project_id: "proj-acme-prod",
    name: "Acme Web Portal (Staging)",
    target_type: "website",
    authorized_domains: ["staging.acmepay.internal"],
    base_urls: ["https://staging.acmepay.internal:8443"],
    allowed_ports: [8443],
    allow_subdomains: false,
    exclusions: ["/api/v1/payments/execute", "/admin/super"],
    created_at: "2026-09-20 10:15:00 UTC",
  },
  {
    id: "target-auth-service",
    project_id: "proj-acme-prod",
    name: "Auth & Identity Service (Source)",
    target_type: "source",
    authorized_domains: [],
    base_urls: [],
    allowed_ports: [],
    allow_subdomains: false,
    exclusions: [".git", "node_modules", "tests/fixtures"],
    source_path: "/workspace/services/auth-service",
    created_at: "2026-09-21 09:00:00 UTC",
  }
];

export const MOCK_ASSESSMENT: Assessment = {
  id: "assess-run-001",
  project_id: "proj-acme-prod",
  target_id: "target-acme-web",
  name: "Pre-Release Security Baseline Scan",
  profile: "observe",
  status: "awaiting_approval",
  ai_provider: "mock",
  model_id: "mock-sec-v1",
  max_steps: 20,
  max_requests: 50,
  max_tool_calls: 30,
  timeout_seconds: 300,
  max_output_bytes: 2097152,
  steps_taken: 4,
  requests_made: 7,
  tool_calls_made: 3,
  started_at: "2026-09-27 12:00:00 UTC",
};

export const MOCK_PROPOSALS: Proposal[] = [
  {
    id: "prop-001",
    assessment_id: "assess-run-001",
    tool_name: "controlled_http_inspect",
    arguments: {
      url: "https://staging.acmepay.internal:8443/login",
      method: "GET",
      follow_redirects: false,
      headers: { "Accept": "text/html" }
    },
    arguments_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    purpose: "Inspect HTTP response headers for missing Strict-Transport-Security (HSTS), Content-Security-Policy (CSP), and anti-clickjacking directives.",
    side_effects: "Single read-only GET request within authorized domain. No state mutation.",
    resource_limits: {
      timeout_sec: 10,
      max_output_kb: 256,
      network_restricted: true,
    },
    status: "pending",
    created_at: "2026-09-27 12:05:12 UTC",
  },
  {
    id: "prop-002",
    assessment_id: "assess-run-001",
    tool_name: "ast_syntax_inspector",
    arguments: {
      file_path: "app/auth/tokens.py",
      check_rules: ["no_eval", "no_shell_exec", "safe_secrets"]
    },
    arguments_hash: "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    purpose: "Perform offline AST parsing of authentication token generator to detect any insecure calls.",
    side_effects: "Read-only offline AST file analysis within isolated sandbox. No network access.",
    resource_limits: {
      timeout_sec: 5,
      max_output_kb: 512,
      network_restricted: true,
    },
    status: "approved",
    created_at: "2026-09-27 12:02:40 UTC",
  }
];

export const MOCK_FINDINGS: Finding[] = [
  {
    id: "find-001",
    assessment_id: "assess-run-001",
    title: "Missing Strict-Transport-Security (HSTS) Header",
    category: "web_security",
    affected_asset: "https://staging.acmepay.internal:8443",
    severity: "medium",
    confidence: "confirmed",
    status: "confirmed",
    preconditions: "Direct TLS connection to staging endpoint.",
    reproduction_steps: "1. Send GET request to https://staging.acmepay.internal:8443/login\n2. Inspect response headers for Strict-Transport-Security\n3. Note header is completely omitted.",
    expected_result: "Response should include Strict-Transport-Security: max-age=31536000; includeSubDomains",
    observed_result: "No Strict-Transport-Security header present in the response.",
    impact: "Users may be vulnerable to SSL stripping attacks during initial unencrypted connections on untrusted networks.",
    remediation: "Configure the reverse proxy or application middleware to set the Strict-Transport-Security header with a minimum max-age of 31536000 seconds.",
    evidence: [
      {
        type: "http_response",
        title: "HTTP/1.1 Response Headers",
        content: "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nServer: nginx/1.24\r\nX-Frame-Options: SAMEORIGIN\r\nConnection: keep-alive\r\n\r\n[Body Content...]"
      }
    ],
    created_at: "2026-09-27 12:03:15 UTC",
  },
  {
    id: "find-002",
    assessment_id: "assess-run-001",
    title: "Session Cookie Missing SameSite and Secure Flags",
    category: "web_security",
    affected_asset: "/login (Set-Cookie: session_id)",
    severity: "high",
    confidence: "confirmed",
    status: "confirmed",
    preconditions: "User visits login page.",
    reproduction_steps: "1. Send GET request to /login\n2. Observe Set-Cookie header for session_id\n3. Notice missing 'Secure' and 'SameSite=Lax/Strict' attributes.",
    expected_result: "Set-Cookie should specify: session_id=...; Secure; HttpOnly; SameSite=Lax",
    observed_result: "Set-Cookie: session_id=[REDACTED_SESSION]; HttpOnly (missing Secure and SameSite)",
    impact: "Session cookies could be transmitted over unencrypted HTTP or leaked in cross-site requests, increasing risk of session hijacking.",
    remediation: "Enforce SameSite=Lax or SameSite=Strict and the Secure attribute on all session identification cookies.",
    evidence: [
      {
        type: "http_response",
        title: "Set-Cookie Header Snapshot",
        content: "Set-Cookie: session_id=[REDACTED_SESSION]; Path=/; HttpOnly"
      }
    ],
    created_at: "2026-09-27 12:04:22 UTC",
  }
];

export const MOCK_LOGS: LogEntry[] = [
  { id: "log-1", timestamp: "12:00:01", level: "info", source: "orchestrator", message: "Starting assessment 'Pre-Release Security Baseline Scan' [Profile: Observe]" },
  { id: "log-2", timestamp: "12:00:02", level: "info", source: "policy_engine", message: "Validated target scope for 'staging.acmepay.internal:8443'. Zero-trust policy active." },
  { id: "log-3", timestamp: "12:00:05", level: "agent", source: "mock_ai", message: "Plan formulated: 1. Public header audit 2. Cookie attribute verification 3. TLS cipher check" },
  { id: "log-4", timestamp: "12:02:30", level: "info", source: "worker", message: "Offline tool 'ast_syntax_inspector' executed in isolated sandbox (exit 0). 0 violations found." },
  { id: "log-5", timestamp: "12:03:15", level: "warn", source: "finding_engine", message: "Flagged missing HSTS header. Status set to 'confirmed' with verified response evidence." },
  { id: "log-6", timestamp: "12:04:22", level: "error", source: "finding_engine", message: "Flagged cookie 'session_id' missing Secure & SameSite attributes. Severity: HIGH." },
  { id: "log-7", timestamp: "12:05:12", level: "warn", source: "approval_engine", message: "Proposal prop-001 created. Awaiting user one-time approval before dispatch." },
];
