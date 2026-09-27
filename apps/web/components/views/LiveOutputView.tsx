'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useStudio } from '../../lib/context';
import {
  Terminal,
  Search,
  Trash2,
  ArrowDownCircle,
  ShieldCheck,
  Cpu
} from 'lucide-react';

export default function LiveOutputView() {
  const { logs, t } = useStudio();
  const [filter, setFilter] = useState('');
  const [autoscroll, setAutoscroll] = useState(true);
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

        <div className="flex items-center gap-2">
          {/* Search Filter */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="text"
              placeholder={t.live.filter}
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-md pl-8 pr-3 py-1 text-xs text-zinc-200 focus:outline-none focus:border-cyan-500 w-44"
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
        </div>
      </div>

      {/* Terminal Screen (Sanitized Viewer) */}
      <div className="flex-1 rounded-xl border border-zinc-800 bg-zinc-950 p-4 font-mono text-xs overflow-y-auto space-y-1 shadow-inner select-text">
        <div className="text-[11px] text-zinc-400 pb-2 border-b border-zinc-900 mb-2 flex items-center justify-between">
          <span>Tawassl Studio Isolated Sandbox Terminal • Standard Output Redactor [ACTIVE]</span>
          <span className="flex items-center gap-1 text-emerald-400 text-[10px]">
            <ShieldCheck className="w-3 h-3" /> Credentials Redacted
          </span>
        </div>

        {filteredLogs.map((log) => (
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
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
