'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import {
  FileText,
  Download,
  Copy,
  Check,
  AlertCircle,
  FileCode,
  Layers
} from 'lucide-react';

export default function ReportsView() {
  const { assessment, targets, findings, t } = useStudio();
  const [activeFormat, setActiveFormat] = useState<'markdown' | 'json' | 'sarif'>('markdown');
  const [copied, setCopied] = useState(false);

  const activeTarget = targets.find((t) => t.id === assessment.target_id) || targets[0];

  const generateMarkdownReport = () => {
    return `# Security Assessment Report: ${assessment.name}

**Workspace:** Tawassl Security Studio  
**Date:** ${new Date().toISOString()}  
**Target:** ${activeTarget?.name} (${activeTarget?.target_type})  
**Authorized Scope:** ${activeTarget?.authorized_domains?.join(', ')}  
**Assessment Profile:** ${assessment.profile}  
**AI Provider:** ${assessment.ai_provider} (${assessment.model_id})  
**Status:** ${assessment.status}  

---

## 1. Executive Summary & Scope Limitations

> **Critical Notice:** "No findings" means no vulnerabilities were detected by the specific tests executed within authorized limits. It does not certify that the application is completely secure.

- **Requests Executed:** ${assessment.requests_made} / ${assessment.max_requests} budget limit
- **Agent Steps:** ${assessment.steps_taken} / ${assessment.max_steps}
- **Tool Calls:** ${assessment.tool_calls_made}

---

## 2. Discovered Findings & Verified Evidence

${findings
  .map(
    (f, idx) => `### ${idx + 1}. [${f.severity.toUpperCase()}] ${f.title}

- **Affected Asset:** \`${f.affected_asset}\`
- **Category:** \`${f.category}\`
- **Status:** **${f.status}** (Confidence: ${f.confidence})
- **Observed Result:** ${f.observed_result}
- **Expected Result:** ${f.expected_result}

#### Reproduction Steps:
\`\`\`
${f.reproduction_steps}
\`\`\`

#### Suggested Remediation:
${f.remediation || 'Remediation pending review.'}

---`
  )
  .join('\n\n')}

## 3. Tool & Engine Versions
- **Tawassl Policy Engine:** v0.1.0-alpha
- **Subprocess Worker:** Isolated Sandboxed Worker
- **Egress Guard:** Deterministic SSRF / DNS Resolution Filter Active
`;
  };

  const generateJsonReport = () => {
    return JSON.stringify(
      {
        report_meta: {
          app: "Tawassl Security Studio",
          version: "0.1.0",
          generated_at: new Date().toISOString(),
          scope_notice: "No findings means no vulnerabilities detected by executed tests."
        },
        assessment,
        target: activeTarget,
        findings
      },
      null,
      2
    );
  };

  const generateSarifReport = () => {
    return JSON.stringify(
      {
        $schema: "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        version: "2.1.0",
        runs: [
          {
            tool: {
              driver: {
                name: "Tawassl Security Studio",
                version: "0.1.0",
                rules: findings.map((f) => ({
                  id: f.id,
                  name: f.title,
                  shortDescription: { text: f.title },
                  fullDescription: { text: f.observed_result },
                  defaultConfiguration: {
                    level: f.severity === 'high' || f.severity === 'critical' ? 'error' : 'warning'
                  }
                }))
              }
            },
            results: findings.map((f) => ({
              ruleId: f.id,
              level: f.severity === 'high' || f.severity === 'critical' ? 'error' : 'warning',
              message: { text: f.observed_result },
              locations: [
                {
                  physicalLocation: {
                    artifactLocation: { uri: f.affected_asset }
                  }
                }
              ]
            }))
          }
        ]
      },
      null,
      2
    );
  };

  const currentContent =
    activeFormat === 'markdown'
      ? generateMarkdownReport()
      : activeFormat === 'json'
      ? generateJsonReport()
      : generateSarifReport();

  const handleCopy = () => {
    navigator.clipboard.writeText(currentContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = activeFormat === 'markdown' ? 'md' : activeFormat === 'json' ? 'json' : 'sarif';
    const blob = new Blob([currentContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tawassl-security-report-${assessment.id}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <span>{t.reports.title}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">{t.reports.description}</p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Format Selector */}
          <div className="flex bg-zinc-900 border border-zinc-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setActiveFormat('markdown')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                activeFormat === 'markdown' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Markdown
            </button>
            <button
              onClick={() => setActiveFormat('json')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                activeFormat === 'json' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              JSON
            </button>
            <button
              onClick={() => setActiveFormat('sarif')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                activeFormat === 'sarif' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              SARIF 2.1.0
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 transition cursor-pointer"
            title="Copy Report"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-semibold text-white shadow-md transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* Scope Limitations Alert */}
      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-cyan-400 shrink-0" />
        <span>{t.reports.limitationsNote}</span>
      </div>

      {/* Report Preview */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-5 font-mono text-xs text-zinc-300 overflow-x-auto max-h-[calc(100vh-230px)] shadow-inner leading-relaxed">
        <pre className="whitespace-pre-wrap">{currentContent}</pre>
      </div>
    </div>
  );
}
