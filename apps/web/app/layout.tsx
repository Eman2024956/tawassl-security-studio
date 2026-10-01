import type { Metadata, Viewport } from "next";
import "./globals.css";

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#090d16" },
    { media: "(prefers-color-scheme: light)", color: "#06b6d4" },
  ],
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  metadataBase: new URL("https://scopeguard-seven-black.vercel.app"),
  title: {
    default: "ScopeGuard Security Studio | استوديو سكوپ غارد للأمن السيبراني - Falah G. Salieh",
    template: "%s | ScopeGuard Security Studio",
  },
  description:
    "Local-First AI Security & Bug Bounty Exploration Workspace with Zero-Trust Egress Guard, Hard Safety Budgets, and Deterministic Evidence Verification. Architected by Falah G. Salieh (AI Developer Since 1988 & Physics/Math Educator) in Baghdad, Iraq (2026). بيئة عمل محلية مدعومة بالذكاء الاصطناعي لفحص الثغرات الأمنية والأخطاء البرمجية - تطوير الأستاذ فلاح كاطع صالح.",
  applicationName: "ScopeGuard Security Studio",
  authors: [
    {
      name: "Falah G. Salieh (الأستاذ فلاح كاطع صالح)",
      url: "https://blog.falahgsalieh.dev",
    },
  ],
  generator: "Next.js",
  keywords: [
    "ScopeGuard",
    "ScopeGuard Security Studio",
    "Tawassl Security Studio",
    "Falah G. Salieh",
    "فلاح كاطع صالح",
    "AI Developer Since 1988",
    "مطور ذكاء اصطناعي منذ 1988",
    "Physics and Mathematics Teacher",
    "أستاذ الفيزياء والرياضيات",
    "Baghdad Iraq 2026",
    "بغداد العراق",
    "Local-First AI Security",
    "Bug Bounty Studio",
    "Zero-Trust Sandbox",
    "Deterministic Evidence Verification",
    "SARIF 2.1.0",
    "Cyber Defense Iraq",
  ],
  creator: "Falah G. Salieh (AI Developer Since 1988)",
  publisher: "ScopeGuard Labs • Baghdad, Iraq",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "https://scopeguard-seven-black.vercel.app",
    languages: {
      "en-US": "https://scopeguard-seven-black.vercel.app",
      "ar-IQ": "https://scopeguard-seven-black.vercel.app",
    },
  },
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  manifest: "/site.webmanifest",
  openGraph: {
    type: "website",
    locale: "en_US",
    alternateLocale: ["ar_IQ"],
    url: "https://scopeguard-seven-black.vercel.app",
    siteName: "ScopeGuard Security Studio | استوديو سكوپ غارد للأمن السيبراني",
    title: "ScopeGuard Security Studio | Local-First AI Security - Falah G. Salieh (1988-2026)",
    description:
      "Autonomous Local-First AI Security & Bug Bounty Exploration Workspace. Zero-Trust Egress Guard, Hard Safety Budgets & Mathematical Verification. Created by Falah G. Salieh (AI Developer Since 1988 | Physics & Mathematical Teacher) - Baghdad, Iraq 2026.",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "ScopeGuard Security Studio - Architected by Falah G. Salieh (AI Developer Since 1988, Baghdad, Iraq 2026)",
      },
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "ScopeGuard Security Studio Preview Card",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "ScopeGuard Security Studio | Falah G. Salieh (AI Developer Since 1988)",
    description:
      "Local-First AI Security & Bug Bounty Studio. Zero-Trust Sandbox & Hard Safety Budgets. Developed by Falah G. Salieh in Baghdad, Iraq (2026). استوديو سكوپ غارد للأمن السيبراني.",
    images: ["/og-image.jpg"],
    creator: "@falahgsalieh",
    site: "@scopeguard_sec",
  },
  category: "Cybersecurity & Artificial Intelligence",
  other: {
    "developer:name": "Falah G. Salieh",
    "developer:name_ar": "فلاح كاطع صالح",
    "developer:experience": "AI Developer Since 1988 (38+ Years)",
    "developer:role": "Senior AI Architect & Physics/Mathematical Teacher",
    "developer:location": "Baghdad, Iraq (2026)",
    "developer:email": "falah.g.salieh@gmail.com",
    "developer:blog": "https://blog.falahgsalieh.dev",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="alternate icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="author" content="Falah G. Salieh (فلاح كاطع صالح)" />
        <meta name="geo.region" content="IQ-BG" />
        <meta name="geo.placename" content="Baghdad" />
      </head>
      <body className="bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-zinc-100 min-h-screen antialiased selection:bg-cyan-500/30 selection:text-cyan-800 dark:selection:text-cyan-200 transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
