'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import { FileCheck2, AlertCircle, CheckCircle2, Clock, XCircle, ShieldAlert } from 'lucide-react';

interface CatalogItem {
  id: string;
  name: string;
  category: string;
  status: 'implemented' | 'prerequisites_missing' | 'not_implemented';
  risk: 'low' | 'medium' | 'high';
  tools: string[];
  verification: string;
  evidence: string;
  limitations: string;
}

const CATALOG_DATA: CatalogItem[] = [
  {
    id: "mod-sec-headers",
    name: "Security Headers & Cookie Flags Audit",
    category: "Web & API Security",
    status: "implemented",
    risk: "low",
    tools: ["controlled_http"],
    verification: "Header parsing and cookie attribute verification against HSTS, CSP, and SameSite standards.",
    evidence: "Raw HTTP request and response header snapshots with flagged missing security directives.",
    limitations: "Does not verify dynamic client-side JS DOM security policies."
  },
  {
    id: "mod-path-traversal",
    name: "Workspace Boundary & Path Traversal Guard",
    category: "Web & API Security",
    status: "implemented",
    risk: "low",
    tools: ["source_inspector"],
    verification: "Static inspection of file access paths to ensure strict containment within canonical workspace.",
    evidence: "Identified file resolution calls omitting canonical path verification.",
    limitations: "Static analysis only; does not simulate OS-level symlink race conditions."
  },
  {
    id: "mod-secret-scan",
    name: "Repository Secret & Credential Scanning",
    category: "Web & API Security",
    status: "implemented",
    risk: "low",
    tools: ["gitleaks", "source_inspector"],
    verification: "Pattern matching and Shannon entropy scans for API tokens, passwords, and private keys.",
    evidence: "Redacted credential tokens with matched regex pattern and source file reference.",
    limitations: "May flag high-entropy mock fixtures unless exclusions are configured."
  },
  {
    id: "mod-ast-sast",
    name: "Python AST Dangerous Builtins Analysis",
    category: "Web & API Security",
    status: "implemented",
    risk: "low",
    tools: ["ast_parser"],
    verification: "Offline AST traversal checking for eval(), exec(), and subprocess(shell=True).",
    evidence: "AST Node line number and source snippet demonstrating unsafe usage.",
    limitations: "Limited to Python source code; does not trace inter-module taint flow."
  },
  {
    id: "mod-xss-reflection",
    name: "Cross-Site Scripting (XSS) Reflection & Context Check",
    category: "Web & API Security",
    status: "prerequisites_missing",
    risk: "medium",
    tools: ["playwright_browser", "controlled_http"],
    verification: "Headless browser DOM execution proof (never reflection alone).",
    evidence: "Browser DOM execution trace or simulated alert dialog dispatch proof.",
    limitations: "Requires headless browser worker setup; disabled on static targets."
  },
  {
    id: "mod-idor-bola",
    name: "Broken Object Level Authorization (IDOR/BOLA)",
    category: "Web & API Security",
    status: "prerequisites_missing",
    risk: "medium",
    tools: ["controlled_http"],
    verification: "Differential comparison of resource access between user A and user B tokens.",
    evidence: "HTTP 200 response with private resource data returned to unauthorized account.",
    limitations: "Requires minimum two distinct test credentials configured in target."
  },
  {
    id: "mod-csrf-state",
    name: "Cross-Site Request Forgery State Change Validation",
    category: "Web & API Security",
    status: "prerequisites_missing",
    risk: "high",
    tools: ["controlled_http", "playwright_browser"],
    verification: "Execution of simulated cross-origin request and verification of persistent state change.",
    evidence: "Confirmed database or state alteration without valid anti-CSRF token.",
    limitations: "Requires stateful mutating endpoint and confirmed rollback mechanism."
  },
  {
    id: "mod-ssrf-validation",
    name: "Server-Side Request Forgery (SSRF) Boundary Check",
    category: "Web & API Security",
    status: "not_implemented",
    risk: "high",
    tools: ["controlled_http", "dns_resolver"],
    verification: "Triggering webhooks pointing to controlled listeners with DNS resolution verification.",
    evidence: "External DNS or HTTP callback received from server egress.",
    limitations: "Not implemented in current release. Planned for v0.2."
  }
];

export default function PlansView() {
  const [selectedItem, setSelectedItem] = useState<CatalogItem>(CATALOG_DATA[0]);

  const getStatusBadge = (status: CatalogItem['status']) => {
    switch (status) {
      case 'implemented':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      case 'prerequisites_missing':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'not_implemented':
        return 'bg-zinc-800 text-zinc-500 border-zinc-700';
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-b border-zinc-800 pb-3">
        <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
          <FileCheck2 className="w-5 h-5 text-cyan-400" />
          <span>Test Coverage Catalog & Assessment Plans</span>
        </h2>
        <p className="text-xs text-zinc-400 mt-0.5">
          Explicit status declaration: Tests are never claimed as implemented unless fully verified by code and fixtures.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Module List */}
        <div className="lg:col-span-5 space-y-2.5">
          {CATALOG_DATA.map((item) => {
            const isSelected = selectedItem.id === item.id;
            return (
              <div
                key={item.id}
                onClick={() => setSelectedItem(item)}
                className={`p-3.5 rounded-xl border transition cursor-pointer ${
                  isSelected ? 'border-cyan-500 bg-zinc-900 shadow-md' : 'border-zinc-800 bg-zinc-900/40 hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${getStatusBadge(item.status)}`}>
                    {item.status.replace('_', ' ')}
                  </span>
                  <span className="text-[10px] font-mono text-zinc-500">{item.risk.toUpperCase()} RISK</span>
                </div>
                <h4 className="text-xs font-semibold text-zinc-100">{item.name}</h4>
                <div className="text-[11px] font-mono text-zinc-500 mt-1">Tools: {item.tools.join(', ')}</div>
              </div>
            );
          })}
        </div>

        {/* Selected Module Detail */}
        <div className="lg:col-span-7">
          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/60 space-y-4 text-xs">
            <div className="border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${getStatusBadge(selectedItem.status)}`}>
                  Status: {selectedItem.status.replace('_', ' ')}
                </span>
                <span className="text-[10px] font-mono text-zinc-400">Risk: {selectedItem.risk}</span>
              </div>
              <h3 className="text-base font-bold text-zinc-100">{selectedItem.name}</h3>
              <p className="text-[11px] text-zinc-400 mt-1">{selectedItem.category}</p>
            </div>

            <div>
              <span className="text-zinc-400 font-semibold block mb-1">Verification Method:</span>
              <p className="text-zinc-300 leading-relaxed bg-zinc-950 p-2.5 rounded border border-zinc-800 font-mono text-[11px]">
                {selectedItem.verification}
              </p>
            </div>

            <div>
              <span className="text-zinc-400 font-semibold block mb-1">Expected Evidence:</span>
              <p className="text-zinc-300 leading-relaxed bg-zinc-950 p-2.5 rounded border border-zinc-800 font-mono text-[11px]">
                {selectedItem.evidence}
              </p>
            </div>

            <div>
              <span className="text-amber-400 font-semibold block mb-1">Known Limitations:</span>
              <p className="text-amber-300/80 leading-relaxed bg-amber-950/20 p-2.5 rounded border border-amber-900/30 text-[11px]">
                {selectedItem.limitations}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
