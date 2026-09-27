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
  Settings as SettingsIcon,
  ShieldCheck
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
    { id: 'settings', label: t.nav.settings, icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 border-r border-zinc-800 bg-zinc-950/60 p-3 flex flex-col justify-between shrink-0 select-none">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
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
                  ? 'bg-zinc-800/90 text-cyan-400 font-semibold shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-zinc-400'}`} />
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
      <div className="p-3 rounded-lg bg-zinc-900/70 border border-zinc-800/80 text-[11px] text-zinc-400 space-y-1">
        <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-xs">
          <ShieldCheck className="w-4 h-4" />
          <span>Scope Enforcement</span>
        </div>
        <p className="text-[10px] leading-relaxed">
          Zero-trust egress guard active. External host calls restricted to explicit target list.
        </p>
      </div>
    </aside>
  );
}
