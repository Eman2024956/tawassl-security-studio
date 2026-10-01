import {
  Project,
  Target,
  Assessment,
  Proposal,
  Finding,
  MOCK_PROJECTS,
  MOCK_TARGETS,
  MOCK_ASSESSMENT,
  MOCK_PROPOSALS,
  MOCK_FINDINGS
} from './mockData';

// Global in-memory storage for serverless runtime
declare global {
  // eslint-disable-next-line no-var
  var __tawasslStore: {
    projects: Project[];
    targets: Target[];
    assessments: Assessment[];
    proposals: Proposal[];
    findings: Finding[];
  } | undefined;
}

if (!globalThis.__tawasslStore) {
  globalThis.__tawasslStore = {
    projects: [...MOCK_PROJECTS],
    targets: [...MOCK_TARGETS],
    assessments: [{ ...MOCK_ASSESSMENT }],
    proposals: [...MOCK_PROPOSALS],
    findings: [...MOCK_FINDINGS],
  };
}

export const serverStore = globalThis.__tawasslStore;
