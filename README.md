# Tawassl Security Studio | استوديو تواصل للأمن السيبراني

[![Backend Tests](https://img.shields.io/badge/pytest-30%20passed-emerald)](./apps/backend/tests)
[![Next.js Build](https://img.shields.io/badge/next.js-v16%20passing-cyan)](./apps/web)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](./apps/backend)
[![License](https://img.shields.io/badge/license-MIT-zinc)](./LICENSE)

**Tawassl Security Studio** (`tawassl-security-studio`) is a local-first, privacy-respecting AI security and functional bug assessment workspace. Built from scratch with human-in-the-loop oversight, strict zero-trust scope enforcement, sandboxed command execution, and AI orchestration powered by Google Gemini, OpenAI GPT, or an offline `MockProvider`.

---

## English Quickstart

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm

### 1. Setup Backend
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

### 2. Setup Frontend
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

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key settings:
- `DEFAULT_AI_PROVIDER`: `mock` (default for 100% offline development), `gemini`, or `openai`.
- `GEMINI_API_KEY`: Optional; required only when using live Gemini models.
- `OPENAI_API_KEY`: Optional; required only when using live OpenAI GPT models.
- `ALLOWED_ORIGINS`: Comma-separated list (default `http://localhost:3000`).

---

## Architecture & Safety Principles

1. **Zero-Trust Scope & SSRF Guard:** Empty scope denies all access. All target URLs, ports, and redirection headers are strictly checked against authorized domains. Cloud metadata (`169.254.169.254`) and loopback/private IP addresses are blocked.
2. **Immutable Proposals & Atomic Approvals:** Models propose typed tool calls; they never execute shell commands directly. Every command with side-effects requires human approval backed by a single-use SHA-256 token.
3. **Isolated Worker:** Commands run via subprocess arrays (`shell=False`). Provider keys, host SSH agents, and sensitive environment variables are completely scrubbed from child processes.
4. **Hard Budgets:** Fixed limits on steps, requests, duration, and output size. Once exhausted, execution immediately stops.
5. **Verified Evidence:** "Model agreement does not confirm a vulnerability." Evidence is required before advancing finding statuses. Reports explicitly declare coverage limitations.

---

## باللغة العربية (Arabic Overview)

### استوديو تواصل للأمن السيبراني

**استوديو تواصل للأمن السيبراني** هو بيئة عمل محلية متقدمة ومدعومة بنماذج الذكاء الاصطناعي لفحص واكتشاف الثغرات الأمنية والأخطاء البرمجية في المواقع، واجهات برمجة التطبيقات (APIs)، ومشاريع الكود المصدري المصرح بفحصها فقط.

### المميزات الرئيسية:
- **تحكم بشري كامل (Human-in-the-Loop):** لا ينفذ الذكاء الاصطناعي أي أمر ذي تأثير دون موافقة صريحة لمرة واحدة مبنية على بصمة SHA-256 مشفرة.
- **نطاق أمني صارم (Zero-Trust Scope):** حماية كاملة ضد هجمات تزوير الطلبات (SSRF)، إعادة توجيه الروابط الخبيثة، والتلاعب بنظام أسماء النطاقات (DNS Rebinding).
- **بيئة عزل محلية (Isolated Worker):** عزل تام للعمليات بدون صلاحيات الـ Root، وحجب تلقائي لكافة المفاتيح والبيانات السرية من المخرجات والطرفية.
- **مزودات ذكاء اصطناعي متعددة:** دعم كامل لنماذج Google Gemini و OpenAI GPT بالإضافة إلى مزود محلي دون إنترنت (`MockProvider`).
- **تقارير أمنية قياسية:** تصدير فوري للتقارير بصيغ Markdown و JSON ومعيار SARIF 2.1.0 المعتمد في مجتمع الأمن السيبراني.

### التشغيل السريع:
```bash
# ١. إعداد البيئة الخلفية (Python)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt # أو الحزم المحددة
PYTHONPATH=. pytest apps/backend/tests -v
PYTHONPATH=. uvicorn apps.backend.app.main:app --host 127.0.0.1 --port 8000

# ٢. تشغيل الواجهة الأمامية (Next.js)
cd apps/web
npm install
npm run dev
```

---

## Documentation Links
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Threat Model & Mitigations](./docs/THREAT_MODEL.md)
- [Implementation & Verification Matrix](./docs/IMPLEMENTATION_MATRIX.md)
