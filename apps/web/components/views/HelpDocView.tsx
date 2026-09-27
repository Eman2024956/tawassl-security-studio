'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import {
  VULNERABILITY_DOCS,
  CATEGORY_LABELS,
  VulnerabilityDocItem
} from '../../lib/vulnerabilityDocs';
import {
  BookOpen,
  Search,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Terminal,
  Code2,
  Check,
  Copy,
  Layers,
  FileCode,
  Info,
  Bug,
  Filter,
  CheckCircle2,
  ExternalLink,
  Cpu
} from 'lucide-react';

export default function HelpDocView() {
  const { language, setLanguage, t } = useStudio();
  const [docLang, setDocLang] = useState<'en' | 'ar'>(language);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [activeTabs, setActiveTabs] = useState<Record<string, 'vulnerable' | 'remediation' | 'curlTest' | 'detectionLogic'>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Sync docLang with global language if changed externally, but allow local override
  const currentLang = docLang;
  const isAr = currentLang === 'ar';

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getActiveTabFor = (vulnId: string): 'vulnerable' | 'remediation' | 'curlTest' | 'detectionLogic' => {
    return activeTabs[vulnId] || 'vulnerable';
  };

  const setActiveTabFor = (vulnId: string, tab: 'vulnerable' | 'remediation' | 'curlTest' | 'detectionLogic') => {
    setActiveTabs((prev) => ({ ...prev, [vulnId]: tab }));
  };

  const filteredDocs = VULNERABILITY_DOCS.filter((item) => {
    const data = isAr ? item.ar : item.en;
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesSeverity = selectedSeverity === 'all' || item.severity === selectedSeverity;
    const query = searchQuery.trim().toLowerCase();
    const matchesSearch =
      !query ||
      data.title.toLowerCase().includes(query) ||
      data.summary.toLowerCase().includes(query) ||
      item.cwe.toLowerCase().includes(query) ||
      item.owasp.toLowerCase().includes(query) ||
      data.tabs.vulnerable.code.toLowerCase().includes(query) ||
      data.tabs.remediation.code.toLowerCase().includes(query);

    return matchesCategory && matchesSeverity && matchesSearch;
  });

  const getSeverityBadge = (severity: VulnerabilityDocItem['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/15 text-red-700 dark:text-red-400 border-red-500/40';
      case 'high':
        return 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/40';
      case 'medium':
        return 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/40';
      case 'low':
        return 'bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/40';
      default:
        return 'bg-slate-500/15 text-slate-700 dark:text-zinc-400 border-slate-500/30';
    }
  };

  const totalCount = VULNERABILITY_DOCS.length;
  const criticalHighCount = VULNERABILITY_DOCS.filter((v) => v.severity === 'critical' || v.severity === 'high').length;

  return (
    <div className={`space-y-6 ${isAr ? 'text-right' : 'text-left'}`} dir={isAr ? 'rtl' : 'ltr'}>
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-zinc-800 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
              <BookOpen className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-zinc-100">
              {isAr ? 'دليل المساعدة وقاعدة معرفة الثغرات الأمنية' : 'Security Vulnerability & Bug Catalog'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-zinc-400 max-w-2xl">
            {isAr
              ? 'دليل تقني شامل لجميع الثغرات وفحوصات باونتي المدعومة في الاستوديو مع تفاصيل الكود المصاب، وطرق المعالجة البرمجية، وأوامر الاختبار عبر Curl.'
              : 'Comprehensive technical guide and vulnerability database detailing vulnerable codebase patterns, production-ready remediation code, and reproducible curl test commands.'}
          </p>
        </div>

        {/* Bilingual Language Switcher Mode Tabs */}
        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="flex bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg p-1 text-xs">
            <button
              onClick={() => {
                setDocLang('en');
                setLanguage('en');
              }}
              className={`px-3 py-1.5 rounded-md font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                currentLang === 'en'
                  ? 'bg-white dark:bg-zinc-800 text-cyan-700 dark:text-cyan-400 shadow-xs'
                  : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
              }`}
            >
              <span>English</span>
            </button>
            <button
              onClick={() => {
                setDocLang('ar');
                setLanguage('ar');
              }}
              className={`px-3 py-1.5 rounded-md font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                currentLang === 'ar'
                  ? 'bg-white dark:bg-zinc-800 text-cyan-700 dark:text-cyan-400 shadow-xs'
                  : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
              }`}
            >
              <span>العربية (Arabic)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs">
          <div className="flex items-center gap-2 text-slate-500 dark:text-zinc-400 text-xs mb-1">
            <Bug className="w-3.5 h-3.5 text-cyan-500" />
            <span>{isAr ? 'إجمالي الثغرات والفحوصات' : 'Cataloged Vulnerabilities'}</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-900 dark:text-zinc-100">{totalCount}</div>
        </div>

        <div className="p-3.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs">
          <div className="flex items-center gap-2 text-slate-500 dark:text-zinc-400 text-xs mb-1">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
            <span>{isAr ? 'عالية وحرجة الخطورة' : 'Critical / High Severity'}</span>
          </div>
          <div className="text-xl font-bold font-mono text-rose-600 dark:text-rose-400">{criticalHighCount}</div>
        </div>

        <div className="p-3.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs">
          <div className="flex items-center gap-2 text-slate-500 dark:text-zinc-400 text-xs mb-1">
            <FileCode className="w-3.5 h-3.5 text-emerald-500" />
            <span>{isAr ? 'ألسنة الكود المصدرية' : 'Codebase Tabs'}</span>
          </div>
          <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">4 per Vulnerability</div>
        </div>

        <div className="p-3.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs">
          <div className="flex items-center gap-2 text-slate-500 dark:text-zinc-400 text-xs mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-500" />
            <span>{isAr ? 'حماية النطاق الصفري' : 'Zero-Trust Guard'}</span>
          </div>
          <div className="text-sm font-bold text-teal-600 dark:text-teal-400 mt-1">{isAr ? 'فعالة ونشطة' : 'Active & Enforced'}</div>
        </div>
      </div>

      {/* Search and Category Filters */}
      <div className="space-y-3 bg-white dark:bg-zinc-900/40 p-4 rounded-xl border border-slate-200 dark:border-zinc-800 shadow-xs">
        {/* Search Input */}
        <div className="relative">
          <Search className={`w-4 h-4 absolute top-3 text-slate-400 dark:text-zinc-500 ${isAr ? 'right-3' : 'left-3'}`} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={
              isAr
                ? 'ابحث باسم الثغرة، رقم CWE، تصنيف OWASP، أو الكود...'
                : 'Search by bug title, CWE, OWASP category, or code snippet...'
            }
            className={`w-full py-2 bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-lg text-xs text-slate-900 dark:text-zinc-100 placeholder:text-slate-400 dark:placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 ${
              isAr ? 'pr-9 pl-3' : 'pl-9 pr-3'
            }`}
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-slate-500 dark:text-zinc-400 font-medium flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            <span>{isAr ? 'التصنيف:' : 'Category:'}</span>
          </span>

          {Object.entries(isAr ? CATEGORY_LABELS.ar : CATEGORY_LABELS.en).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition cursor-pointer ${
                selectedCategory === key
                  ? 'bg-cyan-600 text-white font-semibold'
                  : 'bg-slate-100 dark:bg-zinc-800/80 text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-zinc-800'
              }`}
            >
              {label}
            </button>
          ))}

          <div className="h-4 w-px bg-slate-200 dark:bg-zinc-800 mx-1 hidden sm:block" />

          {/* Severity Filter */}
          <span className="text-slate-500 dark:text-zinc-400 font-medium">
            {isAr ? 'الخطورة:' : 'Severity:'}
          </span>
          {['all', 'critical', 'high', 'medium', 'low', 'info'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              className={`px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase transition cursor-pointer ${
                selectedSeverity === sev
                  ? 'bg-zinc-800 dark:bg-zinc-200 text-zinc-100 dark:text-zinc-900'
                  : 'text-slate-500 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-800'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Vulnerabilities List */}
      <div className="space-y-5">
        {filteredDocs.length === 0 ? (
          <div className="py-16 text-center space-y-3 bg-white dark:bg-zinc-900/30 rounded-xl border border-slate-200 dark:border-zinc-800">
            <Search className="w-8 h-8 text-slate-400 dark:text-zinc-500 mx-auto" />
            <h3 className="text-sm font-semibold text-slate-700 dark:text-zinc-300">
              {isAr ? 'لم يتم العثور على نتائج مطابقة' : 'No matching vulnerabilities found'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              {isAr
                ? 'جرب تغيير مصطلحات البحث أو إعادة تعيين الفلاتر لعرض جميع الثغرات.'
                : 'Try adjusting your search query or reset filters to view all cataloged items.'}
            </p>
          </div>
        ) : (
          filteredDocs.map((item) => {
            const data = isAr ? item.ar : item.en;
            const currentTab = getActiveTabFor(item.id);
            const activeCodeTab =
              currentTab === 'vulnerable'
                ? data.tabs.vulnerable
                : currentTab === 'remediation'
                ? data.tabs.remediation
                : currentTab === 'curlTest'
                ? data.tabs.curlTest
                : null;

            return (
              <div
                key={item.id}
                className="rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 p-5 space-y-4 shadow-xs transition hover:border-slate-300 dark:hover:border-zinc-700"
              >
                {/* Item Header */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase tracking-wider border ${getSeverityBadge(item.severity)}`}>
                        {item.severity}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-zinc-900 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-800">
                        {item.cwe}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-zinc-900 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-800">
                        {item.owasp}
                      </span>
                      <span className="text-[11px] font-medium text-cyan-600 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-200 dark:border-cyan-800/40">
                        {data.categoryLabel}
                      </span>
                    </div>

                    <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
                      {data.title}
                    </h2>
                  </div>

                  {/* Studio Status Badge */}
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-[11px] text-slate-600 dark:text-zinc-400 shrink-0">
                    <Cpu className="w-3.5 h-3.5 text-cyan-500" />
                    <span>{data.studioStatus}</span>
                  </div>
                </div>

                {/* Summary & Impact Box */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-slate-50 dark:bg-zinc-900/60 border border-slate-200 dark:border-zinc-800/80 space-y-1">
                    <div className="font-semibold text-slate-700 dark:text-zinc-300 flex items-center gap-1.5">
                      <Info className="w-3.5 h-3.5 text-cyan-500" />
                      <span>{isAr ? 'الوصف والميكانيكية التقنية:' : 'Vulnerability Mechanism:'}</span>
                    </div>
                    <p className="text-slate-600 dark:text-zinc-400 leading-relaxed">{data.summary}</p>
                  </div>

                  <div className="p-3 rounded-lg bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900/40 space-y-1">
                    <div className="font-semibold text-rose-700 dark:text-rose-400 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                      <span>{isAr ? 'الأثر الأمني والمخاطر:' : 'Security Impact:'}</span>
                    </div>
                    <p className="text-rose-800/90 dark:text-rose-300/80 leading-relaxed">{data.impact}</p>
                  </div>
                </div>

                {/* CODEBASE TABS SECTION */}
                <div className="space-y-2 pt-1">
                  {/* Tab Selectors */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 dark:border-zinc-800 pb-2">
                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                      {/* Tab 1: Vulnerable Pattern */}
                      <button
                        onClick={() => setActiveTabFor(item.id, 'vulnerable')}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          currentTab === 'vulnerable'
                            ? 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border border-rose-500/40'
                            : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900'
                        }`}
                      >
                        <Code2 className="w-3.5 h-3.5" />
                        <span>{isAr ? 'الكود المصاب' : 'Vulnerable Pattern'}</span>
                      </button>

                      {/* Tab 2: Secure Fix */}
                      <button
                        onClick={() => setActiveTabFor(item.id, 'remediation')}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          currentTab === 'remediation'
                            ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/40'
                            : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900'
                        }`}
                      >
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>{isAr ? 'الحل البرمجي الآمن' : 'Secure Remediation'}</span>
                      </button>

                      {/* Tab 3: Curl & CLI Test */}
                      <button
                        onClick={() => setActiveTabFor(item.id, 'curlTest')}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          currentTab === 'curlTest'
                            ? 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border border-cyan-500/40'
                            : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900'
                        }`}
                      >
                        <Terminal className="w-3.5 h-3.5" />
                        <span>{isAr ? 'أمر الاختبار (Curl)' : 'CLI / Curl Test'}</span>
                      </button>

                      {/* Tab 4: Studio Detection Logic */}
                      <button
                        onClick={() => setActiveTabFor(item.id, 'detectionLogic')}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          currentTab === 'detectionLogic'
                            ? 'bg-purple-500/15 text-purple-700 dark:text-purple-400 border border-purple-500/40'
                            : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900'
                        }`}
                      >
                        <Cpu className="w-3.5 h-3.5" />
                        <span>{isAr ? 'منطق الفحص في الاستوديو' : 'Studio Engine Rule'}</span>
                      </button>
                    </div>

                    {/* Copy Code Button for Active Tab */}
                    {activeCodeTab && (
                      <button
                        onClick={() => handleCopy(`${item.id}-${currentTab}`, activeCodeTab.code)}
                        className="flex items-center gap-1 text-[11px] text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200 transition cursor-pointer px-2 py-1 rounded bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800"
                        title="Copy code to clipboard"
                      >
                        {copiedId === `${item.id}-${currentTab}` ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-500" />
                            <span className="text-emerald-500 font-semibold">{isAr ? 'تم النسخ' : 'Copied'}</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>{isAr ? 'نسخ الكود' : 'Copy'}</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Tab Content Display */}
                  {currentTab === 'detectionLogic' ? (
                    <div className="p-4 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900/50 space-y-2 text-xs">
                      <div className="font-semibold text-slate-800 dark:text-zinc-200 flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-purple-500" />
                        <span>{data.tabs.detectionLogic.title}</span>
                      </div>
                      <p className="text-slate-600 dark:text-zinc-400 leading-relaxed">
                        {data.tabs.detectionLogic.description}
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-slate-200 dark:border-zinc-800/80 font-mono text-[11px]">
                        <div>
                          <span className="text-slate-400 dark:text-zinc-500">{isAr ? 'التصنيف الناتج: ' : 'Classification: '}</span>
                          <span className="text-cyan-600 dark:text-cyan-400 font-semibold">{data.tabs.detectionLogic.classification}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 dark:text-zinc-500">{isAr ? 'النتيجة المتوقعة: ' : 'Expected Result: '}</span>
                          <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{data.tabs.detectionLogic.expectedResult}</span>
                        </div>
                      </div>
                    </div>
                  ) : activeCodeTab ? (
                    <div className="space-y-2">
                      <div className="rounded-xl border border-slate-200 dark:border-zinc-800 bg-zinc-950 p-4 font-mono text-xs text-zinc-200 overflow-x-auto shadow-inner relative group" dir="ltr">
                        <div className="flex items-center justify-between text-[10px] text-zinc-500 pb-2 border-b border-zinc-800 mb-2">
                          <span className="font-semibold uppercase tracking-wider text-zinc-400">{activeCodeTab.language}</span>
                          <span>{activeCodeTab.title}</span>
                        </div>
                        <pre className="whitespace-pre-wrap leading-relaxed">{activeCodeTab.code}</pre>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-zinc-400 px-1 leading-relaxed">
                        <span className="font-semibold text-slate-700 dark:text-zinc-300">
                          {isAr ? 'شرح الكود: ' : 'Technical Note: '}
                        </span>
                        {activeCodeTab.explanation}
                      </p>
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
