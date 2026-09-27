'use client';

import React from 'react';
import { useStudio } from '../lib/context';
import ThemeToggle from './ThemeToggle';
import {
  ShieldAlert,
  AlertTriangle,
  Play,
  Square,
  Globe,
  Sun,
  Moon,
  PlusCircle,
  Activity,
  Cpu,
  Layers
} from 'lucide-react';

export default function Header() {
  const {
    language,
    setLanguage,
    theme,
    setTheme,
    assessment,
    targets,
    setIsWizardOpen,
    stopAssessment,
    runActiveAssessment,
    isRunningTest,
    t
  } = useStudio();

  const activeTarget = targets.find((tgt) => tgt.id === assessment.target_id) || targets[0];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 animate-pulse';
      case 'awaiting_approval':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'queued':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
      case 'completed':
        return 'bg-teal-500/20 text-teal-400 border-teal-500/40';
      case 'cancelled':
        return 'bg-zinc-500/20 text-zinc-400 border-zinc-500/40';
      case 'failed':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      default:
        return 'bg-zinc-500/20 text-zinc-300 border-zinc-600';
    }
  };

  const isLiveTarget = (activeTarget?.environment_mode ?? 'live') === 'live';
  const aiProviderLabel =
    assessment.ai_provider === 'mock' || assessment.model_id === 'mock-sec-v1'
      ? t.targetMetadata?.mockRuleEngine || 'Mock Rule Engine (Simulated)'
      : assessment.ai_provider === 'gemini'
      ? `Google Gemini (${assessment.model_id})`
      : assessment.ai_provider === 'openai'
      ? `OpenAI GPT (${assessment.model_id})`
      : `${assessment.ai_provider} (${assessment.model_id})`;

  return (
    <header className="border-b border-slate-200 dark:border-zinc-800 bg-white/95 dark:bg-zinc-950/80 backdrop-blur px-5 py-3 sticky top-0 z-40 flex flex-wrap items-center justify-between gap-4 transition-colors duration-200 shadow-xs">
      {/* Brand & Active Target Badge */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-md shadow-cyan-900/20">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-wide text-slate-900 dark:text-zinc-100 flex items-center gap-2">
              {t.appName}
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-300 dark:border-zinc-700 font-semibold">
                v0.1.0-alpha
              </span>
            </h1>
            <p className="text-[11px] text-slate-500 dark:text-zinc-400 hidden sm:block">{t.subtitle}</p>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-200 dark:bg-zinc-800 hidden md:block" />

        {/* Active Target Meta */}
        <div className="hidden lg:flex items-center gap-2 text-xs">
          <span className="text-slate-500 dark:text-zinc-400 flex items-center gap-1 font-medium">
            <Globe className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
            {t.header.activeTarget}:
          </span>
          <span className="text-slate-800 dark:text-zinc-200 font-mono bg-slate-100 dark:bg-zinc-900 px-2 py-0.5 rounded border border-slate-200 dark:border-zinc-800 font-semibold">
            {activeTarget ? activeTarget.name : 'None'}
          </span>
          {/* Target Type LIVE | MOCK Badge */}
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase tracking-wider border ${
              isLiveTarget
                ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30'
                : 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30'
            }`}
          >
            {isLiveTarget ? (t.targetMetadata?.live || 'LIVE') : (t.targetMetadata?.mock || 'MOCK')}
          </span>
          <span className="text-[11px] font-mono text-slate-500 dark:text-zinc-400 hidden 2xl:inline">
            [{isLiveTarget ? (t.targetMetadata?.realHttp || 'Real HTTP Requests') : (t.targetMetadata?.simulated || 'Simulated')}]
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-slate-700 dark:text-zinc-300">
            {t.profiles[assessment.profile]}
          </span>
        </div>
      </div>

      {/* Center Status Indicators */}
      <div className="flex items-center gap-3">
        {/* Status Badge */}
        <div className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1.5 ${getStatusBadge(assessment.status)}`}>
          <span className="relative flex h-2 w-2">
            {assessment.status === 'running' && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
          </span>
          {t.statuses[assessment.status] || assessment.status}
        </div>

        {/* AI Provider & Model (Mock Rule Engine clearly labeled) */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs font-mono text-slate-700 dark:text-zinc-300">
          <Cpu className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span className="font-medium">{aiProviderLabel}</span>
        </div>

        {/* Request Budget Progress */}
        <div className="hidden xl:flex items-center gap-2 text-xs bg-slate-100 dark:bg-zinc-900 px-3 py-1 rounded-md border border-slate-200 dark:border-zinc-800">
          <span className="text-slate-500 dark:text-zinc-400 font-medium">{t.header.requests}:</span>
          <span className="font-mono text-cyan-700 dark:text-cyan-400 font-bold">{assessment.requests_made}</span>
          <span className="text-slate-400 dark:text-zinc-500">/</span>
          <span className="font-mono text-slate-700 dark:text-zinc-300">{assessment.max_requests}</span>
          <div className="w-16 h-1.5 bg-slate-200 dark:bg-zinc-800 rounded-full overflow-hidden ml-1">
            <div
              className="h-full bg-cyan-600 dark:bg-cyan-500 rounded-full"
              style={{ width: `${Math.min(100, (assessment.requests_made / assessment.max_requests) * 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Actions & Utilities */}
      <div className="flex items-center gap-2">
        {/* Run Live Test Button */}
        <button
          onClick={runActiveAssessment}
          disabled={isRunningTest}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white transition shadow-sm cursor-pointer"
          title="Run Live Security Audit on Target"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isRunningTest ? 'Auditing...' : 'Run Live Audit'}</span>
        </button>

        {/* Emergency Stop Button */}
        {assessment.status !== 'cancelled' && assessment.status !== 'completed' && (
          <button
            onClick={stopAssessment}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-700 dark:text-rose-400 border border-rose-300 dark:border-rose-500/40 transition cursor-pointer"
            title={t.header.stopBtn}
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            <span className="hidden sm:inline">{t.header.stopBtn}</span>
          </button>
        )}

        {/* New Assessment Wizard trigger */}
        <button
          onClick={() => setIsWizardOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm cursor-pointer"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>{t.header.newAssessment}</span>
        </button>

        {/* Language Switcher */}
        <button
          onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}
          className="px-2.5 py-1.5 text-xs font-semibold rounded bg-slate-100 hover:bg-slate-200 dark:bg-zinc-900 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-300 dark:border-zinc-800 transition cursor-pointer"
          title="Toggle Language / تبديل اللغة"
        >
          {language === 'en' ? 'عربي' : 'English'}
        </button>

        {/* Theme Toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
}
