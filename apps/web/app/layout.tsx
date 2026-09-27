import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tawassl Security Studio | استوديو تواصل للأمن السيبراني",
  description: "Local-first AI workspace for discovering, investigating, and documenting functional bugs and security vulnerabilities in user-authorized targets.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 min-h-screen antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
