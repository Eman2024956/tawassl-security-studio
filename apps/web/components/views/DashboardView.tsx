'use client';

import React from 'react';
import { useStudio } from '../../lib/context';
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  ListOrdered,
  Bug,
  Cpu,
  ArrowUpRight,
  Clock,
  Layers,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function DashboardView() {
  const { assessment, targets, findings, proposals, setActiveTab, t } = useStudio();

  const activeTarget = targets.find((tgt) => tgt.id === assessment.target_id) || targets[0];
  const pendingCount = proposals.filter((p) => p.status === 'pending').length;
  const confirmedCount = findings.filter((f) => f.status === 'confirmed').length;

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="p-5 rounded-xl border border-zinc-800 bg-gradient-to-r from-zinc-900 via-zinc-900/80 to-cyan-950/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400 bg-cyan-950/50 border border-cyan-800/40 px-2 py-0.5 rounded">
            Active Workspace
          </span>
          <h2 className="text-xl font-bold text-zinc-100 mt-2">{assessment.name}</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Target: <span className="font-mono text-zinc-300">{activeTarget?.name}</span> • Profile:{' '}
            <span className="text-emerald-400 font-medium">{t.profiles[assessment.profile]}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('queue')}
            className="px-3.5 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-200 border border-zinc-700 flex items-center gap-2 transition cursor-pointer"
          >
            <ListOrdered className="w-4 h-4 text-amber-400" />
            <span>Pending Approvals ({pendingCount})</span>
          </button>
          <button
            onClick={() => setActiveTab('live')}
            className="px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-semibold text-white shadow-md flex items-center gap-2 transition cursor-pointer"
          >
            <Activity className="w-4 h-4" />
            <span>View Live Stream</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Budget Usage */}
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Requests Budget</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-bold font-mono text-zinc-100">
              {assessment.requests_made}{' '}
              <span className="text-sm font-normal text-zinc-500">/ {assessment.max_requests}</span>
            </div>
            <div className="w-full h-1.5 bg-zinc-800 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-cyan-500 rounded-full"
                style={{ width: `${(assessment.requests_made / assessment.max_requests) * 100}%` }}
              />
            </div>
          </div>
          <span className="text-[11px] text-zinc-400 font-mono">
            {assessment.max_requests - assessment.requests_made} requests remaining
          </span>
        </div>

        {/* Metric 2: Agent Steps */}
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Agent Steps</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-bold font-mono text-zinc-100">
              {assessment.steps_taken}{' '}
              <span className="text-sm font-normal text-zinc-500">/ {assessment.max_steps}</span>
            </div>
            <div className="w-full h-1.5 bg-zinc-800 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full"
                style={{ width: `${(assessment.steps_taken / assessment.max_steps) * 100}%` }}
              />
            </div>
          </div>
          <span className="text-[11px] text-zinc-400 font-mono">{assessment.tool_calls_made} tool calls issued</span>
        </div>

        {/* Metric 3: Findings */}
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Confirmed Findings</span>
            <Bug className="w-4 h-4 text-rose-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-bold font-mono text-rose-400">{confirmedCount}</div>
            <div className="flex items-center gap-2 mt-2 text-[11px] text-zinc-400">
              <span className="text-rose-400 font-medium">1 High</span> •{' '}
              <span className="text-amber-400 font-medium">1 Medium</span>
            </div>
          </div>
          <span className="text-[11px] text-zinc-400">Supported by verified evidence</span>
        </div>

        {/* Metric 4: Human Approvals */}
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Command Proposals</span>
            <ListOrdered className="w-4 h-4 text-amber-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-bold font-mono text-amber-400">{pendingCount}</div>
            <div className="flex items-center gap-2 mt-2 text-[11px] text-zinc-400">
              <span>{proposals.length} total proposals</span>
            </div>
          </div>
          <span className="text-[11px] text-zinc-400">Requires atomic user approval</span>
        </div>
      </div>

      {/* Two Column Layout: Recent Findings & Scope Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Discovered Findings */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <Bug className="w-4 h-4 text-rose-400" />
              <span>Recent Discovered Findings</span>
            </h3>
            <button
              onClick={() => setActiveTab('findings')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
            >
              <span>View all</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5">
            {findings.map((f) => (
              <div
                key={f.id}
                onClick={() => setActiveTab('findings')}
                className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/70 hover:border-zinc-700 transition cursor-pointer"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-xs text-zinc-200">{f.title}</span>
                  <span
                    className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded font-bold ${
                      f.severity === 'high'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {f.severity}
                  </span>
                </div>
                <div className="text-[11px] font-mono text-zinc-400 mt-1 truncate">{f.affected_asset}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Active Scope & Boundaries */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Active Scope Boundaries</span>
            </h3>
            <span className="text-[10px] font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 px-2 py-0.5 rounded">
              Zero-Trust Enforced
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <span className="text-zinc-400 block text-[11px]">Authorized Domain(s):</span>
              <span className="font-mono text-zinc-200">
                {activeTarget?.authorized_domains?.join(', ') || 'None'}
              </span>
            </div>
            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <span className="text-zinc-400 block text-[11px]">Permitted Base URLs:</span>
              <span className="font-mono text-zinc-200">
                {activeTarget?.base_urls?.join(', ') || 'None'}
              </span>
            </div>
            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <span className="text-zinc-400 block text-[11px]">Explicit Exclusions:</span>
              <span className="font-mono text-rose-400">
                {activeTarget?.exclusions?.join(', ') || 'None'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
