'use client';

import React from 'react';
import { useStudio } from '../lib/context';
import {
  LayoutDashboard,
  FolderGit2,
  Crosshair,
  FileCheck2,
  Bot,
  ListOrdered,
  Terminal,
  Bug,
  FileText,
  BookOpen,
  Settings as SettingsIcon,
  ShieldCheck,
  UserCheck
} from 'lucide-react';

export default function Sidebar() {
  const { activeTab, setActiveTab, proposals, findings, t } = useStudio();

  const pendingProposalsCount = proposals.filter((p) => p.status === 'pending').length;
  const confirmedFindingsCount = findings.filter((f) => f.status === 'confirmed').length;

  const navItems = [
    { id: 'dashboard', label: t.nav.dashboard, icon: LayoutDashboard },
    { id: 'projects', label: t.nav.projects, icon: FolderGit2 },
    { id: 'targets', label: t.nav.targets, icon: Crosshair },
    { id: 'plans', label: t.nav.plans, icon: FileCheck2 },
    { id: 'agent', label: t.nav.agent, icon: Bot },
    {
      id: 'queue',
      label: t.nav.commandQueue,
      icon: ListOrdered,
      badge: pendingProposalsCount > 0 ? pendingProposalsCount : null,
      badgeColor: 'bg-amber-500/20 text-amber-400 border border-amber-500/40',
    },
    { id: 'live', label: t.nav.liveOutput, icon: Terminal },
    {
      id: 'findings',
      label: t.nav.findings,
      icon: Bug,
      badge: confirmedFindingsCount > 0 ? confirmedFindingsCount : null,
      badgeColor: 'bg-rose-500/20 text-rose-400 border border-rose-500/40',
    },
    { id: 'reports', label: t.nav.reports, icon: FileText },
    { id: 'help', label: t.nav.helpDocs, icon: BookOpen },
    { id: 'settings', label: t.nav.settings, icon: SettingsIcon },
    {
      id: 'developer',
      label: t.nav.developer,
      icon: UserCheck,
      badge: '1988',
      badgeColor: 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/40'
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950/60 p-3 flex flex-col justify-between shrink-0 select-none transition-colors duration-200">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition cursor-pointer ${
                isActive
                  ? 'bg-cyan-50 dark:bg-zinc-800/90 text-cyan-700 dark:text-cyan-400 font-semibold shadow-xs border border-cyan-200/80 dark:border-transparent'
                  : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-900/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-600 dark:text-cyan-400' : 'text-slate-400 dark:text-zinc-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== null && (
                <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Safety Notice Footer */}
      <div className="p-3 rounded-lg bg-slate-100 dark:bg-zinc-900/70 border border-slate-200 dark:border-zinc-800/80 text-[11px] text-slate-600 dark:text-zinc-400 space-y-1">
        <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-semibold text-xs">
          <ShieldCheck className="w-4 h-4" />
          <span>Scope Enforcement</span>
        </div>
        <p className="text-[10px] leading-relaxed text-slate-500 dark:text-zinc-400">
          Zero-trust egress guard active. External host calls restricted to explicit target list.
        </p>
      </div>
    </aside>
  );
}
