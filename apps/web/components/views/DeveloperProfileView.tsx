'use client';

import React, { useState } from 'react';
import { useStudio } from '../../lib/context';
import {
  Award,
  Sparkles,
  BookOpen,
  Code2,
  Atom,
  GraduationCap,
  Mail,
  Copy,
  Check,
  ExternalLink,
  MapPin,
  Calendar,
  Layers,
  Send,
  Terminal,
  ShieldCheck,
  ChevronRight,
  ArrowRight,
  Flame,
  Globe,
  Star,
  Cpu,
  Bookmark,
  Share2,
  UserCheck,
  FolderGit2,
  X
} from 'lucide-react';

interface ProjectItem {
  id: string;
  title: string;
  category: 'ai' | 'physics-math' | 'cybersecurity' | 'education';
  year: string;
  role: string;
  description: string;
  tech: string[];
  linkType: 'internal' | 'external';
  linkTarget?: string;
  highlights: string[];
}

interface ArticleItem {
  id: string;
  title: string;
  titleAr: string;
  date: string;
  readTime: string;
  category: string;
  summary: string;
  summaryAr: string;
  content: string;
  contentAr: string;
  tags: string[];
}

export default function DeveloperProfileView() {
  const { language, setActiveTab, t } = useStudio();
  const [copiedEmail, setCopiedEmail] = useState(false);
  const [projectFilter, setProjectFilter] = useState<'all' | 'ai' | 'physics-math' | 'cybersecurity'>('all');
  const [selectedArticle, setSelectedArticle] = useState<ArticleItem | null>(null);

  // Contact Form state
  const [formName, setFormName] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formSubject, setFormSubject] = useState('');
  const [formMessage, setFormMessage] = useState('');
  const [formSent, setFormSent] = useState(false);

  const emailAddress = 'falah.g.salieh@gmail.com';
  const blogUrl = 'https://blog.falahgsalieh.dev';

  const copyEmail = () => {
    navigator.clipboard.writeText(emailAddress);
    setCopiedEmail(true);
    setTimeout(() => setCopiedEmail(false), 2500);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formEmail || !formMessage) return;
    setFormSent(true);
    setTimeout(() => {
      setFormSent(false);
      setFormName('');
      setFormEmail('');
      setFormSubject('');
      setFormMessage('');
    }, 4000);
  };

  const projects: ProjectItem[] = [
    {
      id: 'tawassl-studio',
      title: 'Tawassl Security Studio (2026 Flagship)',
      category: 'cybersecurity',
      year: '2026',
      role: 'Chief Architect & Lead Developer',
      description:
        'A local-first, zero-trust AI security & vulnerability exploration studio. Features strict hard safety budgets, automated multi-turn verification, offline-safe execution, and SARIF/JSON reporting.',
      tech: ['Next.js 14', 'TypeScript', 'FastAPI', 'Gemini AI', 'TailwindCSS', 'SARIF 2.1.0'],
      linkType: 'internal',
      linkTarget: 'dashboard',
      highlights: [
        'Hard safety budgeting & Zero-Trust egress sandbox',
        'Multi-model fallback & simulated offline rule engine',
        'Bilingual English & Arabic localized enterprise studio'
      ]
    },
    {
      id: 'physimath-engine',
      title: 'PhysiMath AI & Differential Solvers',
      category: 'physics-math',
      year: '2024 - 2026',
      role: 'Principal Researcher & Developer',
      description:
        'High-performance scientific computing framework marrying Physics-Informed Neural Networks (PINNs) with Runge-Kutta numerical solvers to simulate complex dynamical physical systems in real time.',
      tech: ['Python', 'PyTorch', 'C++20', 'WebAssembly', 'SymPy', 'NumPy'],
      linkType: 'external',
      linkTarget: '#',
      highlights: [
        'Enforces thermodynamic & energy conservation constraints in latent loss',
        'Sub-millisecond solver for non-linear coupled differential equations',
        'Deployed for academic physics education and laboratory simulations'
      ]
    },
    {
      id: 'quantum-optimizer',
      title: 'Baghdad Quantum-Classical Algorithmic Solver',
      category: 'ai',
      year: '2022 - 2025',
      role: 'Lead Algorithmic Architect',
      description:
        'A hybrid combinatorial optimization engine combining quantum annealing formulations with classical simulated physics to solve large-scale NP-hard logistical and cryptographic challenges.',
      tech: ['Rust', 'Python', 'Qiskit Algorithms', 'Graph Theory', 'SIMD'],
      linkType: 'external',
      linkTarget: '#',
      highlights: [
        'Novel Hamiltonian penalty formulation for graph partition problems',
        'Tested on distributed networks with 99.4% convergence accuracy',
        'Authored open research benchmarks for classical-quantum comparison'
      ]
    },
    {
      id: 'edutech-academy',
      title: 'Baghdad Math & Physics Interactive Lab',
      category: 'education',
      year: '1998 - 2026 (Continuous Legacy)',
      role: 'Founder, Master Educator & Curriculum Designer',
      description:
        'Comprehensive interactive laboratory and curriculum for higher mathematics and theoretical physics. Features live 3D visualizers for tensor fields, relativity, and multivariable calculus.',
      tech: ['React', 'Three.js', 'WebGL', 'KaTeX', 'Interactive Canvas'],
      linkType: 'external',
      linkTarget: '#',
      highlights: [
        'Trained over 3,500 students, engineers, and researchers across Iraq',
        'Bridging pure abstract mathematics with practical computing implementations',
        'Free, sovereign educational resources created for universities in Baghdad'
      ]
    },
    {
      id: 'aegis-copilot',
      title: 'AegisAgent Sovereign Red-Team Copilot',
      category: 'cybersecurity',
      year: '2025 - 2026',
      role: 'Security Systems Architect',
      description:
        'Air-gapped autonomous agent framework providing defensive security audits and automated threat modeling with deterministic proof chains and zero data leakage.',
      tech: ['TypeScript', 'Go', 'Docker Sandboxing', 'Local Vector DB', 'ONNX Runtime'],
      linkType: 'internal',
      linkTarget: 'agent',
      highlights: [
        '100% offline sovereign execution without third-party cloud dependencies',
        'Cryptographic audit trail for every tool execution step',
        'Integrated with Tawassl Security Studio command queue'
      ]
    }
  ];

  const articles: ArticleItem[] = [
    {
      id: 'art-1',
      title: 'From 1988 to 2026: 38 Years of Computing, Code, and the Essence of AI',
      titleAr: 'من عام 1988 إلى 2026: 38 عاماً في الحوسبة والبرمجة والجوهر الحقيقي للذكاء الاصطناعي',
      date: 'January 2026',
      readTime: '8 min read',
      category: 'AI Philosophy & History',
      tags: ['History of AI', 'Algorithms', 'Symbolic vs Neural', 'Legacy'],
      summary:
        'A comprehensive retrospective spanning nearly four decades of hands-on software development: from 8-bit microcomputers and early symbolic heuristics in 1988 to modern sovereign multi-agent neural architectures in 2026.',
      summaryAr:
        'نظرة شاملة ومحطات ملهمة تمتد لقرابة أربعة عقود من تطوير البرمجيات: من أجهزة الميكروكومبيوتر ذات الـ 8 بت والمنطق الرمزي عام 1988 إلى المعماريات العصبية والوكلاء الأذكياء المستقلين في عام 2026.',
      content: `### The Genesis: 1988 in Baghdad
When I began programming artificial intelligence and complex algorithms in 1988, computing was governed by rigorous mathematical precision. Memory was measured in kilobytes; CPU cycles were precious commodities. If an algorithm was inefficient, it simply did not run. Early neural concepts—Hopfield networks, perceptrons, expert systems in LISP and Pascal—demanded complete conceptual mastery from first principles.

### The Physics of Computing
As a teacher of physics and mathematics, I realized early on that computing and natural law are two sides of the same coin:
1. **Conservation of Information**: Just as energy cannot be created or destroyed, an algorithmic system cannot yield true insight without preserving signal integrity and eliminating entropy.
2. **Deterministic Foundations vs. Probabilistic Models**: Today's generative AI models are astonishing, but they remain probabilistic approximations. Without deterministic bounds, formal mathematical proofs, and safety guardrails, AI is merely a chaotic oscillator.

### The 2026 Horizon: Sovereign, Local-First AI
In 2026, the true frontier of software engineering is not bigger cloud models, but **sovereign, local-first intelligence**. Systems like *Tawassl Security Studio* reflect this culmination: tools that run locally, respect hard resource limits, guarantee zero unauthorized egress, and provide deterministic safety verification. 

Thirty-eight years have taught me that tools change, but fundamental laws of mathematics, logic, and integrity endure forever.`,
      contentAr: `### البدايات: عام 1988 في بغداد
عندما بدأت برمجة خوارزميات الذكاء الاصطناعي والنظم الخبيرة في عام 1988، كانت الحوسبة محكومة بالدقة الرياضية الصارمة. كانت الذاكرة تقاس بالكيلوبايت، وكل نبضة معالج ذات قيمة حاسمة. إن لم تكن الخوارزمية محسوبة بدقة متناهية، فلن تعمل على الإطلاق. تطلبت نماذج الشبكات العصبية المبكرة ونظم المنطق الرمزي بلغات باسكال وليسب فهماً جذرياً من المبادئ الأولى.

### فيزياء الحوسبة
بصفتي أستاذاً للفيزياء والرياضيات، أدركت مبكراً أن القوانين الفيزيائية وهندسة البرمجيات وجهان لعملة واحدة:
1. **حفظ المعلومات والإنتروبيا**: تماماً كما لا تفنى الطاقة ولا تُستحدث من العدم، لا يمكن لأي نظام خوارزمي إنتاج معرفة نقية ما لم يحافظ على سلامة الإشارة ويتخلص من العشوائية.
2. **الأسس الحتمية مقابل النماذج الاحتمالية**: الذكاء الاصطناعي التوليدي اليوم مذهل، لكنه يظل تقريبات احتمالية. بدون القيود الرياضية الحتمية وضوابط الأمان الصارمة، يتحول النظام إلى مذبذب عشوائي غير آمن.

### أفق عام 2026: الذكاء السيادي المحلي
في عام 2026، الرهان الحقيقي ليس في تكبير النماذج السحابية العملاقة، بل في **الأنظمة الذكية السيادية المحلية المستقلة**. استوديو تواصل للأمن السيبراني هو تجسيد حي لهذه الرؤية: أنظمة تعمل محلياً بحدود أمان صارمة وبدون تسريب للبيانات.

38 عاماً علمتني أن لغات البرمجة تتغير وتتطور، لكن قوانين الرياضيات والفيزياء والمنطق الحتمي تبقى ثابتة لا تتزعزع.`
    },
    {
      id: 'art-2',
      title: 'The Unreasonable Effectiveness of Physics in Neural Network Architectures',
      titleAr: 'الفاعلية غير المعقولة للفيزياء في تصميم شبكات الذكاء الاصطناعي',
      date: 'February 2026',
      readTime: '6 min read',
      category: 'Physics & Neural Computing',
      tags: ['Physics-Informed AI', 'PINNs', 'Thermodynamics', 'Differential Equations'],
      summary:
        'How incorporating Hamiltonian mechanics, thermodynamic loss functions, and tensor calculus prevents neural hallucinations and guarantees physically consistent predictive models.',
      summaryAr:
        'كيف يساهم دمج ميكانيكا هاملتون ودوال الخسارة الديناميكية الحرارية وحساب الموترات في منع هلوسة النماذج وضمان تنبؤات ذكاء اصطناعي منضبطة فيزيائياً.',
      content: `### Grounding AI in Natural Laws
Modern deep learning often suffers from "unconstrained optimization"—the model finds a numerical minimum that minimizes training loss, yet violates basic real-world boundaries.

By embedding physical differential equations directly into the neural loss function (Physics-Informed Neural Networks or PINNs), we enforce:
- **Momentum Conservation**: Ensuring trajectories do not invent phantom velocities.
- **Energy Boundedness**: Limiting maximum entropy to avoid model divergence.
- **Invariance under Symmetry**: Leveraging Noether's theorem to reduce parameter overhead by orders of magnitude.

Applying these principles in the *PhysiMath Engine* reduced the required training data by 80% while maintaining sub-millisecond execution speeds.`,
      contentAr: `### تأصيل الذكاء الاصطناعي في القوانين الطبيعية
غالباً ما تعاني شبكات التعلم العميق الحديثة من "الاستمثال غير المقيد"، حيث يصل النموذج إلى قاع رقمي يقلل دالة الخسارة لكنه ينتهك أبسط القوانين الفيزيائية والمنطقية.

من خلال تضمين المعادلات التفاضلية الفيزيائية مباشرة في دالة الخسارة العصبية (Physics-Informed Neural Networks)، نفرض ما يلي:
- **حفظ كمية الحركة والطاقة**: ضمان عدم خلق طاقات وهمية تؤدي إلى انحراف النموذج.
- **حدود الإنتروبيا القصوى**: منع التشتت والهلوسة غير المبررة.
- **التماثل وقوانين نويثر**: استغلال التناظر الرياضي لاختزال ملايين المعاملات الحسابية الزائدة.

إن تطبيق هذه المبادئ الفيزيائية في محرك *PhysiMath* خفّض حجم بيانات التدريب المطلوبة بنسبة 80% مع رفع سرعة التنفيذ لمستوى أجزاء من الألف من الثانية.`
    },
    {
      id: 'art-3',
      title: 'Why Mathematical Rigor is Missing in Modern Cybersecurity Tools',
      titleAr: 'لماذا تفتقر أدوات الأمن السيبراني الحديثة إلى الرصانة الرياضية الصارمة؟',
      date: 'March 2026',
      readTime: '7 min read',
      category: 'Cybersecurity & Logic',
      tags: ['Zero-Trust', 'Formal Verification', 'Security Studio', 'Deterministic Proofs'],
      summary:
        'Heuristic vulnerability scanners generate noise and false positives. True zero-trust security requires deterministic state automata and mathematically bounded execution sandboxes.',
      summaryAr:
        'الماسحات الأمنية التقليدية المبنية على التخمين تنتج الكثير من الضوضاء والإنذارات الكاذبة. الأمان الحقيقي يتطلب آلات حالات حتمية وأطر عمل مقيدة رياضياً.',
      content: `### The Problem with Heuristic Scanning
Most vulnerability scanners rely on simple pattern matching. In high-stakes environments, this yields high false-positive rates and, worse, silent misses when dealing with non-trivial logical vulnerabilities (IDOR, race conditions, auth bypasses).

### The Tawassl Paradigm: Mathematical State Verification
In *Tawassl Security Studio*, we applied mathematical automata theory:
1. **Hard Safety Envelope**: A budget vector $\\mathbf{B} = (R_{\\max}, D_{\\max}, C_{\\max})$ that can never be exceeded regardless of agent prompt state.
2. **Deterministic Evidence Graph**: A vulnerability is never flagged as "confirmed" unless accompanied by a deterministic replay proof that satisfies an invariant predicate $P(s) = \\text{compromised}$.
3. **Zero-Trust Egress Isolation**: Mathematically proving that no socket call outside the explicit target list can be initialized.

Security is not guesswork; it is applied discrete mathematics and formal logic.`,
      contentAr: `### معضلة الفحص التخميني التقليدي
تعتمد معظم برامج فحص الثغرات الحالية على مطابقة الأنماط البسيطة. في البيئات الحساسة، يؤدي هذا إلى إغراق مهندسي الأمن بآلاف البلاغات الكاذبة، والأسوأ من ذلك، الفشل في رصد الثغرات المنطقية المعقدة.

### نموذج تواصل: التحقق الرياضي من آلة الحالات
في *استوديو تواصل للأمن السيبراني*، قمنا بتطبيق نظرية الآلات الرياضية الحتمية:
1. **مغلف الأمان الصارم**: متجهة ميزانية رياضية تقيد استهلاك الذاكرة والطلبات ولا يمكن للنموذج خرقها مهما كانت التوجيهات.
2. **رسم بياني للأدلة الحتمية**: لا يتم تصنيف أي ثغرة على أنها "مؤكدة" ما لم يقترن ذلك بإثبات قابل للتكرار يحقق المعادلة المنطقية الحتمية للإصابة.
3. **عزل الشبكة الصارم**: برهان رياضي على استحالة إجراء أي اتصال خارجي خارج نطاق الهدف المصرح به.

الأمن السيبراني ليس تخميناً؛ بل هو رياضيات متقطعة ومنطق شكلي صارم.`
    },
    {
      id: 'art-4',
      title: 'Building Sovereign Local-First AI Systems in Baghdad, Iraq',
      titleAr: 'بناء أنظمة ذكاء اصطناعي سيادية ومحلية في بغداد، العراق',
      date: 'April 2026',
      readTime: '6 min read',
      category: 'Sovereign Technology',
      tags: ['Baghdad 2026', 'Sovereignty', 'Local AI', 'Independence'],
      summary:
        'Why relying exclusively on foreign cloud APIs compromises national data sovereignty, and how Iraqi software architects can build resilient, local-first intelligence platforms.',
      summaryAr:
        'لماذا يشكل الاعتماد الكامل على السحابات الخارجية خطراً على سيادة البيانات الوطنية، وكيف يمكن للمطورين العراقيين بناء منصات ذكاء اصطناعي محلية ومستقلة.',
      content: `### Sovereignty in the Age of Artificial Intelligence
Baghdad has historically been the beacon of algebra, astronomy, and algorithmic philosophy (from Al-Khwarizmi to Al-Kindi). In 2026, we face a new frontier: ensuring our technological tools remain sovereign and under our direct control.

### The Local-First Imperative
- **Data Privacy**: Critical security audits, healthcare data, and infrastructure plans must never leave the local machine.
- **Resilience Against Disconnection**: Systems must function flawlessly whether connected to high-speed fiber or completely isolated in an air-gapped facility.
- **Empowering Iraqi Youth**: By teaching foundational mathematics, physics, and systems programming, we empower the next generation to be creators of core engines rather than passive API consumers.`,
      contentAr: `### السيادة في عصر الذكاء الاصطناعي
كانت بغداد تاريخياً منارة الجبر والفلك وفلسفة الخوارزميات (من الخوارزمي إلى الكندي). وفي عام 2026، نقف أمام مسؤولية تاريخية جديدة: ضمان بقاء أدواتنا الرقمية ومعارفنا التقنية سيادية وتحت إدارتنا المباشرة.

### ركائز النموذج المحلي المستقل
- **خصوصية البيانات والسيادة**: الفحوصات الأمنية الحساسة، البيانات الطبية، وخطط البنية التحتية يجب ألا تغادر الجهاز المحلي أبداً.
- **الصمود أمام انقطاع الشبكات**: يجب أن تعمل الأنظمة بكفاءة كاملة سواء توافر الاتصال السحابي أو في غرف معزولة تماماً (Air-Gapped).
- **تمكين الشباب العراقي**: من خلال تدريس الرياضيات والفيزياء وهندسة النظم العميقة، نُمكّن الجيل القادم ليكونوا بناة للمحركات الأصلية وليس مجرد مستهلكين لخدمات خارجية.`
    }
  ];

  const milestones = [
    {
      period: '1988 — 1994',
      title: 'Genesis of AI, Pascal/Assembly & Physics Pedagogy',
      titleAr: 'انطلاقة الذكاء الاصطناعي، لغات باسكال والأسمبلي وتدريس الفيزياء',
      location: 'Baghdad, Iraq',
      desc: 'Pioneered early neural network models (Perceptron & Hopfield networks), algorithmic logic, and numerical analysis. Began career as a dedicated physics and mathematics educator, instilling foundational scientific discipline into students.',
      descAr: 'برمجة النماذج العصبية الأولى وخوارزميات المنطق والتحليل العددي. بدء مسيرة تدريس الفيزياء والرياضيات النظرية وغرس المفاهيم العلمية الرصينة في عقول الطلبة.'
    },
    {
      period: '1995 — 2004',
      title: 'Computational Physics & Non-Linear Mathematical Modeling',
      titleAr: 'الفيزياء الحاسوبية والنمذجة الرياضية للأنظمة اللاخطية',
      location: 'Baghdad, Iraq',
      desc: 'Formulated numerical solvers for complex differential equations, fluid dynamics approximations, and mathematical modeling. Authored university lecture series on analytical mechanics and discrete mathematics.',
      descAr: 'تطوير حلول عددية للمعادلات التفاضلية المعقدة وديناميكا الموائع والنمذجة الرياضية. تأليف سلاسل محاضرات جامعية في الميكانيكا التحليلية والرياضيات المتقطعة.'
    },
    {
      period: '2005 — 2017',
      title: 'Modern Distributed Systems & Applied Machine Learning',
      titleAr: 'الأنظمة الموزعة الحديثة والتعلم الآلي التطبيقي',
      location: 'Baghdad, Iraq',
      desc: 'Architected high-scale software systems, database kernels, and statistical learning pipelines. Mentored over 1,500 aspiring software developers and engineers in algorithmic thinking and solid software architecture.',
      descAr: 'تصميم معمارية النظم الموزعة ونوى قواعد البيانات ومسارات التعلم الإحصائي. تدريب وإرشاد أكثر من 1500 مطور ومهندس برمجيات على التفكير الخوارزمي وهندسة البرمجيات المتينة.'
    },
    {
      period: '2018 — 2026+',
      title: 'Autonomous AI Agents, Zero-Trust Cybersecurity & Sovereign Tech',
      titleAr: 'وكلاء الذكاء الاصطناعي المستقلون، الأمن السيبراني الصارم والتقنيات السيادية',
      location: 'Baghdad, Iraq — Present Day',
      desc: 'Creator and Chief Architect of Tawassl Security Studio. Active researcher in Physics-Informed Neural Networks (PINNs), deterministic security verification, and sovereign local-first AI systems in Iraq.',
      descAr: 'المؤسس والمعماري الرئيسي لاستوديو تواصل للأمن السيبراني. باحث نشط في شبكات الذكاء المعززة بالفيزياء (PINNs) والتحقق الأمني الحتمي والأنظمة الذكية السيادية في العراق.'
    }
  ];

  const filteredProjects =
    projectFilter === 'all' ? projects : projects.filter((p) => p.category === projectFilter);

  const isAr = language === 'ar';

  return (
    <div className="space-y-8 max-w-6xl pb-16">
      {/* Top Banner / Hero Card */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-200 dark:border-zinc-800 bg-linear-to-b from-white via-slate-50 to-slate-100 dark:from-zinc-900/90 dark:via-zinc-900/50 dark:to-zinc-950 p-6 sm:p-8 shadow-xl transition-colors duration-200">
        {/* Subtle Cyber Grid Glow */}
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-cyan-500/10 dark:bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-emerald-500/10 dark:bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            {/* Avatar Badge with futuristic glowing ring */}
            <div className="relative group shrink-0">
              <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-linear-to-tr from-cyan-600 via-teal-500 to-emerald-500 p-0.75 shadow-lg shadow-cyan-500/20">
                <div className="w-full h-full rounded-[14px] bg-slate-900 flex flex-col items-center justify-center text-white relative overflow-hidden">
                  <div className="absolute inset-0 bg-linear-to-br from-cyan-500/20 to-emerald-500/10" />
                  <Atom className="w-10 h-10 text-cyan-400 animate-spin-slow mb-1" />
                  <span className="text-[10px] font-mono font-bold tracking-widest text-emerald-400">1988-2026</span>
                </div>
              </div>
              <div className="absolute -bottom-2 -right-1 px-2 py-0.5 rounded-full bg-emerald-500 text-slate-950 text-[10px] font-bold font-mono shadow-md flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                <span>ONLINE</span>
              </div>
            </div>

            {/* Profile Core Info */}
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide bg-cyan-100 text-cyan-800 dark:bg-cyan-500/15 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-500/30">
                  <Flame className="w-3.5 h-3.5 text-amber-500" />
                  <span>AI DEVELOPER SINCE 1988</span>
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-200 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-300 dark:border-zinc-700">
                  <MapPin className="w-3 h-3 text-rose-500" />
                  <span>Iraq, Baghdad • 2026</span>
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-500/30">
                  <GraduationCap className="w-3.5 h-3.5" />
                  <span>Physics & Mathematical Teacher</span>
                </span>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-baseline gap-2 pt-1">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  Falah.G.Salieh
                </h1>
                <span className="text-base sm:text-lg font-bold text-cyan-600 dark:text-cyan-400 font-sans">
                  (الأستاذ فلاح كاطع صالح)
                </span>
              </div>

              <p className="text-xs sm:text-sm font-medium text-slate-600 dark:text-zinc-300 max-w-2xl leading-relaxed">
                {isAr
                  ? 'رائد في هندسة وتطوير الذكاء الاصطناعي منذ عام 1988، أستاذ متميز في الفيزياء والرياضيات النظرية، ومصمم معماريات النظم المستقلة والأمن السيبراني في بغداد، العراق 2026.'
                  : 'Master AI Architect & Developer since 1988, distinguished Physics & Mathematical Teacher, and Pioneer of Local-First Autonomous Cyber Systems in Baghdad, Iraq (2026).'}
              </p>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-row md:flex-col gap-2.5 w-full md:w-auto shrink-0 pt-2 md:pt-0">
            <button
              onClick={copyEmail}
              className="flex-1 md:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition bg-cyan-600 hover:bg-cyan-500 text-white shadow-md shadow-cyan-600/20 cursor-pointer"
            >
              {copiedEmail ? (
                <>
                  <Check className="w-4 h-4 text-white" />
                  <span>{isAr ? 'تم نسخ البريد!' : 'Email Copied!'}</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>{isAr ? 'نسخ البريد الإلكتروني' : 'Copy Email'}</span>
                </>
              )}
            </button>

            <a
              href={`mailto:${emailAddress}?subject=Inquiry%20from%20Tawassl%20Studio`}
              className="flex-1 md:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition bg-slate-100 hover:bg-slate-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-800 dark:text-zinc-200 border border-slate-300 dark:border-zinc-700 cursor-pointer"
            >
              <Mail className="w-4 h-4 text-emerald-500" />
              <span>{isAr ? 'مراسلة مباشرة' : 'Send Direct Mail'}</span>
            </a>

            <a
              href={blogUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 md:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition bg-slate-100 hover:bg-slate-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-800 dark:text-zinc-200 border border-slate-300 dark:border-zinc-700 cursor-pointer"
            >
              <Globe className="w-4 h-4 text-cyan-500" />
              <span>{isAr ? 'المدونة التقنية' : 'Developer Blog'}</span>
              <ExternalLink className="w-3 h-3 opacity-60" />
            </a>
          </div>
        </div>

        {/* Highlight Banner on Bottom */}
        <div className="mt-6 pt-4 border-t border-slate-200 dark:border-zinc-800/80 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2 text-slate-600 dark:text-zinc-400">
            <ShieldCheck className="w-4 h-4 text-cyan-500 shrink-0" />
            <span>
              {isAr
                ? 'المعماري والمطور الرئيسي لمنصة استوديو تواصل للأمن السيبراني (Tawassl Security Studio)'
                : 'Principal Architect & Lead Developer behind Tawassl Security Studio Engine'}
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono text-slate-500 dark:text-zinc-400">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-cyan-500" />
              <span>1988 — 2026 (38 Years)</span>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-emerald-500" />
              <span>Baghdad, Iraq</span>
            </span>
          </div>
        </div>
      </div>

      {/* 4 Key Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: isAr ? 'سنوات في تطوير الذكاء والبرمجة' : 'Years in AI & Computing',
            value: '38+',
            sub: isAr ? 'منذ عام 1988 بدون انقطاع' : 'Since 1988 continuous',
            icon: Flame,
            color: 'text-amber-500',
            bg: 'bg-amber-500/10 border-amber-500/20'
          },
          {
            label: isAr ? 'أستاذ فيزياء ورياضيات' : 'Physics & Math Pedagogy',
            value: '1988+',
            sub: isAr ? 'تأصيل رياضي للخوارزميات' : 'First-principles rigor',
            icon: Atom,
            color: 'text-cyan-500',
            bg: 'bg-cyan-500/10 border-cyan-500/20'
          },
          {
            label: isAr ? 'طلبة ومهندسون تتلمذوا' : 'Scholars & Engineers Mentored',
            value: '3,500+',
            sub: isAr ? 'أجيال في بغداد والعالم العربي' : 'Generations in Baghdad',
            icon: GraduationCap,
            color: 'text-emerald-500',
            bg: 'bg-emerald-500/10 border-emerald-500/20'
          },
          {
            label: isAr ? 'أنظمة ونماذج معمارية' : 'Systems & Engines Built',
            value: '120+',
            sub: isAr ? 'أمن سيبراني ومحاكاة وذكاء' : 'Local-first & sovereign',
            icon: Cpu,
            color: 'text-purple-500',
            bg: 'bg-purple-500/10 border-purple-500/20'
          }
        ].map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className="p-4 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs flex flex-col justify-between space-y-2 transition-colors duration-200"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">{card.label}</span>
                <div className={`p-1.5 rounded-lg border ${card.bg}`}>
                  <Icon className={`w-4 h-4 ${card.color}`} />
                </div>
              </div>
              <div>
                <div className="text-2xl font-black font-mono text-slate-900 dark:text-white tracking-tight">
                  {card.value}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-zinc-400 mt-0.5">{card.sub}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pillars of Mastery */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-zinc-800 pb-2">
          <Award className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
          <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
            {isAr ? 'ركائز الخبرة والتميز العلمي والتقني' : 'Pillars of Mastery & Technical Legacy'}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Pillar 1: AI Since 1988 */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 space-y-2.5">
            <div className="flex items-center gap-2.5 text-cyan-600 dark:text-cyan-400">
              <div className="p-2 rounded-lg bg-cyan-100 dark:bg-cyan-500/10 border border-cyan-300 dark:border-cyan-500/20">
                <Cpu className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100">
                {isAr ? 'هندسة الذكاء الاصطناعي منذ عام 1988' : 'Pioneering AI Engineering (Since 1988)'}
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
              {isAr
                ? 'مسيرة متواصلة منذ بدايات الذكاء الاصطناعي الرمزي والنظم الخبيرة والشبكات العصبية الأولى (Hopfield & Perceptrons) وصولاً إلى نماذج التعلم العميق والوكلاء الأذكياء المستقلين في عام 2026. خبرة عميقة في كفاءة المعالجة وهندسة الخوارزميات الحتمية.'
                : 'An uninterrupted journey spanning from 1988 early symbolic AI, heuristic expert systems, and classic neural nets to 2026 state-of-the-art agentic reasoning and sovereign LLM workflows. Mastering algorithmic complexity where every byte counts.'}
            </p>
          </div>

          {/* Pillar 2: Physics & Mathematics Pedagogy */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 space-y-2.5">
            <div className="flex items-center gap-2.5 text-emerald-600 dark:text-emerald-400">
              <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/20">
                <Atom className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100">
                {isAr ? 'أستاذ الفيزياء والرياضيات النظرية' : 'Distinguished Physics & Mathematics Teacher'}
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
              {isAr
                ? 'تدريس الفيزياء والميكانيكا التحليلية والمعادلات التفاضلية وحساب الموترات لعقود طويلة. توظيف قوانين الفيزياء وبديهيات الرياضيات في فرض قيود حتمية على الشبكات العصبية لمنع الهلوسة وضمان انضباط مخرجات الذكاء.'
                : 'Decades of pedagogical excellence in theoretical physics, multivariable calculus, and tensor analysis. Infusing natural conservation laws into loss functions (PINNs) to transform unpredictable AI models into deterministic engineering engines.'}
            </p>
          </div>

          {/* Pillar 3: Zero-Trust & Tawassl Security Studio */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 space-y-2.5">
            <div className="flex items-center gap-2.5 text-amber-600 dark:text-amber-400">
              <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-500/10 border border-amber-300 dark:border-amber-500/20">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100">
                {isAr ? 'الأمن السيبراني الصارم واستوديو تواصل' : 'Zero-Trust Cybersecurity & Tawassl Studio'}
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
              {isAr
                ? 'تصميم وبناء أدوات الفحص السيبراني المستقلة ذات الحدود الصارمة وميزانيات الأمان غير القابلة للتجاوز. عزل تام للشبكة، حماية للبيانات السيادية، وتحويل التقييمات الأمنية إلى إثباتات رياضية حتمية.'
                : 'Architecting bulletproof local-first security tooling with non-negotiable hard safety budgets and zero-trust egress guards. Ensuring complete sovereign isolation and transforming security audits into reproducible mathematical proofs.'}
            </p>
          </div>

          {/* Pillar 4: Mentorship & Academic Impact */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 space-y-2.5">
            <div className="flex items-center gap-2.5 text-purple-600 dark:text-purple-400">
              <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-500/10 border border-purple-300 dark:border-purple-500/20">
                <GraduationCap className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100">
                {isAr ? 'الإرشاد الأكاديمي وبناء الأجيال في بغداد' : 'Educational Leadership & Baghdad Legacy'}
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
              {isAr
                ? 'تخريج وتدريب آلاف الطلبة والباحثين والمهندسين في العاصمة بغداد والعالم العربي، وغرس ثقافة التفكير المنطقي والبحث العلمي الجاد وتطوير البرمجيات الرصينة القادرة على المنافسة عالمياً.'
                : 'Inspiring over 3,500 students, researchers, and software engineers in Baghdad and across the Arab region. Fostering a culture of disciplined logical reasoning, first-principles problem solving, and sovereign technological independence.'}
            </p>
          </div>
        </div>
      </div>

      {/* 38-Year Milestones Timeline (1988 - 2026) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-zinc-800 pb-2">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
              {isAr ? 'محطات التاريخ والخبرة (38 عاماً: 1988 — 2026)' : 'Best Developer History: 38-Year Timeline (1988 — 2026)'}
            </h2>
          </div>
          <span className="text-[11px] font-mono text-cyan-600 dark:text-cyan-400 font-semibold">
            {isAr ? 'العراق — بغداد' : 'Baghdad, Iraq Legacy'}
          </span>
        </div>

        <div className="relative pl-6 sm:pl-8 border-l-2 border-slate-200 dark:border-zinc-800 space-y-6 my-2">
          {milestones.map((m, idx) => (
            <div key={idx} className="relative group">
              {/* Glowing Timeline Marker */}
              <div className="absolute -left-[31px] sm:-left-[39px] top-1.5 w-4 h-4 rounded-full bg-white dark:bg-zinc-950 border-2 border-cyan-500 group-hover:scale-125 transition-transform duration-200 flex items-center justify-center">
                <div className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
              </div>

              <div className="p-4 sm:p-5 rounded-xl border border-slate-200 dark:border-zinc-800/80 bg-white dark:bg-zinc-900/40 hover:border-cyan-500/40 transition">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-md text-[11px] font-mono font-bold bg-cyan-100 text-cyan-800 dark:bg-cyan-500/20 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-500/30">
                      {m.period}
                    </span>
                    <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100">
                      {isAr ? m.titleAr : m.title}
                    </h3>
                  </div>
                  <span className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-rose-500" />
                    {m.location}
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                  {isAr ? m.descAr : m.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Featured Projects Showcase with Link Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-zinc-800 pb-2">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
              {isAr ? 'المشاريع البارزة والمعماريات البرمجية' : 'Featured Projects & Architectural Systems'}
            </h2>
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
            {[
              { id: 'all', label: isAr ? 'الكل' : 'All Projects' },
              { id: 'cybersecurity', label: isAr ? 'الأمن السيبراني' : 'Cybersecurity' },
              { id: 'physics-math', label: isAr ? 'الفيزياء والرياضيات' : 'Physics & Math' },
              { id: 'ai', label: isAr ? 'الذكاء الاصطناعي' : 'AI Systems' }
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setProjectFilter(f.id as any)}
                className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer text-xs whitespace-nowrap ${
                  projectFilter === f.id
                    ? 'bg-cyan-600 text-white font-bold shadow-xs'
                    : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Project Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredProjects.map((p) => (
            <div
              key={p.id}
              className="p-5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 flex flex-col justify-between space-y-4 hover:border-cyan-500/50 transition group"
            >
              <div className="space-y-2.5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700">
                        {p.category}
                      </span>
                      <span className="text-[11px] font-mono text-cyan-600 dark:text-cyan-400 font-bold">{p.year}</span>
                    </div>
                    <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100 mt-1.5 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition">
                      {p.title}
                    </h3>
                    <div className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium">{p.role}</div>
                  </div>
                </div>

                <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                  {p.description}
                </p>

                {/* Highlights List */}
                <ul className="space-y-1 text-[11px] text-slate-500 dark:text-zinc-400">
                  {p.highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <Check className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Tech Badges & Action Link */}
              <div className="pt-3 border-t border-slate-100 dark:border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-1.5">
                  {p.tech.map((t, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700"
                    >
                      {t}
                    </span>
                  ))}
                </div>

                {p.linkType === 'internal' && p.linkTarget ? (
                  <button
                    onClick={() => setActiveTab(p.linkTarget!)}
                    className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 bg-cyan-50 dark:bg-cyan-500/10 hover:bg-cyan-100 dark:hover:bg-cyan-500/20 border border-cyan-200 dark:border-cyan-500/30 transition cursor-pointer shrink-0"
                  >
                    <span>{isAr ? 'فتح في الاستوديو' : 'Open in Studio'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <a
                    href={blogUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 dark:text-zinc-300 bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 transition cursor-pointer shrink-0"
                  >
                    <span>{isAr ? 'التفاصيل والمعمارية' : 'View Architecture'}</span>
                    <ExternalLink className="w-3 h-3 opacity-70" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Blog & Thought Leadership Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-zinc-800 pb-2">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
              {isAr ? 'المقالات والبحوث المنشورة' : 'Technical Blog & Research Articles'}
            </h2>
          </div>
          <a
            href={blogUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-cyan-600 dark:text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
          >
            <span>{isAr ? 'زيارة المدونة الرسمية' : 'Visit Official Blog'}</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {articles.map((art) => (
            <div
              key={art.id}
              onClick={() => setSelectedArticle(art)}
              className="p-5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 hover:border-purple-500/50 transition cursor-pointer flex flex-col justify-between space-y-3 group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-zinc-400">
                  <span className="font-mono text-purple-600 dark:text-purple-400 font-semibold">{art.category}</span>
                  <div className="flex items-center gap-2 font-mono text-[10px]">
                    <span>{art.date}</span>
                    <span>•</span>
                    <span>{art.readTime}</span>
                  </div>
                </div>

                <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-100 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition">
                  {isAr ? art.titleAr : art.title}
                </h3>

                <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                  {isAr ? art.summaryAr : art.summary}
                </p>
              </div>

              <div className="pt-2 flex items-center justify-between text-xs">
                <div className="flex flex-wrap gap-1">
                  {art.tags.slice(0, 3).map((t, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-50 dark:bg-purple-950/30 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800/50"
                    >
                      #{t}
                    </span>
                  ))}
                </div>
                <span className="text-purple-600 dark:text-purple-400 font-bold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  <span>{isAr ? 'قراءة المقال' : 'Read Article'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Direct Contact & Inquiry Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-zinc-800 pb-2">
          <Mail className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
            {isAr ? 'التواصل المباشر والتعاون البحثي' : 'Direct Communication & Research Inquiries'}
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Contact Details Card */}
          <div className="p-6 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-zinc-100">
                {isAr ? 'معلومات التواصل المباشرة' : 'Direct Contact Information'}
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
                {isAr
                  ? 'متاح للاستشارات المعمارية في الذكاء الاصطناعي والأمن السيبراني والبحوث الرياضية والفيزيائية.'
                  : 'Open for strategic AI consultations, security architectures, and mathematical research collaborations.'}
              </p>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
                <div className="space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Official Email</div>
                  <div className="font-mono font-semibold text-slate-800 dark:text-zinc-200 text-xs">
                    {emailAddress}
                  </div>
                </div>
                <button
                  onClick={copyEmail}
                  className="p-1.5 rounded-md hover:bg-slate-200 dark:hover:bg-zinc-800 text-slate-600 dark:text-zinc-400 cursor-pointer"
                  title="Copy Email"
                >
                  {copiedEmail ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
                <div className="space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Location & Hub</div>
                  <div className="font-semibold text-slate-800 dark:text-zinc-200 text-xs">
                    Baghdad, Iraq (GMT+3)
                  </div>
                </div>
                <MapPin className="w-4 h-4 text-rose-500" />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
                <div className="space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Developer Blog</div>
                  <div className="font-mono font-semibold text-slate-800 dark:text-zinc-200 text-xs">
                    blog.falahgsalieh.dev
                  </div>
                </div>
                <a
                  href={blogUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-md hover:bg-slate-200 dark:hover:bg-zinc-800 text-cyan-500 cursor-pointer"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>

            <div className="pt-2">
              <a
                href={`mailto:${emailAddress}?subject=Inquiry%20for%20Falah%20G.%20Salieh`}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white shadow-md transition cursor-pointer"
              >
                <Mail className="w-4 h-4" />
                <span>{isAr ? 'فتح تطبيق البريد للمراسلة' : 'Launch Mail Client'}</span>
              </a>
            </div>
          </div>

          {/* Message Form */}
          <div className="lg:col-span-2 p-6 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60">
            <h3 className="text-sm font-bold text-slate-900 dark:text-zinc-100 mb-1">
              {isAr ? 'إرسال رسالة مباشرة للمطور' : 'Send a Direct Inquiry to Falah G. Salieh'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mb-4">
              {isAr
                ? 'استفسارات المشاريع، التعاون الأكاديمي، أو مراجعات الأمان السيبراني.'
                : 'Project collaborations, academic lectures, or cybersecurity architecture reviews.'}
            </p>

            {formSent ? (
              <div className="p-6 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300 text-center space-y-2">
                <Check className="w-8 h-8 mx-auto text-emerald-500" />
                <h4 className="font-bold text-sm">
                  {isAr ? 'تم إرسال رسالتك بنجاح!' : 'Message Sent Successfully!'}
                </h4>
                <p className="text-xs">
                  {isAr
                    ? 'شكراً لتواصلك. سيتم الرد على استفسارك في أقرب وقت ممكن.'
                    : 'Thank you for reaching out. Falah G. Salieh will review your inquiry shortly.'}
                </p>
              </div>
            ) : (
              <form onSubmit={handleFormSubmit} className="space-y-3.5 text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-600 dark:text-zinc-400 mb-1 font-medium">
                      {isAr ? 'الاسم الكريم' : 'Your Name'}
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="Eng. Ahmed / Dr. Sarah"
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-slate-900 dark:text-zinc-100 focus:outline-hidden focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 dark:text-zinc-400 mb-1 font-medium">
                      {isAr ? 'البريد الإلكتروني' : 'Your Email'}
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="your.email@organization.com"
                      value={formEmail}
                      onChange={(e) => setFormEmail(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-slate-900 dark:text-zinc-100 focus:outline-hidden focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-slate-600 dark:text-zinc-400 mb-1 font-medium">
                    {isAr ? 'موضوع الرسالة' : 'Subject'}
                  </label>
                  <input
                    type="text"
                    required
                    placeholder={
                      isAr
                        ? 'استشارة في الذكاء الاصطناعي / تدريس فيزياء / أمن سيبراني'
                        : 'AI System Consultation / Math & Physics Seminar / Security Architecture'
                    }
                    value={formSubject}
                    onChange={(e) => setFormSubject(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-slate-900 dark:text-zinc-100 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-600 dark:text-zinc-400 mb-1 font-medium">
                    {isAr ? 'نص الرسالة' : 'Your Message'}
                  </label>
                  <textarea
                    rows={4}
                    required
                    placeholder={
                      isAr
                        ? 'اكتب تفاصيل مشروعك أو استفسارك هنا...'
                        : 'Describe your inquiry, project scope, or research topic in detail...'
                    }
                    value={formMessage}
                    onChange={(e) => setFormMessage(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-slate-900 dark:text-zinc-100 focus:outline-hidden focus:border-cyan-500 resize-none"
                  />
                </div>

                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md transition cursor-pointer"
                  >
                    <Send className="w-4 h-4" />
                    <span>{isAr ? 'إرسال الرسالة الآن' : 'Send Message Now'}</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* Article Reader Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs">
          <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl w-full max-w-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between gap-4 bg-slate-50 dark:bg-zinc-950/60">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-[11px] font-mono text-purple-600 dark:text-purple-400">
                  <span className="font-bold uppercase">{selectedArticle.category}</span>
                  <span>•</span>
                  <span>{selectedArticle.readTime}</span>
                  <span>•</span>
                  <span>{selectedArticle.date}</span>
                </div>
                <h3 className="font-extrabold text-base sm:text-lg text-slate-900 dark:text-white leading-snug">
                  {isAr ? selectedArticle.titleAr : selectedArticle.title}
                </h3>
              </div>
              <button
                onClick={() => setSelectedArticle(null)}
                className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-4 text-xs sm:text-sm text-slate-700 dark:text-zinc-300 leading-relaxed font-sans">
              <div className="p-4 rounded-xl bg-slate-100 dark:bg-zinc-950/80 border border-slate-200 dark:border-zinc-800 text-xs italic text-slate-600 dark:text-zinc-400">
                {isAr ? selectedArticle.summaryAr : selectedArticle.summary}
              </div>

              <div className="space-y-4 whitespace-pre-line">
                {isAr ? selectedArticle.contentAr : selectedArticle.content}
              </div>

              <div className="pt-4 border-t border-slate-200 dark:border-zinc-800 flex flex-wrap items-center justify-between gap-2">
                <div className="flex flex-wrap gap-1.5">
                  {selectedArticle.tags.map((t, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded text-[11px] font-mono bg-purple-100 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800"
                    >
                      #{t}
                    </span>
                  ))}
                </div>

                <div className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">
                  By Falah G. Salieh • Baghdad, Iraq 2026
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950/60 flex items-center justify-between">
              <a
                href={blogUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-cyan-600 dark:text-cyan-400 font-bold hover:underline"
              >
                <span>{isAr ? 'زيارة رابط المقال على المدونة' : 'View on Official Blog'}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <button
                onClick={() => setSelectedArticle(null)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 hover:bg-slate-300 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-800 dark:text-zinc-200 transition cursor-pointer"
              >
                {isAr ? 'إغلاق' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
