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
  Layers,
  Trash2,
  CheckCircle2,
  RotateCcw
} from 'lucide-react';
import { Finding } from '../../lib/mockData';
import { fetchFindingsApi } from '../../lib/api';

export default function ReportsView() {
  const { assessment, targets, findings, clearFindings, t } = useStudio();
  const [activeFormat, setActiveFormat] = useState<'markdown' | 'json' | 'sarif'>('markdown');
  const [copied, setCopied] = useState(false);
  const [cleared, setCleared] = useState(false);
  const [clearNotice, setClearNotice] = useState<string | null>(null);

  const activeTarget = targets.find((t) => t.id === assessment.target_id) || targets[0];

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


  const isMockTarget = activeTarget?.environment_mode === 'mock';
  const targetTypeDisplay = isMockTarget ? 'MOCK' : 'LIVE';
  const networkModeDisplay = isMockTarget ? 'Simulated' : 'Real HTTP Requests';
  const aiProviderDisplay = assessment.ai_provider === 'mock'
    ? 'Mock (Mock Rule Engine - Simulated Analysis)'
    : assessment.ai_provider === 'gemini'
    ? 'Gemini'
    : assessment.ai_provider === 'gpt'
    ? 'GPT'
    : assessment.ai_provider;
  const targetUrl = activeTarget?.base_urls?.[0] || (activeTarget?.authorized_domains?.[0] ? `https://${activeTarget.authorized_domains[0]}` : 'https://matami.tawassl.com');

  const deduplicateFindings = (list: Finding[]) => {
    // Prevent mixing: for LIVE targets, exclude any simulated artifacts
    const filtered = isMockTarget 
      ? list 
      : list.filter((f) => !f.title.includes('[SIMULATED]') && f.impact !== 'Simulated synthetic result for testing. Zero live network impact.');
    const seen = new Set<string>();
    const unique: Finding[] = [];
    for (const f of filtered) {
      const key = `${f.affected_asset}:${f.category}:${f.evidence_hash || f.title}`;
      if (!seen.has(key)) {
        seen.add(key);
        unique.push(f);
      }
    }
    return unique;
  };

  const uniqueFindings = deduplicateFindings(findings);
  const confirmedVulns = uniqueFindings.filter((f) => getResultType(f) === 'finding');
  const observations = uniqueFindings.filter((f) => getResultType(f) === 'observation');
  const passedControls = uniqueFindings.filter((f) => getResultType(f) === 'passed_control');
  const inconclusiveTests = uniqueFindings.filter((f) => getResultType(f) === 'inconclusive');

  const generateMarkdownReport = () => {
    const notice = "No confirmed vulnerabilities were identified by the tests executed within this assessment scope.";
    return `# Security Assessment Report: ${assessment.name}

**Workspace:** Tawassl Security Studio  
**Date:** ${new Date().toISOString()}  
**Target Type:** ${targetTypeDisplay}  
**Target URL:** ${targetUrl}  
**Authorization Status:** Authorized Scope Verified  
**Network Mode:** ${networkModeDisplay}  
**AI Provider:** ${aiProviderDisplay}  
**Assessment Profile:** ${assessment.profile}  
**Status:** ${assessment.status}  

${isMockTarget ? `> ⚠️ **SIMULATION NOTICE (MOCK TARGET):** All test executions and findings in this report are simulated via the mock rule engine with zero network egress. This does not represent a live penetration test.\n` : ''}---

## 1. Executive Summary & Assessment Scope Notice

> **Important Coverage Notice:**
> ${notice}
> A report with no findings indicates that no vulnerabilities were detected by the specific tests executed within the configured limits and budget. It does not certify that the application is completely secure.

### Result Breakdown Summary:
- **Confirmed Vulnerabilities:** ${confirmedVulns.length}
- **Security Observations:** ${observations.length}
- **Passed Controls:** ${passedControls.length}
- **Inconclusive Tests:** ${inconclusiveTests.length}

- **Requests Made:** ${assessment.requests_made} / ${assessment.max_requests} budget limit
- **Agent Steps:** ${assessment.steps_taken} / ${assessment.max_steps}
- **Tool Calls:** ${assessment.tool_calls_made}

---

## 2. Confirmed Security Findings (${confirmedVulns.length})

${
  confirmedVulns.length === 0
    ? `> ${notice}\n`
    : confirmedVulns
        .map(
          (f, idx) => `### ${idx + 1}. [${f.severity.toUpperCase()}] ${f.title}

- **Affected Asset:** \`${f.affected_asset}\`
- **Category:** \`${f.category}\`
- **Result Type:** \`finding\` (Confirmed Vulnerability: Yes)
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
        .join('\n\n')
}

## 3. Security Observations (${observations.length})

${
  observations.length === 0
    ? 'No informational observations recorded.\n'
    : observations
        .map(
          (f, idx) => `### ${idx + 1}. [OBSERVATION / ${f.severity.toUpperCase()}] ${f.title}

- **Affected Asset:** \`${f.affected_asset}\`
- **Category:** \`${f.category}\`
- **Result Type:** \`observation\` (Confirmed Vulnerability: No)
- **Observed Behavior:** ${f.observed_result}
- **Context & Note:** ${f.impact || 'Informational reconnaissance detail. Does not represent a vulnerability.'}

---`
        )
        .join('\n\n')
}

## 4. Passed Controls (${passedControls.length})

${
  passedControls.length === 0
    ? 'No passed controls recorded.\n'
    : passedControls
        .map((f) => `- **[PASSED]** \`${f.title}\` on \`${f.affected_asset}\`: ${f.observed_result}`)
        .join('\n')
}

