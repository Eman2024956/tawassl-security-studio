// Client API helpers for Tawassl Security Studio backend

const API_BASE = '/api';

const HEADERS = {
  'Content-Type': 'application/json',
  'X-Tawassl-Client': 'studio-web-ui',
};

export async function fetchProjectsApi() {
  const res = await fetch(`${API_BASE}/projects`, { headers: HEADERS });
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function createProjectApi(name: string, description?: string) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ name, description }),
  });
  if (!res.ok) throw new Error('Failed to create project');
  return res.json();
}

export async function fetchTargetsApi(projectId?: string) {
  const url = projectId ? `${API_BASE}/targets?project_id=${projectId}` : `${API_BASE}/targets`;
  const res = await fetch(url, { headers: HEADERS });
  if (!res.ok) throw new Error('Failed to fetch targets');
  return res.json();
}

export async function createTargetApi(data: {
  project_id: string;
  name: string;
  target_type: string;
  environment_mode?: string;
  authorized_domains: string[];
  base_urls: string[];
  allowed_ports: number[];
  allow_subdomains: boolean;
  exclusions: string[];
}) {
  const res = await fetch(`${API_BASE}/targets`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create target');
  return res.json();
}

export async function fetchAssessmentsApi(targetId?: string) {
  const url = targetId ? `${API_BASE}/assessments?target_id=${targetId}` : `${API_BASE}/assessments`;
  const res = await fetch(url, { headers: HEADERS });
  if (!res.ok) throw new Error('Failed to fetch assessments');
  return res.json();
}

export async function createAssessmentApi(data: {
  project_id: string;
  target_id: string;
  name: string;
  profile: string;
  ai_provider?: string;
  model_id?: string;
  max_steps?: number;
  max_requests?: number;
  max_tool_calls?: number;
}) {
  const res = await fetch(`${API_BASE}/assessments`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create assessment');
  return res.json();
}

export async function runAssessmentLiveApi(assessmentId: string) {
  const res = await fetch(`${API_BASE}/assessments/${assessmentId}/run`, {
    method: 'POST',
    headers: HEADERS,
  });
  if (!res.ok) throw new Error('Failed to run live assessment');
  return res.json();
}

export async function fetchFindingsApi(assessmentId?: string) {
  const url = assessmentId ? `${API_BASE}/findings?assessment_id=${assessmentId}` : `${API_BASE}/findings`;
  const res = await fetch(url, { headers: HEADERS });
  if (!res.ok) throw new Error('Failed to fetch findings');
  return res.json();
}

export async function fetchProposalsApi(assessmentId?: string) {
  const url = assessmentId ? `${API_BASE}/approvals?assessment_id=${assessmentId}` : `${API_BASE}/approvals`;
  const res = await fetch(url, { headers: HEADERS });
  if (!res.ok) throw new Error('Failed to fetch proposals');
  return res.json();
}
