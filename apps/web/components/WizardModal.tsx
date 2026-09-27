'use client';

import React, { useState } from 'react';
import { useStudio } from '../lib/context';
import {
  X,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  Shield,
  AlertTriangle,
  Globe,
  Code,
  Key,
  Sliders,
  Play
} from 'lucide-react';

export default function WizardModal() {
  const { isWizardOpen, setIsWizardOpen, projects, addLog, t } = useStudio();
  const [step, setStep] = useState<number>(1);

  // Form State
  const [projectName, setProjectName] = useState('Payment Gateway Audit');
  const [targetType, setTargetType] = useState<'website' | 'api' | 'source' | 'combined'>('website');
  const [authorizedDomains, setAuthorizedDomains] = useState('staging.acmepay.internal');
  const [baseUrls, setBaseUrls] = useState('https://staging.acmepay.internal:8443');
  const [allowedPorts, setAllowedPorts] = useState('8443, 443');
  const [allowSubdomains, setAllowSubdomains] = useState(false);
  const [exclusions, setExclusions] = useState('/admin/billing, /logout, /auth/oauth/callback');
  const [authRole, setAuthRole] = useState('test_standard_user');
  const [authUsername, setAuthUsername] = useState('sec_auditor_01@acmepay.internal');
  const [profile, setProfile] = useState<'observe' | 'source_review' | 'controlled_active' | 'authenticated' | 'regression'>('observe');
  const [maxSteps, setMaxSteps] = useState(20);
  const [maxRequests, setMaxRequests] = useState(50);
  const [maxDurationSec, setMaxDurationSec] = useState(300);

  if (!isWizardOpen) return null;

  const handleFinish = () => {
    addLog('info', 'wizard', `New assessment created for ${authorizedDomains} under profile: ${profile}`);
    setIsWizardOpen(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-3xl rounded-xl border border-zinc-800 bg-zinc-950 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-md bg-cyan-600/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-zinc-100">{t.wizard.title}</h2>
              <p className="text-[11px] text-zinc-400">Step {step} of 8</p>
            </div>
          </div>
          <button
            onClick={() => setIsWizardOpen(false)}
            className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Step Indicator Bar */}
        <div className="flex border-b border-zinc-800 bg-zinc-900/30 overflow-x-auto text-[11px] px-4 py-2 gap-2 text-zinc-400">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
            <button
              key={s}
              onClick={() => setStep(s)}
              className={`px-2.5 py-1 rounded flex items-center gap-1 shrink-0 ${
                step === s
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/40'
                  : s < step
                  ? 'text-emerald-400 font-medium'
                  : 'text-zinc-400 hover:text-zinc-300'
              }`}
            >
              <span>{s}</span>
              {s < step && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
            </button>
          ))}
        </div>

        {/* Step Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4 text-xs">
          {/* STEP 1: Project Name */}
          {step === 1 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step1}: Project Identification</h3>
              <p className="text-zinc-400">Group this target under an existing or newly named assessment project.</p>
              <div>
                <label className="block text-zinc-300 font-medium mb-1">Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          {/* STEP 2: Target Type */}
          {step === 2 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step2}: Select Target Architecture</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { id: 'website', label: t.wizard.targetTypes.website, desc: 'Web apps, single page applications, portals' },
                  { id: 'api', label: t.wizard.targetTypes.api, desc: 'REST, GraphQL, microservices endpoints' },
                  { id: 'source', label: t.wizard.targetTypes.source, desc: 'Offline repository source code (Python, JS/TS)' },
                  { id: 'combined', label: t.wizard.targetTypes.combined, desc: 'Synchronized live endpoint and source analysis' },
                ].map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setTargetType(type.id as any)}
                    className={`p-4 rounded-lg border text-left transition cursor-pointer ${
                      targetType === type.id
                        ? 'border-cyan-500 bg-cyan-950/20 text-cyan-200'
                        : 'border-zinc-800 bg-zinc-900/40 text-zinc-400 hover:border-zinc-700'
                    }`}
                  >
                    <div className="font-semibold text-zinc-200 mb-1">{type.label}</div>
                    <div className="text-[11px] text-zinc-400">{type.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 3: Authorized Scope */}
          {step === 3 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step3}: Explicit Scope Definition</h3>
              <div className="p-3 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] flex gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
                <span>{t.wizard.scopeNotice}</span>
              </div>
              <div>
                <label className="block text-zinc-300 font-medium mb-1">Authorized Domains (comma-separated)</label>
                <input
                  type="text"
                  value={authorizedDomains}
                  onChange={(e) => setAuthorizedDomains(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono"
                />
              </div>
              <div>
                <label className="block text-zinc-300 font-medium mb-1">Base URLs (comma-separated)</label>
                <input
                  type="text"
                  value={baseUrls}
                  onChange={(e) => setBaseUrls(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono"
                />
              </div>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <label className="block text-zinc-300 font-medium mb-1">Permitted Ports</label>
                  <input
                    type="text"
                    value={allowedPorts}
                    onChange={(e) => setAllowedPorts(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono"
                  />
                </div>
                <div className="pt-5 flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="subdomains"
                    checked={allowSubdomains}
                    onChange={(e) => setAllowSubdomains(e.target.checked)}
                    className="rounded border-zinc-700 text-cyan-600 focus:ring-0"
                  />
                  <label htmlFor="subdomains" className="text-zinc-300">Allow Subdomains (*.domain)</label>
                </div>
              </div>
            </div>
          )}

          {/* STEP 4: Exclusions */}
          {step === 4 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step4}: Strict Exclusions</h3>
              <p className="text-zinc-400">Endpoints, paths, and patterns that MUST NOT be touched by the agent or tools.</p>
              <div>
                <label className="block text-zinc-300 font-medium mb-1">Excluded Paths / Regexes (comma-separated)</label>
                <textarea
                  rows={4}
                  value={exclusions}
                  onChange={(e) => setExclusions(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono text-xs"
                />
              </div>
            </div>
          )}

          {/* STEP 5: Authentication */}
          {step === 5 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step5}: Dedicated Test Accounts</h3>
              <p className="text-zinc-400">Never use real or production user credentials. Provide test accounts with defined roles.</p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Account Role Label</label>
                  <input
                    type="text"
                    value={authRole}
                    onChange={(e) => setAuthRole(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100"
                  />
                </div>
                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Test Username / Email</label>
                  <input
                    type="text"
                    value={authUsername}
                    onChange={(e) => setAuthUsername(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100"
                  />
                </div>
              </div>
              <p className="text-[11px] text-zinc-400 italic">
                Passwords and tokens will be securely passed through backend environment references and automatically redacted from all outputs.
              </p>
            </div>
          )}

          {/* STEP 6: Testing Profile */}
          {step === 6 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step6}: Testing Profile & Operations</h3>
              <div className="space-y-2">
                {[
                  { id: 'observe', title: t.profiles.observe, desc: 'Public page inspection, headers, TLS, cookie flags. Zero state-changing requests.' },
                  { id: 'source_review', title: t.profiles.source_review, desc: 'Static code analysis, AST inspection, secret scanning. No code execution.' },
                  { id: 'controlled_active', title: t.profiles.controlled_active, desc: 'Explicitly approved vulnerability checks, strict request budget, human approval on mutations.' },
                  { id: 'authenticated', title: t.profiles.authenticated, desc: 'Authorization and session checks using dedicated test accounts. Reversible operations.' },
                  { id: 'regression', title: t.profiles.regression, desc: 'Re-runs previously verified tests after code patches.' },
                ].map((p) => (
                  <div
                    key={p.id}
                    onClick={() => setProfile(p.id as any)}
                    className={`p-3 rounded-lg border cursor-pointer transition ${
                      profile === p.id
                        ? 'border-cyan-500 bg-cyan-950/20 text-zinc-100'
                        : 'border-zinc-800 bg-zinc-900/40 text-zinc-400 hover:border-zinc-700'
                    }`}
                  >
                    <div className="font-semibold text-xs text-zinc-200">{p.title}</div>
                    <div className="text-[11px] text-zinc-400 mt-0.5">{p.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STEP 7: Limits & Budgets */}
          {step === 7 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step7}: Hard Safety Limits & Budgets</h3>
              <p className="text-zinc-400">Hard stop thresholds. When any limit is reached, execution immediately halts.</p>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Max Steps</label>
                  <input
                    type="number"
                    value={maxSteps}
                    onChange={(e) => setMaxSteps(Number(e.target.value))}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Max HTTP Requests</label>
                  <input
                    type="number"
                    value={maxRequests}
                    onChange={(e) => setMaxRequests(Number(e.target.value))}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Timeout (Seconds)</label>
                  <input
                    type="number"
                    value={maxDurationSec}
                    onChange={(e) => setMaxDurationSec(Number(e.target.value))}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 8: Review & Start */}
          {step === 8 && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-zinc-200">{t.wizard.step8}: Review Scope & Authorization</h3>
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-zinc-800/60">
                  <span className="text-zinc-400">Project:</span>
                  <span className="font-semibold text-zinc-200">{projectName}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/60">
                  <span className="text-zinc-400">Target Type:</span>
                  <span className="font-mono text-cyan-400">{targetType}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/60">
                  <span className="text-zinc-400">Authorized Domains:</span>
                  <span className="font-mono text-zinc-200">{authorizedDomains}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/60">
                  <span className="text-zinc-400">Selected Profile:</span>
                  <span className="font-medium text-emerald-400">{t.profiles[profile]}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-zinc-400">Hard Limits:</span>
                  <span className="font-mono text-zinc-300">{maxSteps} steps, {maxRequests} reqs, {maxDurationSec}s</span>
                </div>
              </div>

              <div className="p-3 rounded bg-zinc-900/60 border border-zinc-800 text-[11px] text-zinc-400">
                By starting, you certify that you own or have explicit written authorization to assess the specified domains.
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
          <button
            onClick={() => setStep((s) => Math.max(1, s - 1))}
            disabled={step === 1}
            className="flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium text-zinc-400 hover:text-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>{t.wizard.back}</span>
          </button>

          {step < 8 ? (
            <button
              onClick={() => setStep((s) => Math.min(8, s + 1))}
              className="flex items-center gap-1 px-4 py-1.5 rounded text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition cursor-pointer"
            >
              <span>{t.wizard.next}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleFinish}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-md cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{t.wizard.start}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
