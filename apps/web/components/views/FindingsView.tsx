'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import {
  Bug,
  AlertTriangle,
  CheckCircle2,
  FileCode,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ExternalLink,
  Lock
} from 'lucide-react';
import { Finding } from '../../lib/mockData';

export default function FindingsView() {
  const { findings, t } = useStudio();
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(findings[0] || null);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'critical':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'high':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'medium':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'low':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default:
        return 'bg-zinc-800 text-zinc-400 border-zinc-700';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <Bug className="w-5 h-5 text-rose-400" />
            <span>{t.findings.title}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">{t.findings.description}</p>
        </div>
        <div className="text-[11px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-3 py-1 rounded-md">
          {findings.length} Discovered Findings
        </div>
      </div>

      {/* Two Column Layout: List and Detailed Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Finding Cards */}
        <div className="lg:col-span-5 space-y-3">
          {findings.map((finding) => {
            const isSelected = selectedFinding?.id === finding.id;
            return (
              <div
                key={finding.id}
                onClick={() => setSelectedFinding(finding)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  isSelected
                    ? 'border-cyan-500 bg-zinc-900 shadow-md'
                    : 'border-zinc-800 bg-zinc-900/40 hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded border ${getSeverityBadge(finding.severity)}`}>
                    {finding.severity}
                  </span>
                  <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded">
                    {t.findingStatuses[finding.status] || finding.status}
                  </span>
                </div>
                <h3 className="text-xs font-semibold text-zinc-100 leading-snug">{finding.title}</h3>
                <p className="text-[11px] font-mono text-zinc-400 mt-1 truncate">{finding.affected_asset}</p>
              </div>
            );
          })}
        </div>

        {/* Right: Selected Finding Inspector */}
        <div className="lg:col-span-7">
          {selectedFinding ? (
            <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/60 space-y-5 text-xs">
              {/* Finding Title & Severity Header */}
              <div className="border-b border-zinc-800 pb-3">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded border ${getSeverityBadge(selectedFinding.severity)}`}>
                    {selectedFinding.severity}
                  </span>
                  <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded">
                    Status: {selectedFinding.status}
                  </span>
                  <span className="text-[10px] font-mono text-zinc-400">Confidence: {selectedFinding.confidence}</span>
                </div>
                <h2 className="text-base font-bold text-zinc-100">{selectedFinding.title}</h2>
                <div className="text-[11px] font-mono text-cyan-400 mt-1">{selectedFinding.affected_asset}</div>
              </div>

              {/* Reproduction Steps */}
              <div>
                <h4 className="font-semibold text-zinc-300 text-xs mb-1">Reproduction Steps:</h4>
                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 font-mono text-[11px] text-zinc-300 whitespace-pre-wrap leading-relaxed">
                  {selectedFinding.reproduction_steps}
                </div>
              </div>

              {/* Observed vs Expected */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
                <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-900/30">
                  <span className="font-semibold text-rose-300 block mb-1">Observed Behavior:</span>
                  <p className="text-zinc-300 font-mono">{selectedFinding.observed_result}</p>
                </div>
                <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/30">
                  <span className="font-semibold text-emerald-300 block mb-1">Expected Secure Behavior:</span>
                  <p className="text-zinc-300 font-mono">{selectedFinding.expected_result}</p>
                </div>
              </div>

              {/* Impact & Remediation */}
              <div className="space-y-3 text-xs">
                {selectedFinding.impact && (
                  <div>
                    <span className="font-semibold text-zinc-300 block mb-0.5">Impact:</span>
                    <p className="text-zinc-400 leading-relaxed">{selectedFinding.impact}</p>
                  </div>
                )}
                {selectedFinding.remediation && (
                  <div>
                    <span className="font-semibold text-emerald-400 block mb-0.5">Suggested Remediation:</span>
                    <p className="text-zinc-300 leading-relaxed bg-zinc-950 p-2.5 rounded border border-zinc-800">
                      {selectedFinding.remediation}
                    </p>
                  </div>
                )}
              </div>

              {/* Attached Evidence Items */}
              <div>
                <h4 className="font-semibold text-zinc-300 text-xs mb-2 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Verified Evidence References:</span>
                </h4>
                <div className="space-y-2">
                  {selectedFinding.evidence.map((ev, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 font-mono text-[11px]">
                      <div className="text-cyan-400 font-bold mb-1">{ev.title}</div>
                      <pre className="text-zinc-300 whitespace-pre-wrap overflow-x-auto leading-relaxed">{ev.content}</pre>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-xl border border-zinc-800 text-center text-zinc-500 text-xs">
              Select a finding from the list to view reproduction details and evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
