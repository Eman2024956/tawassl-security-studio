# ScopeGuard Security Studio | استوديو سكوپ غارد للأمن السيبراني
### (Formerly Tawassl Security Studio)

[![Live Production](https://img.shields.io/badge/Vercel-scopeguard--seven--black.vercel.app-cyan?logo=vercel)](https://scopeguard-seven-black.vercel.app/)
[![Backend Tests](https://img.shields.io/badge/pytest-30%20passed-emerald)](./apps/backend/tests)
[![Next.js Build](https://img.shields.io/badge/next.js-v16%20passing-cyan)](./apps/web)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](./apps/backend)
[![Developer](https://img.shields.io/badge/Developer-Falah%20G.%20Salieh%20(1988)-purple)](https://scopeguard-seven-black.vercel.app/)
[![License](https://img.shields.io/badge/license-MIT-zinc)](./LICENSE)

**ScopeGuard Security Studio** is an original, local-first, privacy-respecting AI security and functional bug assessment workspace. Built with human-in-the-loop oversight, strict zero-trust scope enforcement, sandboxed command execution, and AI orchestration powered by Google Gemini, OpenAI GPT, or an offline `MockProvider`.

* **Live Cloud Deployment:** [https://scopeguard-seven-black.vercel.app/](https://scopeguard-seven-black.vercel.app/)
* **Chief Architect & Developer:** **Falah G. Salieh** (`الأستاذ فلاح كاطع صالح`) — AI Developer Since 1988 & Physics/Mathematics Teacher, Baghdad, Iraq (2026).

---

## 🌟 Developer Profile: Falah G. Salieh (1988 — 2026)

* **Legacy:** Over **38 years** of continuous artificial intelligence, algorithmic logic, and systems engineering (Genesis in 1988).
* **Academic Discipline:** Senior **Physics & Mathematical Teacher** bringing theoretical mechanics, differential equations, and tensor analysis to deterministic neural architectures and AI safety.
* **Location:** Baghdad, Iraq • 2026.
* **Developer Profile in Studio:** Explore the dedicated **Developer Profile** section in ScopeGuard Studio featuring:
  - Interactive **38-Year History & Milestones** timeline (1988 — 2026).
  - **Pillars of Mastery:** AI Architecture, Physics/Math Pedagogy, Zero-Trust Engineering, Academic Mentorship.
  - **Featured Projects Showcase:** ScopeGuard Security Studio, PhysiMath AI Engine, Quantum-Classical Solvers, and Baghdad Math Lab.
  - **In-App Technical Articles & Reader:** Deep dives into PINNs, mathematical cybersecurity proofs, and sovereign AI.
  - **Direct Inquiry & Email Hub:** `falah.g.salieh@gmail.com` with one-click copy and contact form.
  - **Official Blog:** [https://blog.falahgsalieh.dev](https://blog.falahgsalieh.dev)

---

## 🎨 Branding, Favicon & Social Media Preview

* **High-Definition OpenGraph Preview Card:** Beautiful 16:9 social share banner ([`/og-image.jpg`](https://scopeguard-seven-black.vercel.app/og-image.jpg)) with custom cyber-shield, security analytics telemetry, and developer credit for Falah G. Salieh.
* **Vector & Multi-Size Favicon Suite:**
  - `favicon.svg`: Infinitely sharp neon cyan and emerald vector shield.
  - `favicon.ico`: Universal multi-format icon for all browsers.
  - `favicon-32x32.png` & `favicon-16x16.png`: Crisp desktop tab icons.
  - `apple-touch-icon.png` (180x180): High-res icon for mobile and iOS home screens.
  - `site.webmanifest`: Progressive Web App (PWA) configuration with dark cyber theme.
* **Bilingual SEO & Social Metadata:** Full OpenGraph, Twitter Large Summary Cards, canonical links, and hreflang tags for English (`en-US`) and Arabic (`ar-IQ`).

---

## English Quickstart

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm

### 1. Setup Backend (Local Python)
```bash
# Create virtual environment and activate
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install fastapi "uvicorn[standard]" "pydantic>=2.0" pydantic-settings aiosqlite httpx pytest pytest-asyncio python-multipart google-genai openai

# Run test suite (30 passed)
PYTHONPATH=. pytest apps/backend/tests -v

# Start FastAPI backend server (http://127.0.0.1:8000)
PYTHONPATH=. uvicorn apps.backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Setup Frontend (Next.js 16)
```bash
# Navigate to web app
cd apps/web

# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Or build for production
npm run build
```

### 3. Serverless & Cloud Deployment
The frontend includes built-in Next.js App Router API route handlers (`/api/projects`, `/api/targets`, `/api/assessments`, `/api/findings`, `/api/approvals`, `/api/health`). It can be deployed instantly to Vercel as a standalone zero-config cloud app:
```bash
cd apps/web
vercel --prod
```

### 4. Key Features & Bug Bounty Capabilities
- **Target Domain Scope:** Default target is configured to `scopeguard-seven-black.vercel.app` (and `scopeguard.vercel.app`) with strict zero-trust boundary validation.
- **Bug Bounty Security Suite:**
  - Strict-Transport-Security (HSTS), Content-Security-Policy (CSP), and clickjacking audit.
  - CORS Misconfiguration Probe (evaluates arbitrary origin reflection with credentials).
  - Open Redirect & Insecure URL Forwarding validation (`?redirect=`, `?next=`).
  - Crawler & Route Reconnaissance (`robots.txt` and `sitemap.xml`).
  - Git Repository Exposure (`/.git/HEAD`) & configuration leak testing.
  - Single Page Application (SPA) HTML fallback differentiation (avoids false-positive secret leak reports).
  - Server Fingerprinting & Technology Banner version masking.
- **Live Output & Audit History Log Export:**
  - Real-time sanitized terminal with automated credential redaction.
  - One-click **Clear Logs** action to reset view between runs.
  - Instant **Export History Log** downloading structured `.log` files (`tawassl-audit-history-[timestamp].log`) for bug bounty documentation and archiving.

---

## Architecture & Safety Principles

1. **Zero-Trust Scope & SSRF Guard:** Empty scope denies all access. All target URLs, ports, and redirection headers are strictly checked against authorized domains (`scopeguard.vercel.app`). Cloud metadata (`169.254.169.254`) and loopback/private IP addresses are blocked.
2. **Immutable Proposals & Atomic Approvals:** Models propose typed tool calls; they never execute shell commands directly. Every command with side-effects requires human approval backed by a single-use SHA-256 token.
3. **Isolated Worker:** Commands run via subprocess arrays (`shell=False`). Provider keys, host SSH agents, and sensitive environment variables are completely scrubbed from child processes.
4. **Hard Budgets:** Fixed limits on steps, requests, duration, and output size. Once exhausted, execution immediately stops.
5. **Verified Evidence:** "Model agreement does not confirm a vulnerability." Evidence is required before advancing finding statuses. Reports explicitly declare coverage limitations.

---

## باللغة العربية (Arabic Overview)

### استوديو سكوپ غارد للأمن السيبراني | ScopeGuard Security Studio

**استوديو سكوپ غارد للأمن السيبراني** (المعروف سابقاً باستوديو تواصل) هو بيئة عمل محلية متقدمة ومدعومة بنماذج الذكاء الاصطناعي لفحص واكتشاف الثغرات الأمنية (Bug Bounty) والأخطاء البرمجية في المواقع، واجهات برمجة التطبيقات (APIs)، ومشاريع الكود المصدري المصرح بفحصها فقط (`scopeguard-seven-black.vercel.app`).

* **الرابط المباشر على سحابة Vercel:** [https://scopeguard-seven-black.vercel.app/](https://scopeguard-seven-black.vercel.app/)
* **المعماري والمطور الرئيسي:** **الأستاذ فلاح كاطع صالح (Falah G. Salieh)** — مطور ذكاء اصطناعي منذ عام 1988 وأستاذ الفيزياء والرياضيات - بغداد، العراق (2026).

### المميزات الرئيسية:
- **الملف التعريفي للمطور (Falah G. Salieh):** قسم كامل يستعرض مسيرة 38 عاماً من الخبرة البرمجية (1988 — 2026)، الربط بين الفيزياء النظرية والرياضيات والذكاء الاصطناعي، معرض المشاريع، وقارئ المقالات التخصصية.
- **الهوية البصرية والأيقونات:** أيقونة SVG متجهة فائقة الدقة، أيقونات لكافة المنصات والمتصفحات، وبطاقة معاينة للمشاركة على وسائل التواصل الاجتماعي (OpenGraph) تحمل اسم المطور ومعالم الاستوديو.
- **تحكم بشري كامل (Human-in-the-Loop):** لا ينفذ الذكاء الاصطناعي أي أمر ذي تأثير دون موافقة صريحة لمرة واحدة مبنية على بصمة SHA-256 مشفرة.
- **فحوصات Bug Bounty شاملة:** فحص ترويسات الأمان، كشف ثغرات CORS، التحقق من إعادة التوجيه المفتوح (Open Redirect)، استكشاف `robots.txt`، واختبار تسريبات Git.
- **الطرفية المباشرة وتصدير سجل التدقيق:** متابعة حية للأحداث مع إمكانية مسح الشاشة وتصدير سجل التدقيق التاريخي كملف `.log` بضغطة زر واحدة.
- **نطاق أمني صارم (Zero-Trust Scope):** حماية كاملة ضد هجمات تزوير الطلبات (SSRF)، إعادة توجيه الروابط الخبيثة، والتلاعب بنظام أسماء النطاقات (DNS Rebinding).
- **بيئة عزل محلية (Isolated Worker):** عزل تام للعمليات بدون صلاحيات الـ Root، وحجب تلقائي لكافة المفاتيح والبيانات السرية من المخرجات والطرفية.
- **مزودات ذكاء اصطناعي متعددة:** دعم كامل لنماذج Google Gemini و OpenAI GPT بالإضافة إلى مزود محلي دون إنترنت (`MockProvider`).
- **تقارير أمنية قياسية:** تصدير فوري للتقارير بصيغ Markdown و JSON ومعيار SARIF 2.1.0 المعتمد في مجتمع الأمن السيبراني.

---

## Documentation Links
- [Arabic Security & Bug Bounty Testing Guide (دليل الفحص بالعربية)](./docs/ARABIC_TESTING_GUIDE_MATAMI.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Threat Model & Mitigations](./docs/THREAT_MODEL.md)
- [Implementation & Verification Matrix](./docs/IMPLEMENTATION_MATRIX.md)
