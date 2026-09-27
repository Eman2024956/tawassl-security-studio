'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Language, translations } from './i18n';
import {
  MOCK_PROJECTS,
  MOCK_TARGETS,
  MOCK_ASSESSMENT,
  MOCK_PROPOSALS,
  MOCK_FINDINGS,
  MOCK_LOGS,
  Project,
  Target,
  Assessment,
  Proposal,
  Finding,
  LogEntry
} from './mockData';
import {
  fetchProjectsApi,
  createProjectApi,
  fetchTargetsApi,
  createTargetApi,
  fetchAssessmentsApi,
  createAssessmentApi,
  runAssessmentLiveApi,
  fetchFindingsApi,
  fetchProposalsApi
} from './api';

interface StudioContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  theme: 'dark' | 'light';
  setTheme: (t: 'dark' | 'light') => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isWizardOpen: boolean;
  setIsWizardOpen: (open: boolean) => void;
  isRunningTest: boolean;

  projects: Project[];
  targets: Target[];
  assessment: Assessment;
  proposals: Proposal[];
  findings: Finding[];
  logs: LogEntry[];

  approveProposal: (id: string) => void;
  rejectProposal: (id: string) => void;
  stopAssessment: () => void;
  runActiveAssessment: () => Promise<void>;
  createAndLaunchAssessment: (wizardData: any) => Promise<void>;
  addLog: (level: LogEntry['level'], source: string, message: string) => void;
  clearLogs: () => void;
  t: typeof translations.en;
}

const StudioContext = createContext<StudioContextType | undefined>(undefined);

