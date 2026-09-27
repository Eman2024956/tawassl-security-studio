'use client';

import React from 'react';
import { useStudio } from '../lib/context';
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

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur px-5 py-3 sticky top-0 z-40 flex flex-wrap items-center justify-between gap-4">
      {/* Brand & Active Target Badge */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-900/30">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-wide text-zinc-100 flex items-center gap-2">
              {t.appName}
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                v0.1.0-alpha
              </span>
            </h1>
            <p className="text-[11px] text-zinc-400 hidden sm:block">{t.subtitle}</p>
          </div>
        </div>

        <div className="h-5 w-px bg-zinc-800 hidden md:block" />

        {/* Active Target Meta */}
        <div className="hidden lg:flex items-center gap-2 text-xs">
          <span className="text-zinc-400 flex items-center gap-1 font-medium">
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            {t.header.activeTarget}:
          </span>
          <span className="text-zinc-200 font-mono bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
            {activeTarget ? activeTarget.name : 'None'}
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-900 border border-zinc-800 text-zinc-300">
            {t.profiles[assessment.profile]}
          </span>
        </div>
      </div>

      {/* Center Status Indicators */}
      <div className="flex items-center gap-3">
        {/* Status Badge */}
        <div className={`px-2.5 py-1 rounded-full text-xs font-medium border flex items-center gap-1.5 ${getStatusBadge(assessment.status)}`}>
          <span className="relative flex h-2 w-2">
            {assessment.status === 'running' && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
          </span>
          {t.statuses[assessment.status] || assessment.status}
        </div>

        {/* AI Provider & Model */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-300">
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span>{assessment.ai_provider}</span>
          <span className="text-zinc-500">/</span>
          <span className="text-zinc-400">{assessment.model_id}</span>
        </div>

        {/* Request Budget Progress */}
        <div className="hidden xl:flex items-center gap-2 text-xs bg-zinc-900 px-3 py-1 rounded-md border border-zinc-800">
          <span className="text-zinc-400">{t.header.requests}:</span>
          <span className="font-mono text-cyan-400">{assessment.requests_made}</span>
          <span className="text-zinc-500">/</span>
          <span className="font-mono text-zinc-300">{assessment.max_requests}</span>
          <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden ml-1">
            <div
              className="h-full bg-cyan-500 rounded-full"
              style={{ width: `${Math.min(100, (assessment.requests_made / assessment.max_requests) * 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Actions & Utilities */}
      <div className="flex items-center gap-2">
        {/* Emergency Stop Button */}
        {assessment.status !== 'cancelled' && assessment.status !== 'completed' && (
          <button
            onClick={stopAssessment}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/40 transition cursor-pointer"
            title={t.header.stopBtn}
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            <span className="hidden sm:inline">{t.header.stopBtn}</span>
          </button>
        )}

        {/* New Assessment Wizard trigger */}
        <button
          onClick={() => setIsWizardOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm cursor-pointer"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>{t.header.newAssessment}</span>
        </button>

        {/* Language Switcher */}
        <button
          onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}
          className="px-2.5 py-1.5 text-xs font-medium rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 transition"
          title="Toggle Language / تبديل اللغة"
        >
          {language === 'en' ? 'عربي' : 'English'}
        </button>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-1.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 transition"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-zinc-600" />}
        </button>
      </div>
    </header>
  );
}
