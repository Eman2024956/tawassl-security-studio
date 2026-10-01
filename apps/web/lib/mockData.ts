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
  environment_mode: 'live' | 'mock';
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
  result_type: 'passed_control' | 'observation' | 'finding' | 'inconclusive';
  confirmed_vulnerability: boolean;
  sensitive_file_content_verified?: boolean;
  evidence_hash?: string;
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
    id: "proj-scopeguard-prod",
    name: "ScopeGuard Security Platform",
    description: "Production ScopeGuard security & assessment web application",
    created_at: "2026-09-20 10:00:00 UTC",
  },
  {
    id: "proj-tawassl-internal",
    name: "ScopeGuard Internal Services",
    description: "Microservices and internal security portals",
    created_at: "2026-09-22 14:30:00 UTC",
  }
];

export const MOCK_TARGETS: Target[] = [
  {
    id: "target-scopeguard-web",
    project_id: "proj-scopeguard-prod",
    name: "ScopeGuard Production Platform (Live)",
    target_type: "website",
    environment_mode: "live",
    authorized_domains: ["scopeguard.vercel.app", "scopeguard-seven-black.vercel.app"],
    base_urls: ["https://scopeguard-seven-black.vercel.app"],
    allowed_ports: [443, 80],
    allow_subdomains: false,
    exclusions: ["/api/auth/logout", "/logout"],
    created_at: "2026-09-20 10:15:00 UTC",
  },
  {
    id: "target-demo-sandbox",
    project_id: "proj-scopeguard-prod",
    name: "Demo Sandbox Target (Simulated)",
    target_type: "website",
    environment_mode: "mock",
    authorized_domains: ["demo.mock-target.local"],
    base_urls: ["https://demo.mock-target.local"],
    allowed_ports: [443, 80],
    allow_subdomains: false,
    exclusions: ["/api/auth/logout", "/logout"],
    created_at: "2026-09-21 14:00:00 UTC",
  },
  {
    id: "target-auth-service",
    project_id: "proj-scopeguard-prod",
    name: "Auth & Identity Service (Source)",
    target_type: "source",
    environment_mode: "live",
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
  project_id: "proj-scopeguard-prod",
  target_id: "target-scopeguard-web",
  name: "ScopeGuard Security Baseline Scan",
  profile: "observe",
  status: "completed",
  ai_provider: "mock",
  model_id: "mock-sec-v1",
  max_steps: 20,
  max_requests: 50,
  max_tool_calls: 30,
  timeout_seconds: 300,
  max_output_bytes: 2097152,
  steps_taken: 8,
  requests_made: 8,
  tool_calls_made: 8,
  started_at: "2026-09-27 12:00:00 UTC",
  completed_at: "2026-09-27 12:01:15 UTC",
};

export const MOCK_PROPOSALS: Proposal[] = [
  {
    id: "prop-001",
    assessment_id: "assess-run-001",
    tool_name: "controlled_http_inspect",
    arguments: {
      url: "https://scopeguard-seven-black.vercel.app",
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
    status: "approved",
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
    title: "Single Page Application (SPA) HTML Fallback on Unknown Routes",
    category: "web_security",
    affected_asset: "https://scopeguard-seven-black.vercel.app/.env",
    severity: "info",
    confidence: "confirmed",
    status: "observation",
    result_type: "observation",
    confirmed_vulnerability: false,
    sensitive_file_content_verified: false,
    evidence_hash: "ev-spa-fallback-001",
    preconditions: "Direct TLS connection to scopeguard.vercel.app.",
    reproduction_steps: "1. Send GET request to https://scopeguard-seven-black.vercel.app/.env\n2. Inspect response status code and Content-Type header\n3. Observed HTTP 200 with text/html serving Next.js SPA index router.",
    expected_result: "Non-existent sensitive file paths should return explicit HTTP 404 Not Found or HTTP 403 Forbidden.",
    observed_result: "Server returns HTTP 200 with HTML document preview.",
    impact: "Client-side routing fallback may cause false positives in automated black-box scanners that do not inspect Content-Type headers.",
    remediation: "Optionally configure Vercel / Nginx rewrite rules to return 404 for dotfiles (.env, .git, .bak).",
    evidence: [
      {
        type: "http_response",
        title: "HTTP/1.1 Response Headers",
        content: "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nServer: Vercel\r\nX-Matched-Path: /\r\n\r\n<!DOCTYPE html><html>..."
      }
    ],
    created_at: "2026-09-27 12:03:15 UTC",
  },
  {
    id: "find-002",
    assessment_id: "assess-run-001",
    title: "HTTP to HTTPS Redirection Enforced via 308 Permanent Redirect",
    category: "web_security",
    affected_asset: "http://scopeguard-seven-black.vercel.app",
    severity: "info",
    confidence: "confirmed",
    status: "confirmed",
    result_type: "passed_control",
    confirmed_vulnerability: false,
    evidence_hash: "ev-redirect-pass-002",
    preconditions: "Plain HTTP request to domain.",
    reproduction_steps: "1. Send GET request to http://scopeguard-seven-black.vercel.app\n2. Observe HTTP 308 Permanent Redirect with Location: https://scopeguard-seven-black.vercel.app",
    expected_result: "Insecure HTTP connections must immediately redirect to HTTPS.",
    observed_result: "HTTP 308 Location: https://scopeguard-seven-black.vercel.app",
    impact: "Protects against accidental unencrypted transmissions.",
    remediation: "Configuration adheres to security baseline standards.",
    evidence: [
      {
        type: "http_response",
        title: "HTTP 308 Redirect Snapshot",
        content: "HTTP/1.1 308 Permanent Redirect\r\nLocation: https://scopeguard-seven-black.vercel.app\r\nServer: Vercel"
      }
    ],
    created_at: "2026-09-27 12:04:22 UTC",
  }
];


export const MOCK_LOGS: LogEntry[] = [
  { id: "log-1", timestamp: "12:00:01", level: "info", source: "orchestrator", message: "Starting assessment 'ScopeGuard Security Baseline Scan' [Profile: Observe]" },
  { id: "log-2", timestamp: "12:00:02", level: "info", source: "policy_engine", message: "Validated target scope for 'scopeguard.vercel.app'. Zero-trust policy active." },
  { id: "log-3", timestamp: "12:00:05", level: "agent", source: "mock_ai", message: "Plan formulated: 1. Public header audit 2. CORS origin probe 3. Open redirect check 4. Reconnaissance" },
  { id: "log-4", timestamp: "12:02:30", level: "info", source: "worker", message: "Probing primary endpoint https://scopeguard-seven-black.vercel.app: HTTP 200 OK (Server: Vercel)." },
  { id: "log-5", timestamp: "12:03:15", level: "success", source: "finding_engine", message: "CORS protection verified: External untrusted origins safely rejected." },
  { id: "log-6", timestamp: "12:04:22", level: "success", source: "finding_engine", message: "Open Redirect validation passed: External redirection parameters safely ignored." },
  { id: "log-7", timestamp: "12:05:12", level: "info", source: "finding_engine", message: "Probing /.env: Returned HTTP 200 with HTML (SPA client-side router, not a credential leak)." },
];