export function StudioProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>('en');
  const [theme, setThemeState] = useState<'dark' | 'light'>('dark');
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [isWizardOpen, setIsWizardOpen] = useState<boolean>(false);
  const [isRunningTest, setIsRunningTest] = useState<boolean>(false);

  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS);
  const [targets, setTargets] = useState<Target[]>(MOCK_TARGETS);
  const [assessment, setAssessment] = useState<Assessment>(MOCK_ASSESSMENT);
  const [proposals, setProposals] = useState<Proposal[]>(MOCK_PROPOSALS);
  const [findings, setFindings] = useState<Finding[]>(MOCK_FINDINGS);
  const [logs, setLogs] = useState<LogEntry[]>(MOCK_LOGS);

  // Initialize theme & language from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('tawassl_theme') as 'dark' | 'light' | null;
    if (savedTheme) {
      setThemeState(savedTheme);
    }
    const savedLang = localStorage.getItem('tawassl_lang') as Language | null;
    if (savedLang) {
      setLanguageState(savedLang);
    }
  }, []);

  const setTheme = (t: 'dark' | 'light') => {
    setThemeState(t);
    try {
      localStorage.setItem('tawassl_theme', t);
    } catch {}
  };

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    try {
      localStorage.setItem('tawassl_lang', lang);
    } catch {}
  };

  // Sync document dir and class on theme/lang change
  useEffect(() => {
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Load real data from backend on initial mount
  useEffect(() => {
    async function loadBackendData() {
      try {
        const [dbProjects, dbTargets, dbAssessments, dbFindings] = await Promise.all([
          fetchProjectsApi(),
          fetchTargetsApi(),
          fetchAssessmentsApi(),
          fetchFindingsApi(),
        ]);

        if (dbProjects && dbProjects.length > 0) {
          setProjects(dbProjects);
        }
        if (dbTargets && dbTargets.length > 0) {
          setTargets(dbTargets);
        }
        if (dbAssessments && dbAssessments.length > 0) {
          setAssessment(dbAssessments[0]);
        }
        if (dbFindings && dbFindings.length > 0) {
          setFindings(dbFindings);
        }
      } catch (err) {
        console.warn('Backend loading deferred or using local cache:', err);
      }
    }
    loadBackendData();
  }, []);

  const addLog = (level: LogEntry['level'], source: string, message: string) => {
    const newLog: LogEntry = {
      id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      timestamp: new Date().toLocaleTimeString(),
      level,
      source,
      message,
    };
    setLogs((prev) => [...prev, newLog]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const runActiveAssessment = async () => {
    if (!assessment || !assessment.id) return;
    setIsRunningTest(true);
    addLog('info', 'orchestrator', `Starting live assessment execution for ${assessment.name}...`);

    try {
      const runResult = await runAssessmentLiveApi(assessment.id);
      if (runResult && runResult.assessment) {
        setAssessment(runResult.assessment);
      }
      if (runResult && runResult.debug_logs) {
        runResult.debug_logs.forEach((item: any) => {
          addLog(item.level, item.source, item.message);
        });
      }
      // Reload findings
      const latestFindings = await fetchFindingsApi(assessment.id);
      if (latestFindings && latestFindings.length > 0) {
        setFindings(latestFindings);
      }
    } catch (err: any) {
      addLog('error', 'orchestrator', `Live execution failed: ${err.message}`);
    } finally {
      setIsRunningTest(false);
    }
  };

  const createAndLaunchAssessment = async (wizardData: {
    projectName: string;
    targetType: string;
    authorizedDomains: string;
    baseUrls: string;
    allowedPorts: string;
    allowSubdomains: boolean;
    exclusions: string;
    profile: string;
    maxSteps: number;
    maxRequests: number;
    maxDurationSec: number;
  }) => {
    setIsRunningTest(true);
    setIsWizardOpen(false);
    setActiveTab('live'); // Switch immediately to live terminal

    try {
      addLog('info', 'wizard', `Creating project '${wizardData.projectName}' in local database...`);
      const newProj = await createProjectApi(
        wizardData.projectName,
        `Security assessment target for ${wizardData.authorizedDomains}`
      );

      const parsedDomains = wizardData.authorizedDomains
        .split(',')
        .map((d) => d.trim())
        .filter(Boolean);
      const parsedBaseUrls = wizardData.baseUrls
        .split(',')
        .map((u) => u.trim())
        .filter(Boolean);
      const parsedPorts = wizardData.allowedPorts
        .split(',')
        .map((p) => parseInt(p.trim(), 10))
        .filter((p) => !isNaN(p));
      const parsedExclusions = wizardData.exclusions
        .split(',')
        .map((e) => e.trim())
        .filter(Boolean);

      addLog('info', 'policy_engine', `Registering scope for ${parsedDomains.join(', ')} with zero-trust validation...`);
      const newTarget = await createTargetApi({
        project_id: newProj.id,
        name: parsedDomains[0] || 'Target Domain',
        target_type: wizardData.targetType,
        authorized_domains: parsedDomains,
        base_urls: parsedBaseUrls,
        allowed_ports: parsedPorts.length > 0 ? parsedPorts : [80, 443],
        allow_subdomains: wizardData.allowSubdomains,
        exclusions: parsedExclusions,
      });

      addLog('info', 'orchestrator', `Configuring assessment under profile '${wizardData.profile}'...`);
      const newAssess = await createAssessmentApi({
        project_id: newProj.id,
        target_id: newTarget.id,
        name: `${wizardData.projectName} - Audit`,
        profile: wizardData.profile,
        ai_provider: 'mock',
        model_id: 'mock-sec-v1',
        max_steps: wizardData.maxSteps,
        max_requests: wizardData.maxRequests,
        max_tool_calls: 30,
      });

      // Update state so project & target immediately appear in lists and header
      setProjects((prev) => [newProj, ...prev]);
      setTargets((prev) => [newTarget, ...prev]);
      setAssessment(newAssess);

      addLog('success', 'orchestrator', `Assessment '${newAssess.name}' created! Launching live security diagnostics...`);

      // Run live tests against the target domain
      const runResult = await runAssessmentLiveApi(newAssess.id);
      if (runResult && runResult.assessment) {
        setAssessment(runResult.assessment);
      }
      if (runResult && runResult.debug_logs) {
        runResult.debug_logs.forEach((item: any) => {
          addLog(item.level, item.source, item.message);
        });
      }

      // Fetch newly recorded findings
      const newFindings = await fetchFindingsApi(newAssess.id);
      if (newFindings && newFindings.length > 0) {
        setFindings(newFindings);
      }
    } catch (err: any) {
      addLog('error', 'orchestrator', `Error creating/launching assessment: ${err.message}`);
    } finally {
      setIsRunningTest(false);
    }
  };

  const approveProposal = (id: string) => {
    setProposals((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: 'approved' } : p))
    );
    addLog('success', 'approval_engine', `Proposal ${id} approved by user. Scheduled for isolated execution.`);
  };

  const rejectProposal = (id: string) => {
    setProposals((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: 'rejected' } : p))
    );
    addLog('warn', 'approval_engine', `Proposal ${id} rejected by user. Command will not be run.`);
  };

  const stopAssessment = () => {
    setAssessment((prev) => ({
      ...prev,
      status: 'cancelled',
      completed_at: new Date().toISOString(),
    }));
    addLog('error', 'orchestrator', 'Emergency Stop invoked by user. Halting all worker processes.');
  };

  const t = translations[language];

  return (
    <StudioContext.Provider
      value={{
        language,
        setLanguage,
        theme,
        setTheme,
        activeTab,
        setActiveTab,
        isWizardOpen,
        setIsWizardOpen,
        isRunningTest,
        projects,
        targets,
        assessment,
        proposals,
        findings,
        logs,
        approveProposal,
        rejectProposal,
        stopAssessment,
        runActiveAssessment,
        createAndLaunchAssessment,
        addLog,
        clearLogs,
        t,
      }}
    >
      {children}
    </StudioContext.Provider>
  );
}

export function useStudio() {
  const context = useContext(StudioContext);
  if (!context) {
    throw new Error('useStudio must be used within a StudioProvider');
  }
  return context;
}
