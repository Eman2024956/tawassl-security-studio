'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import { Settings as SettingsIcon, Cpu, ShieldCheck, Key, Save, Check } from 'lucide-react';

export default function SettingsView() {
  const { language, setLanguage, theme, setTheme, t } = useStudio();
  const [provider, setProvider] = useState<'mock' | 'gemini' | 'openai'>('mock');
  const [modelId, setModelId] = useState('mock-sec-v1');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="border-b border-zinc-800 pb-3">
        <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-cyan-400" />
          <span>{t.settings.title}</span>
        </h2>
        <p className="text-xs text-zinc-400 mt-0.5">
          Local configuration. Credentials remain securely stored on your local machine only.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6 text-xs">
        {/* Section 1: AI Provider Selection */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>{t.settings.aiSection}</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { id: 'mock', name: 'MockProvider', desc: '100% offline development. Zero API calls or cost.' },
              { id: 'gemini', name: 'Google Gemini', desc: 'Official Google Gen AI SDK integration.' },
              { id: 'openai', name: 'OpenAI GPT', desc: 'Official OpenAI SDK integration.' },
            ].map((p) => (
              <div
                key={p.id}
                onClick={() => setProvider(p.id as any)}
                className={`p-3.5 rounded-lg border cursor-pointer transition ${
                  provider === p.id
                    ? 'border-cyan-500 bg-cyan-950/20 text-cyan-200'
                    : 'border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:border-zinc-700'
                }`}
              >
                <div className="font-bold text-xs text-zinc-100">{p.name}</div>
                <div className="text-[11px] text-zinc-500 mt-1">{p.desc}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-zinc-300 font-medium mb-1">Model Identifier</label>
              <input
                type="text"
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-zinc-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-zinc-300 font-medium mb-1">Google Gemini API Key</label>
              <input
                type="password"
                placeholder={provider === 'gemini' ? 'AIzaSy...' : 'Not required for MockProvider'}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-zinc-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Appearance & Language */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300">
            {t.settings.themeSection}
          </h3>

          <div className="flex flex-wrap items-center gap-6">
            <div>
              <label className="block text-zinc-400 mb-1.5 font-medium">Interface Language</label>
              <div className="flex bg-zinc-900 border border-zinc-800 rounded-lg p-0.5">
                <button
                  type="button"
                  onClick={() => setLanguage('en')}
                  className={`px-3 py-1 rounded-md transition ${language === 'en' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400'}`}
                >
                  English (LTR)
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage('ar')}
                  className={`px-3 py-1 rounded-md transition ${language === 'ar' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400'}`}
                >
                  العربية (RTL)
                </button>
              </div>
            </div>

            <div>
              <label className="block text-zinc-400 mb-1.5 font-medium">Theme Mode</label>
              <div className="flex bg-zinc-900 border border-zinc-800 rounded-lg p-0.5">
                <button
                  type="button"
                  onClick={() => setTheme('dark')}
                  className={`px-3 py-1 rounded-md transition ${theme === 'dark' ? 'bg-zinc-800 text-cyan-300' : 'text-zinc-400'}`}
                >
                  Dark Cybersecurity
                </button>
                <button
                  type="button"
                  onClick={() => setTheme('light')}
                  className={`px-3 py-1 rounded-md transition ${theme === 'light' ? 'bg-zinc-800 text-zinc-900 font-bold' : 'text-zinc-400'}`}
                >
                  Light Mode
                </button>
              </div>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="flex items-center gap-2 px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-md transition cursor-pointer"
        >
          {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          <span>{saved ? 'Saved!' : t.settings.save}</span>
        </button>
      </form>
    </div>
  );
}
