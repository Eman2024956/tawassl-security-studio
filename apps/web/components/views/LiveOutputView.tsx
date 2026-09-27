'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useStudio } from '../../lib/context';
import {
  Terminal,
  Search,
  Trash2,
  ArrowDownCircle,
  ShieldCheck,
  Download,
  CheckCircle2,
  FileText,
  AlertCircle
} from 'lucide-react';

export default function LiveOutputView() {
  const { logs, clearLogs, isRunningTest, assessment, targets, t } = useStudio();
  const [filter, setFilter] = useState('');
  const [autoscroll, setAutoscroll] = useState(true);
  const [exportNotice, setExportNotice] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoscroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoscroll]);

  const filteredLogs = logs.filter(
    (l) =>
      l.message.toLowerCase().includes(filter.toLowerCase()) ||
      l.source.toLowerCase().includes(filter.toLowerCase())
  );

  const handleExportLogs = () => {
    if (logs.length === 0) return;

    const targetName = targets[0]?.authorized_domains?.[0] || 'matami.tawassl.com';
    const timestampStr = new Date().toISOString();
    
    let content = '================================================================================\n';
    content += 'TAWASSL SECURITY STUDIO - AUDIT EXECUTION HISTORY LOG\n';
    content += `Target Scope: ${targetName}\n`;
    content += `Assessment: ${assessment?.name || 'Live Audit'}\n`;
    content += `Status: ${assessment?.status || 'completed'}\n`;
    content += `Export Timestamp: ${timestampStr}\n`;
    content += `Total Entries: ${logs.length}\n`;
    content += '================================================================================\n\n';

    logs.forEach((log) => {
      content += `[${log.timestamp}] [${log.level.toUpperCase().padEnd(7)}] [${log.source.padEnd(16)}] ${log.message}\n`;
    });

    content += '\n================================================================================\n';
    content += 'END OF AUDIT LOG - ZERO-TRUST ISOLATION ACTIVE\n';
    content += '================================================================================\n';

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const safeDate = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    link.href = url;
    link.download = `tawassl-audit-history-${safeDate}.log`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setExportNotice(t.live.exportSuccess);
    setTimeout(() => setExportNotice(null), 4000);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-rose-400 bg-rose-950/40 border-rose-800/40';
      case 'warn':
        return 'text-amber-400 bg-amber-950/40 border-amber-800/40';
      case 'agent':
        return 'text-cyan-400 bg-cyan-950/40 border-cyan-800/40';
      case 'success':
        return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';
      default:
        return 'text-zinc-400 bg-zinc-900 border-zinc-800';
    }
  };

  return (
    <div className="space-y-4 flex flex-col h-[calc(100vh-140px)]">
      {/* View Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-3 shrink-0">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-cyan-400" />
            <span>{t.live.title}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">{t.live.description}</p>
        </div>

        <div className="flex items-center flex-wrap gap-2">
          {/* Search Filter */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="text"
              placeholder={t.live.filter}
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-md pl-8 pr-3 py-1 text-xs text-zinc-200 focus:outline-none focus:border-cyan-500 w-36 sm:w-44"
            />
          </div>

          {/* Autoscroll Toggle */}
          <button
            onClick={() => setAutoscroll(!autoscroll)}
            className={`px-2.5 py-1 rounded text-xs font-medium border flex items-center gap-1 transition cursor-pointer ${
              autoscroll
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-zinc-200'
            }`}
          >
            <ArrowDownCircle className="w-3.5 h-3.5" />
            <span>{t.live.autoscroll}</span>
          </button>

          {/* Clear Button */}
          <button
            onClick={clearLogs}
            disabled={logs.length === 0}
            className="px-2.5 py-1 rounded text-xs font-medium border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-rose-400 hover:border-rose-500/40 disabled:opacity-40 disabled:hover:text-zinc-300 disabled:cursor-not-allowed flex items-center gap-1 transition cursor-pointer"
            title={t.live.clear}
          >
            <Trash2 className="w-3.5 h-3.5 text-zinc-400" />
            <span>{t.live.clear}</span>
          </button>

          {/* Export History Log Button */}
          <button
            onClick={handleExportLogs}
            disabled={logs.length === 0}
            className="px-3 py-1 rounded text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-40 disabled:hover:bg-cyan-600 disabled:cursor-not-allowed flex items-center gap-1.5 shadow-sm transition cursor-pointer"
            title={t.live.exportLog}
          >
            <Download className="w-3.5 h-3.5" />
            <span>{t.live.exportLog}</span>
          </button>
        </div>
      </div>

      {/* Completion & Export Banner */}
      {!isRunningTest && logs.length > 0 && assessment?.status === 'completed' && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/30 px-4 py-2.5 flex items-center justify-between gap-3 text-xs shrink-0 animate-in fade-in duration-300">
          <div className="flex items-center gap-2 text-emerald-300">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{t.live.auditCompletedNotice}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleExportLogs}
              className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center gap-1 transition shadow cursor-pointer text-[11px]"
            >
              <Download className="w-3 h-3" />
              <span>{t.live.exportLog}</span>
            </button>
          </div>
        </div>
      )}

      {/* Export Toast Notification */}
      {exportNotice && (
        <div className="rounded-lg border border-cyan-500/40 bg-cyan-950/50 text-cyan-200 px-4 py-2 text-xs flex items-center gap-2 shrink-0 animate-in fade-in duration-200">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{exportNotice}</span>
        </div>
      )}

      {/* Terminal Screen (Sanitized Viewer) */}
      <div className="flex-1 rounded-xl border border-zinc-800 bg-zinc-950 p-4 font-mono text-xs overflow-y-auto space-y-1 shadow-inner select-text">
        <div className="text-[11px] text-zinc-400 pb-2 border-b border-zinc-900 mb-2 flex items-center justify-between">
          <span>Tawassl Studio Isolated Sandbox Terminal • Standard Output Redactor [ACTIVE]</span>
          <span className="flex items-center gap-1 text-emerald-400 text-[10px]">
            <ShieldCheck className="w-3 h-3" /> Credentials Redacted
          </span>
        </div>

        {filteredLogs.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center text-zinc-500 gap-2">
            <Terminal className="w-6 h-6 stroke-1" />
            <p>No log events to display.</p>
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div key={log.id} className="flex items-start gap-2.5 leading-relaxed hover:bg-zinc-900/50 py-0.5 px-1 rounded">
              <span className="text-zinc-400 text-[11px] shrink-0 select-none">[{log.timestamp}]</span>
              <span className={`text-[10px] uppercase font-bold px-1.5 py-0.2 rounded border shrink-0 ${getLevelColor(log.level)}`}>
                {log.source}
              </span>
              <span
                className={`break-all ${
                  log.level === 'error'
                    ? 'text-rose-300'
                    : log.level === 'warn'
                    ? 'text-amber-300'
                    : log.level === 'agent'
                    ? 'text-cyan-300'
                    : log.level === 'success'
                    ? 'text-emerald-300'
                    : 'text-zinc-300'
                }`}
              >
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
