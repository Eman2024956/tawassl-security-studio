'use client';

import React from 'react';
import { useStudio } from '../../lib/context';
import {
  ListOrdered,
  CheckCircle2,
  XCircle,
  Square,
  ShieldAlert,
  Hash,
  Clock,
  Terminal,
  AlertTriangle
} from 'lucide-react';

export default function CommandQueueView() {
  const { proposals, approveProposal, rejectProposal, stopAssessment, t } = useStudio();

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <ListOrdered className="w-5 h-5 text-amber-400" />
            <span>{t.queue.title}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-1">{t.queue.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={stopAssessment}
            className="px-3 py-1.5 rounded bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/40 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            <span>{t.queue.stopAll}</span>
          </button>
        </div>
      </div>

      {/* Proposals List */}
      <div className="space-y-4">
        {proposals.length === 0 ? (
          <div className="p-8 rounded-xl border border-zinc-800 bg-zinc-900/30 text-center text-zinc-400 text-xs">
            No command proposals currently queued.
          </div>
        ) : (
          proposals.map((prop) => {
            const isPending = prop.status === 'pending';
            return (
              <div
                key={prop.id}
                className={`p-5 rounded-xl border transition ${
                  isPending
                    ? 'border-amber-500/40 bg-zinc-900/80 shadow-lg shadow-amber-950/20'
                    : prop.status === 'approved'
                    ? 'border-emerald-500/30 bg-zinc-900/40 opacity-75'
                    : 'border-zinc-800 bg-zinc-900/20 opacity-60'
                }`}
              >
                {/* Proposal Top Bar */}
                <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-zinc-800">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-800/40">
                      {prop.tool_name}
                    </span>
                    <span className="text-[11px] font-mono text-zinc-400">ID: {prop.id}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded ${
                        isPending
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                          : prop.status === 'approved'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                          : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                      }`}
                    >
                      {prop.status}
                    </span>
                  </div>
                </div>

                {/* Purpose & Side Effects */}
                <div className="my-3 space-y-2 text-xs">
                  <div>
                    <span className="text-zinc-400 font-semibold block text-[11px]">{t.queue.purpose}:</span>
                    <p className="text-zinc-200 mt-0.5">{prop.purpose}</p>
                  </div>
                  <div>
                    <span className="text-zinc-400 font-semibold block text-[11px]">{t.queue.sideEffects}:</span>
                    <p className="text-amber-300/90 mt-0.5 font-mono text-[11px]">{prop.side_effects}</p>
                  </div>
                </div>

                {/* Arguments Preview */}
                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 font-mono text-xs text-zinc-300 overflow-x-auto">
                  <div className="text-[10px] text-zinc-400 uppercase font-sans font-bold mb-1">Validated Arguments</div>
                  <pre className="text-[11px] leading-relaxed">{JSON.stringify(prop.arguments, null, 2)}</pre>
                </div>

                {/* SHA-256 Hash & Resource Bounds */}
                <div className="mt-3 flex flex-wrap items-center justify-between text-[11px] text-zinc-400 gap-2">
                  <div className="flex items-center gap-1.5 font-mono text-[10px]">
                    <Hash className="w-3 h-3 text-cyan-400" />
                    <span>SHA-256: {prop.arguments_hash.substring(0, 16)}...</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-[10px] text-zinc-400">
                    <span>Timeout: {prop.resource_limits.timeout_sec}s</span> •{' '}
                    <span>Output Max: {prop.resource_limits.max_output_kb}KB</span> •{' '}
                    <span>Net Isolation: {prop.resource_limits.network_restricted ? 'ACTIVE' : 'NONE'}</span>
                  </div>
                </div>

                {/* Decision Actions for Pending */}
                {isPending && (
                  <div className="mt-4 pt-3 border-t border-zinc-800 flex items-center justify-end gap-3">
                    <button
                      onClick={() => rejectProposal(prop.id)}
                      className="px-3.5 py-1.5 rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
                    >
                      <XCircle className="w-4 h-4 text-rose-400" />
                      <span>{t.queue.reject}</span>
                    </button>
                    <button
                      onClick={() => approveProposal(prop.id)}
                      className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-md flex items-center gap-1.5 transition cursor-pointer"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{t.queue.approveOnce}</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