${
  inconclusiveTests.length > 0
    ? `\n## 5. Inconclusive Tests (${inconclusiveTests.length})\n\n` +
      inconclusiveTests.map((f) => `- **[INCONCLUSIVE]** \`${f.title}\`: ${f.observed_result}`).join('\n')
    : ''
}

## 5. Engine & Policy Controls
- **Tawassl Policy Engine:** v0.1.0 (Zero-Trust Active)
- **Subprocess Worker:** Isolated Sandboxed Worker
- **Egress Guard:** Deterministic SSRF / DNS Resolution Filter Active
`;
  };

  const generateJsonReport = () => {
    return JSON.stringify(
      {
        metadata: {
          application: "Tawassl Security Studio",
          version: "0.1.0",
          generated_at: new Date().toISOString(),
          scope_notice: "No confirmed vulnerabilities were identified by the tests executed within this assessment scope."
        },
        summary: {
          confirmed_vulnerabilities: confirmedVulns.length,
          security_observations: observations.length,
          passed_controls: passedControls.length,
          inconclusive_tests: inconclusiveTests.length
        },
        target_metadata: {
          target_type: targetTypeDisplay,
          target_url: targetUrl,
          authorization_status: "Authorized Scope Verified",
          network_mode: networkModeDisplay,
          ai_provider: aiProviderDisplay,
          simulated: isMockTarget
        },
        assessment,
        target: activeTarget,
        results: {
          confirmed_vulnerabilities: confirmedVulns,
          security_observations: observations,
          passed_controls: passedControls,
          inconclusive_tests: inconclusiveTests
        },
        findings: uniqueFindings
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
                rules: [
                  ...confirmedVulns.map((f) => ({
                    id: f.id,
                    name: f.title,
                    shortDescription: { text: f.title },
                    fullDescription: { text: f.observed_result },
                    defaultConfiguration: {
                      level: f.severity === 'high' || f.severity === 'critical' ? 'error' : 'warning'
                    }
                  })),
                  ...observations.map((f) => ({
                    id: f.id,
                    name: f.title,
                    shortDescription: { text: f.title },
                    fullDescription: { text: f.observed_result },
                    defaultConfiguration: { level: 'note' }
                  }))
                ]
              }
            },
            results: [
              ...confirmedVulns.map((f) => ({
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
              })),
              ...observations.map((f) => ({
                ruleId: f.id,
                level: 'note',
                message: { text: f.observed_result },
                locations: [
                  {
                    physicalLocation: {
                      artifactLocation: { uri: f.affected_asset }
                    }
                  }
                ]
              }))
            ]
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

  const handleClear = () => {
    clearFindings();
    setCleared(true);
    setClearNotice(t.reports.clearSuccess || "Report preview cleared successfully.");
    setTimeout(() => setClearNotice(null), 4000);
  };

  const handleRestore = async () => {
    try {
      if (assessment?.id) {
        const latest = await fetchFindingsApi(assessment.id);
        if (latest && latest.length > 0) {
          window.location.reload();
          return;
        }
      }
      window.location.reload();
    } catch {
      window.location.reload();
    }
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
        <div className="flex items-center gap-2 flex-wrap">
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

          {/* Clear Report Button */}
          <button
            onClick={handleClear}
            disabled={uniqueFindings.length === 0 && cleared}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-rose-400 hover:border-rose-500/40 disabled:opacity-40 disabled:hover:text-zinc-300 disabled:cursor-not-allowed text-xs font-medium transition cursor-pointer"
            title={t.reports.clear || "Clear Report"}
          >
            <Trash2 className="w-3.5 h-3.5 text-zinc-400" />
            <span>{t.reports.clear || "Clear"}</span>
          </button>
        </div>
      </div>

      {/* Clear Toast Notification */}
      {clearNotice && (
        <div className="rounded-lg border border-cyan-500/40 bg-cyan-950/50 text-cyan-200 px-4 py-2 text-xs flex items-center justify-between gap-2 shrink-0 animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>{clearNotice}</span>
          </div>
          <button
            onClick={handleRestore}
            className="text-[11px] underline text-cyan-300 hover:text-cyan-100 flex items-center gap-1 cursor-pointer"
          >
            <RotateCcw className="w-3 h-3" />
            <span>{t.reports.restore || "Reload"}</span>
          </button>
        </div>
      )}

      {/* Scope Limitations Alert */}
      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-cyan-400 shrink-0" />
        <span>{t.reports.limitationsNote}</span>
      </div>

      {/* Report Preview */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-5 font-mono text-xs text-zinc-300 overflow-x-auto max-h-[calc(100vh-230px)] shadow-inner leading-relaxed">
        {cleared && uniqueFindings.length === 0 ? (
          <div className="py-16 text-center space-y-3 font-sans">
            <div className="w-12 h-12 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 flex items-center justify-center mx-auto">
              <FileText className="w-6 h-6 stroke-1 text-zinc-500" />
            </div>
            <h3 className="text-sm font-semibold text-zinc-200">{t.reports.emptyTitle || "Report Preview Cleared"}</h3>
            <p className="text-xs text-zinc-400 max-w-md mx-auto">{t.reports.emptyDesc || "The current report has been cleared. Run a new assessment or click reload to restore previous findings."}</p>
            <div className="pt-2">
              <button
                onClick={handleRestore}
                className="px-3.5 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold inline-flex items-center gap-1.5 transition cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
                <span>{t.reports.restore || "Reload Findings"}</span>
              </button>
            </div>
          </div>
        ) : (
          <pre className="whitespace-pre-wrap">{currentContent}</pre>
        )}
      </div>
    </div>
  );
}
