'use client';

import React from 'react';
import { useStudio } from '../../lib/context';
import { Crosshair, ShieldCheck, Globe, Code, Plus, AlertTriangle } from 'lucide-react';

export default function TargetsView() {
  const { targets, setIsWizardOpen } = useStudio();

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <Crosshair className="w-5 h-5 text-emerald-400" />
            <span>Targets & Authorized Scope</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Zero-Trust Scope: Only traffic to explicitly authorized hostnames and ports will be permitted.
          </p>
        </div>
        <button
          onClick={() => setIsWizardOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Onboard New Target</span>
        </button>
      </div>

      <div className="space-y-4">
        {targets.map((tgt) => (
          <div key={tgt.id} className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-md bg-zinc-800 text-zinc-300">
                  {tgt.target_type === 'source' ? <Code className="w-4 h-4 text-cyan-400" /> : <Globe className="w-4 h-4 text-emerald-400" />}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-zinc-100">{tgt.name}</h3>
                  <div className="text-[11px] font-mono text-zinc-400">Type: {tgt.target_type}</div>
                </div>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/50 border border-emerald-800/40 px-2 py-0.5 rounded">
                Scope Active
              </span>
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
        ))}
      </div>
    </div>
  );
}
