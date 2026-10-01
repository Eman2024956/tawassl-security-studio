'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldAlert, ArrowLeft, Terminal, Home, Lock, Sparkles, CheckCircle2 } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-4 relative overflow-hidden select-none">
      {/* Futuristic Background Glow & Grid */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-[300px] h-[300px] bg-purple-500/10 rounded-full blur-[90px] pointer-events-none" />

      {/* Cyber Grid Lines Overlay (Zero inline styles for strict CSP compliance) */}
      <svg className="absolute inset-0 w-full h-full opacity-20 pointer-events-none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <pattern id="notFoundCyberGrid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="rgba(6, 182, 212, 0.25)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#notFoundCyberGrid)" />
      </svg>

      <div className="relative z-10 max-w-xl w-full text-center space-y-6">
        {/* Glowing Shield 404 Emblem */}
        <div className="relative inline-flex items-center justify-center">
          <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-3xl bg-linear-to-br from-cyan-500/20 via-teal-500/10 to-emerald-500/20 border border-cyan-500/40 p-1 flex items-center justify-center shadow-2xl shadow-cyan-500/20">
            <div className="w-full h-full rounded-[22px] bg-slate-900/90 flex flex-col items-center justify-center relative overflow-hidden">
              <ShieldAlert className="w-12 h-12 text-cyan-400 mb-1 animate-pulse" />
              <div className="text-[11px] font-mono font-bold text-emerald-400 tracking-wider">
                SCOPE-GUARD
              </div>
            </div>
          </div>
          <div className="absolute -bottom-2 px-3 py-0.5 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 font-mono text-[11px] font-bold shadow-lg">
            HTTP 404
          </div>
        </div>

        {/* Status Chip */}
        <div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-cyan-950/60 text-cyan-300 border border-cyan-800/80 shadow-inner">
            <Lock className="w-3.5 h-3.5 text-cyan-400" />
            <span>ROUTE_OUT_OF_SCOPE • المسار خارج النطاق</span>
          </span>
        </div>

        {/* Headings */}
        <div className="space-y-2">
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            Page Not Found
          </h1>
          <p className="text-lg sm:text-xl font-bold text-cyan-400 font-sans" dir="rtl">
            عذراً، الصفحة المطلوبة غير موجودة
          </p>
          <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto leading-relaxed pt-1">
            The target route you requested does not exist or has been isolated by zero-trust scope policy. All internal data and sessions remain securely protected.
          </p>
          <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed font-sans" dir="rtl">
            المسار المطلوب يقع خارج نطاق العمليات المصرح بها أو تم نقله. لا توجد أي بيانات معرضة للخطر.
          </p>
        </div>

        {/* Security Telemetry Box */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-left font-mono text-[11px] space-y-1.5 text-slate-400 shadow-lg">
          <div className="flex items-center justify-between text-slate-500 border-b border-slate-800/80 pb-1.5 mb-1.5">
            <div className="flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>SECURITY TELEMETRY LOG</span>
            </div>
            <span className="text-[10px] text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> ZERO-TRUST ACTIVE
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">EVENT_STATUS:</span>
            <span className="text-rose-400 font-bold">404_NOT_FOUND</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">EGRESS_GUARD:</span>
            <span className="text-cyan-300">STRICT_ISOLATION</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">STUDIO_ENGINE:</span>
            <span className="text-slate-300">ScopeGuard v2026.1</span>
          </div>
        </div>

        {/* The One Primary Action Button */}
        <div className="pt-2">
          <Link
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 rounded-xl font-bold text-sm bg-linear-to-r from-cyan-600 via-teal-500 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white shadow-xl shadow-cyan-600/25 hover:shadow-cyan-500/40 transition-all duration-200 cursor-pointer active:scale-98"
          >
            <Home className="w-4 h-4" />
            <span>Return to ScopeGuard Studio</span>
            <span className="opacity-80 font-sans font-medium text-xs border-l border-white/20 pl-2 ml-1">
              العودة للوحة التحكم
            </span>
          </Link>
        </div>

        {/* Developer Attribution Footer */}
        <div className="pt-4 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-500">
          <div className="flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-cyan-500" />
            <span>ScopeGuard Security Studio • 2026</span>
          </div>
          <div>
            Developer: <span className="text-slate-300 font-semibold">Falah G. Salieh</span> (AI Developer Since 1988)
          </div>
        </div>
      </div>
    </div>
  );
}
