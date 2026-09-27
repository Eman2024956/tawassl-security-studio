'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import {
  Bug,
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  Eye,
  HelpCircle,
  ShieldAlert,
  Info
} from 'lucide-react';
import { Finding } from '../../lib/mockData';

export default function FindingsView() {
  const { findings, targets, assessment, t } = useStudio();
  const [filterTab, setFilterTab] = useState<'all' | 'finding' | 'observation' | 'passed_control' | 'inconclusive'>('all');

  const activeTarget = targets.find((t) => t.id === assessment?.target_id) || targets[0];
  const isMockTarget = activeTarget?.environment_mode === 'mock';

  // Prevent mixing: for LIVE targets, exclude simulated findings
  const cleanFindings = findings.filter((f) => {
    if (isMockTarget) return true;
    return !f.title.includes('[SIMULATED]') && f.impact !== 'Simulated synthetic result for testing. Zero live network impact.';
  });

  const getResultType = (f: Finding): 'passed_control' | 'observation' | 'finding' | 'inconclusive' => {
    // Requirement 5: Before reporting secret exposure, require sensitive_file_content_verified = true
    const isSensitivePath = f.title?.toLowerCase().includes('env') || f.affected_asset?.toLowerCase().includes('.env');
    if (isSensitivePath && !f.sensitive_file_content_verified) {
      if (f.result_type === 'passed_control') return 'passed_control';
      return 'observation';
    }

    if (f.result_type) return f.result_type;
    if (f.severity === 'info' || f.status === 'observation') return 'observation';
    if (f.status === 'inconclusive') return 'inconclusive';
    if (f.confirmed_vulnerability) return 'finding';
    return 'finding';
  };

  const confirmedVulns = cleanFindings.filter((f) => getResultType(f) === 'finding');
  const observations = cleanFindings.filter((f) => getResultType(f) === 'observation');
  const passedControls = cleanFindings.filter((f) => getResultType(f) === 'passed_control');
  const inconclusiveTests = cleanFindings.filter((f) => getResultType(f) === 'inconclusive');

  const filteredFindings = cleanFindings.filter((f) => {
    if (filterTab === 'all') return true;
    return getResultType(f) === filterTab;
  });

  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(filteredFindings[0] || cleanFindings[0] || null);

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

  const getResultTypeBadge = (rtype: 'passed_control' | 'observation' | 'finding' | 'inconclusive') => {
    switch (rtype) {
      case 'finding':
        return {
          label: t.resultTypes?.finding || 'Confirmed Vulnerability',
          style: 'bg-rose-950/60 text-rose-300 border-rose-700/50',
          icon: <AlertTriangle className="w-3 h-3 text-rose-400" />
        };
      case 'observation':
        return {
          label: t.resultTypes?.observation || 'Security Observation',
          style: 'bg-cyan-950/60 text-cyan-300 border-cyan-700/50',
          icon: <Eye className="w-3 h-3 text-cyan-400" />
        };
      case 'passed_control':
        return {
          label: t.resultTypes?.passed_control || 'Passed Control',
          style: 'bg-emerald-950/60 text-emerald-300 border-emerald-700/50',
          icon: <CheckCircle2 className="w-3 h-3 text-emerald-400" />
        };
      case 'inconclusive':
        return {
          label: t.resultTypes?.inconclusive || 'Inconclusive Test',
          style: 'bg-zinc-900 text-zinc-400 border-zinc-700',
          icon: <HelpCircle className="w-3 h-3 text-zinc-400" />
        };
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
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-mono text-rose-400 bg-rose-950/40 border border-rose-800/40 px-2.5 py-1 rounded-md">
            {confirmedVulns.length} Vulnerabilities
          </span>
          <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2.5 py-1 rounded-md">
            {observations.length} Observations
          </span>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2.5 py-1 rounded-md">
            {passedControls.length} Passed Controls
          </span>
        </div>
      </div>

      {/* Segmented Filter Tabs */}
      {isMockTarget && (
        <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/25 flex items-center gap-2 text-xs text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Notice: Target is set to MOCK mode. All findings below are simulated synthetic outputs for rule engine demonstration.</span>
        </div>
      )}

      <div className="flex flex-wrap gap-1.5 p-1 bg-zinc-900/80 border border-zinc-800 rounded-lg text-xs">
        <button
          onClick={() => {
            setFilterTab('all');
            setSelectedFinding(cleanFindings[0] || null);
          }}
          className={`px-3 py-1.5 rounded-md font-medium transition cursor-pointer ${
            filterTab === 'all' ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          {t.findings.tabs?.all || 'All Results'} ({cleanFindings.length})
        </button>
        <button
          onClick={() => {
            setFilterTab('finding');
            setSelectedFinding(confirmedVulns[0] || null);
          }}
          className={`px-3 py-1.5 rounded-md font-medium transition flex items-center gap-1.5 cursor-pointer ${
            filterTab === 'finding' ? 'bg-rose-900/40 text-rose-300 border border-rose-700/40 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Bug className="w-3.5 h-3.5 text-rose-400" />
          <span>{t.findings.tabs?.findings || 'Confirmed Vulnerabilities'}</span> ({confirmedVulns.length})
        </button>
        <button
          onClick={() => {
            setFilterTab('observation');
            setSelectedFinding(observations[0] || null);
          }}
          className={`px-3 py-1.5 rounded-md font-medium transition flex items-center gap-1.5 cursor-pointer ${
            filterTab === 'observation' ? 'bg-cyan-900/40 text-cyan-300 border border-cyan-700/40 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Eye className="w-3.5 h-3.5 text-cyan-400" />
          <span>{t.findings.tabs?.observations || 'Security Observations'}</span> ({observations.length})
        </button>
        <button
          onClick={() => {
            setFilterTab('passed_control');
            setSelectedFinding(passedControls[0] || null);
          }}
          className={`px-3 py-1.5 rounded-md font-medium transition flex items-center gap-1.5 cursor-pointer ${
            filterTab === 'passed_control' ? 'bg-emerald-900/40 text-emerald-300 border border-emerald-700/40 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>{t.findings.tabs?.passed || 'Passed Controls'}</span> ({passedControls.length})
        </button>
        {inconclusiveTests.length > 0 && (
          <button
            onClick={() => {
              setFilterTab('inconclusive');
              setSelectedFinding(inconclusiveTests[0] || null);
            }}
            className={`px-3 py-1.5 rounded-md font-medium transition flex items-center gap-1.5 cursor-pointer ${
              filterTab === 'inconclusive' ? 'bg-zinc-800 text-zinc-200 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 text-zinc-400" />
            <span>{t.findings.tabs?.inconclusive || 'Inconclusive'}</span> ({inconclusiveTests.length})
          </button>
        )}
      </div>

      {/* Two Column Layout: List and Detailed Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Cards List */}
        <div className="lg:col-span-5 space-y-3">
          {filteredFindings.length === 0 ? (
            <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40 text-center space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
              <div className="text-xs font-semibold text-zinc-200">
                {filterTab === 'finding'
                  ? 'No confirmed vulnerabilities were identified by the tests executed within this assessment scope.'
                  : 'No entries found in this category.'}
              </div>
            </div>
          ) : (
            filteredFindings.map((finding) => {
              const isSelected = selectedFinding?.id === finding.id;
              const rtype = getResultType(finding);
              const rBadge = getResultTypeBadge(rtype);

              const isFindingSimulated = isMockTarget || finding.title.includes('[SIMULATED]') || finding.impact === 'Simulated synthetic result for testing. Zero live network impact.';

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
                  <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
                    <span className={`text-[10px] font-mono font-bold flex items-center gap-1 px-2 py-0.5 rounded border ${rBadge.style}`}>
                      {rBadge.icon}
                      <span>{rBadge.label}</span>
                    </span>
                    <div className="flex items-center gap-1.5">
                      {isFindingSimulated && (
                        <span className="text-[9px] uppercase font-mono font-bold px-1.5 py-0.5 rounded border bg-amber-500/20 text-amber-300 border-amber-500/40">
                          SIMULATED
                        </span>
                      )}
                      <span className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded border ${getSeverityBadge(finding.severity)}`}>
                        {finding.severity}
                      </span>
                    </div>
                  </div>
                  <h3 className="text-xs font-semibold text-zinc-100 leading-snug">{finding.title}</h3>
                  <p className="text-[11px] font-mono text-zinc-400 mt-1 truncate">{finding.affected_asset}</p>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Selected Inspector */}
        <div className="lg:col-span-7">
          {selectedFinding ? (
            <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/60 space-y-5 text-xs">
              {/* Finding Title & Result Type Header */}
              <div className="border-b border-zinc-800 pb-3">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  {(() => {
                    const rtype = getResultType(selectedFinding);
                    const rBadge = getResultTypeBadge(rtype);
                    return (
                      <span className={`text-[10px] font-mono font-bold flex items-center gap-1 px-2.5 py-0.5 rounded border ${rBadge.style}`}>
                        {rBadge.icon}
                        <span>{rBadge.label}</span>
                      </span>
                    );
                  })()}
                  {(isMockTarget || selectedFinding.title.includes('[SIMULATED]')) && (
                    <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded border bg-amber-500/20 text-amber-300 border-amber-500/40">
                      SIMULATED RESULT (ZERO NETWORK EGRESS)
                    </span>
                  )}
                  <span className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded border ${getSeverityBadge(selectedFinding.severity)}`}>
                    Severity: {selectedFinding.severity}
                  </span>
                  <span className="text-[10px] font-mono text-zinc-400">Confidence: {selectedFinding.confidence}</span>
                  <span className="text-[10px] font-mono text-zinc-400">Status: {selectedFinding.status}</span>
                </div>
                <h2 className="text-base font-bold text-zinc-100">{selectedFinding.title}</h2>
                <div className="text-[11px] font-mono text-cyan-400 mt-1">{selectedFinding.affected_asset}</div>
              </div>

              {/* Reproduction Steps */}
              {selectedFinding.reproduction_steps && (
                <div>
                  <h4 className="font-semibold text-zinc-300 text-xs mb-1">Reproduction & Verification Steps:</h4>
                  <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 font-mono text-[11px] text-zinc-300 whitespace-pre-wrap leading-relaxed">
                    {selectedFinding.reproduction_steps}
                  </div>
                </div>
              )}

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
              {selectedFinding.evidence && selectedFinding.evidence.length > 0 && (
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
              )}
            </div>
          ) : (
            <div className="p-8 rounded-xl border border-zinc-800 text-center text-zinc-500 text-xs">
              Select an item from the list to view reproduction details and evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
