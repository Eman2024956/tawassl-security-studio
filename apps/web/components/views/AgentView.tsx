'use client';

import React from 'react';
import { useStudio } from '../../lib/context';
import { Bot, Cpu, CheckCircle2, ArrowRight, ShieldCheck, Clock, Layers } from 'lucide-react';

export default function AgentView() {
  const { assessment, t } = useStudio();

  const STEPS_TIMELINE = [
    {
      step: 1,
      title: "Target Scope Validation",
      status: "completed",
      rationale: "Ensured base URL 'https://matami.tawassl.com' resolves to an authorized domain with zero-trust egress check.",
      tool: "policy_engine"
    },
    {
      step: 2,
      title: "Source AST Parsing",
      status: "completed",
      rationale: "Ran offline AST inspector on auth token logic to verify absence of dangerous builtins (eval, exec).",
      tool: "ast_syntax_inspector"
    },
    {
      step: 3,
      title: "TLS & HTTP Security Inspection",
      status: "completed",
      rationale: "Sent bounded GET request to /login. Identified missing HSTS header and insecure cookie flags.",
      tool: "controlled_http_inspect"
    },
    {
      step: 4,
      title: "Header Redirection Follow-up Proposal",
      status: "awaiting_approval",
      rationale: "Proposing controlled inspection of redirect target location to verify no external cross-origin escapes.",
      tool: "controlled_http_inspect"
    }
  ];

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyan-400" />
            <span>AI Agent Orchestration Console</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Step-by-step reasoning and typed tool proposals. The model plans and interprets; human-in-the-loop approves side effects.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-zinc-300 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg">
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span>Provider: {assessment.ai_provider}</span>
          <span className="text-zinc-500">|</span>
          <span className="text-cyan-400">Step {assessment.steps_taken} of {assessment.max_steps}</span>
        </div>
      </div>

      {/* Execution Timeline */}
      <div className="space-y-3">
        {STEPS_TIMELINE.map((item) => (
          <div
            key={item.step}
            className={`p-4 rounded-xl border transition ${
              item.status === 'awaiting_approval'
                ? 'border-amber-500/40 bg-zinc-900/80 shadow-md shadow-amber-950/20'
                : 'border-zinc-800 bg-zinc-900/30'
            }`}
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono font-bold text-zinc-400 bg-zinc-800 px-2 py-0.5 rounded">
                  STEP {item.step}
                </span>
                <span className="font-bold text-xs text-zinc-100">{item.title}</span>
              </div>
              <span
                className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded ${
                  item.status === 'completed'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {item.status.replace('_', ' ')}
              </span>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">{item.rationale}</p>

            <div className="mt-2.5 pt-2 border-t border-zinc-800/80 flex items-center justify-between text-[11px] font-mono text-zinc-500">
              <span>Tool: <strong className="text-cyan-400 font-semibold">{item.tool}</strong></span>
              <span>Isolated Worker Bound</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
