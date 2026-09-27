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

interface StudioContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  theme: 'dark' | 'light';
  setTheme: (t: 'dark' | 'light') => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isWizardOpen: boolean;
  setIsWizardOpen: (open: boolean) => void;

  projects: Project[];
  targets: Target[];
  assessment: Assessment;
  proposals: Proposal[];
  findings: Finding[];
  logs: LogEntry[];

  approveProposal: (id: string) => void;
  rejectProposal: (id: string) => void;
  stopAssessment: () => void;
  addLog: (level: LogEntry['level'], source: string, message: string) => void;
  t: typeof translations.en;
}

const StudioContext = createContext<StudioContextType | undefined>(undefined);

export function StudioProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [isWizardOpen, setIsWizardOpen] = useState<boolean>(false);

  const [projects] = useState<Project[]>(MOCK_PROJECTS);
  const [targets] = useState<Target[]>(MOCK_TARGETS);
  const [assessment, setAssessment] = useState<Assessment>(MOCK_ASSESSMENT);
  const [proposals, setProposals] = useState<Proposal[]>(MOCK_PROPOSALS);
  const [findings, setFindings] = useState<Finding[]>(MOCK_FINDINGS);
  const [logs, setLogs] = useState<LogEntry[]>(MOCK_LOGS);

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

  const addLog = (level: LogEntry['level'], source: string, message: string) => {
    const newLog: LogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date().toLocaleTimeString(),
      level,
      source,
      message,
    };
    setLogs((prev) => [...prev, newLog]);
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
        projects,
        targets,
        assessment,
        proposals,
        findings,
        logs,
        approveProposal,
        rejectProposal,
        stopAssessment,
        addLog,
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
