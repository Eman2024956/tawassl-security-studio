'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import { Crosshair, ShieldCheck, Globe, Code, Plus, AlertTriangle, Layers, Server } from 'lucide-react';

export default function TargetsView() {
  const { targets, setIsWizardOpen, t } = useStudio();
  const [filterMode, setFilterMode] = useState<'all' | 'live' | 'mock'>('all');

  const filteredTargets = targets.filter((tgt) => {
    const mode = tgt.environment_mode ?? 'live';
    if (filterMode === 'live') return mode === 'live';
    if (filterMode === 'mock') return mode === 'mock';
    return true;
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <Crosshair className="w-5 h-5 text-emerald-400" />
            <span>{t.nav.targets}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Zero-Trust Scope: Only traffic to explicitly authorized hostnames and ports will be permitted. MOCK targets execute in simulated mode.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Target Mode Filter */}
          <div className="flex bg-zinc-900 border border-zinc-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setFilterMode('all')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                filterMode === 'all' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              All ({targets.length})
            </button>
            <button
              onClick={() => setFilterMode('live')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                filterMode === 'live' ? 'bg-emerald-950/50 text-emerald-300 border border-emerald-800/40' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              LIVE ({targets.filter((t) => (t.environment_mode ?? 'live') === 'live').length})
            </button>
            <button
              onClick={() => setFilterMode('mock')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                filterMode === 'mock' ? 'bg-amber-950/50 text-amber-300 border border-amber-800/40' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              MOCK ({targets.filter((t) => t.environment_mode === 'mock').length})
            </button>
          </div>

          <button
            onClick={() => setIsWizardOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Onboard New Target</span>
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {filteredTargets.map((tgt) => {
          const isLive = (tgt.environment_mode ?? 'live') === 'live';
          const primaryUrl = tgt.base_urls?.[0] || (tgt.authorized_domains?.[0] ? `https://${tgt.authorized_domains[0]}` : 'N/A');

          return (
            <div
              key={tgt.id}
              className={`p-5 rounded-xl border space-y-4 ${
                isLive
                  ? 'border-zinc-800 bg-zinc-900/40'
                  : 'border-amber-900/30 bg-amber-950/10'
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-1.5 rounded-md bg-zinc-800 text-zinc-300">
                    {tgt.target_type === 'source' ? (
                      <Code className="w-4 h-4 text-cyan-400" />
                    ) : (
                      <Globe className={`w-4 h-4 ${isLive ? 'text-emerald-400' : 'text-amber-400'}`} />
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                      <span>{tgt.name}</span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase tracking-wider border ${
                          isLive
                            ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                            : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                        }`}
                      >
                        Target Type: {isLive ? 'LIVE' : 'MOCK'}
                      </span>
                    </h3>
                    <div className="text-[11px] font-mono text-zinc-400 mt-0.5">
                      Architecture: {tgt.target_type} • Primary URL: <span className="text-zinc-200">{primaryUrl}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                      isLive
                        ? 'text-cyan-400 bg-cyan-950/40 border-cyan-800/40'
                        : 'text-amber-400 bg-amber-950/40 border-amber-800/40'
                    }`}
                  >
                    Network Mode: {isLive ? 'Real HTTP Requests' : 'Simulated'}
                  </span>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                      isLive
                        ? 'text-emerald-400 bg-emerald-950/50 border-emerald-800/40'
                        : 'text-zinc-400 bg-zinc-900 border-zinc-800'
                    }`}
                  >
                    {isLive ? 'Authorized & Scope Verified' : 'Simulated Sandbox Scope'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                  <span className="text-zinc-400 block text-[11px] font-medium mb-1">Authorized Domains:</span>
                  <div className="font-mono text-zinc-200">
                    {tgt.authorized_domains.length > 0 ? tgt.authorized_domains.join(', ') : 'None (Offline Source Target)'}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                  <span className="text-zinc-400 block text-[11px] font-medium mb-1">Base URLs & Ports:</span>
                  <div className="font-mono text-zinc-200">
                    {tgt.base_urls.length > 0 ? `${tgt.base_urls.join(', ')} [Ports: ${tgt.allowed_ports.join(', ')}]` : 'N/A'}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                  <span className="text-zinc-400 block text-[11px] font-medium mb-1">Strict Exclusions:</span>
                  <div className="font-mono text-rose-400">
                    {tgt.exclusions.length > 0 ? tgt.exclusions.join(', ') : 'None'}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
