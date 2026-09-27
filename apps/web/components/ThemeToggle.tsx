'use client';

import React from 'react';
import { useStudio } from '../lib/context';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, setTheme, language } = useStudio();
  const isDark = theme === 'dark';

  return (
    <div
      role="switch"
      aria-checked={isDark}
      aria-label="Toggle dark/light theme"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          setTheme(isDark ? 'light' : 'dark');
        }
      }}
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="relative flex items-center p-1 rounded-full cursor-pointer transition-colors duration-300 select-none bg-zinc-200 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 w-16 h-8 shadow-inner"
      title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
    >
      {/* Sliding Pill Indicator */}
      <div
        className={`absolute top-1 bottom-1 w-6 rounded-full bg-white dark:bg-cyan-500 shadow-md transition-all duration-300 ease-out flex items-center justify-center ${
          language === 'ar'
            ? isDark
              ? 'translate-x-0 bg-cyan-500'
              : '-translate-x-8 bg-amber-400'
            : isDark
            ? 'translate-x-8 bg-cyan-500'
            : 'translate-x-0 bg-amber-400'
        }`}
      >
        {isDark ? (
          <Moon className="w-3.5 h-3.5 text-zinc-950 fill-current" />
        ) : (
          <Sun className="w-3.5 h-3.5 text-zinc-950 fill-current" />
        )}
      </div>

      {/* Background Icons */}
      <div className="flex justify-between items-center w-full px-1.5 text-xs text-zinc-400 pointer-events-none">
        <Sun className={`w-3.5 h-3.5 transition-opacity ${!isDark ? 'opacity-0' : 'opacity-70 text-amber-500'}`} />
        <Moon className={`w-3.5 h-3.5 transition-opacity ${isDark ? 'opacity-0' : 'opacity-70 text-zinc-500'}`} />
      </div>
    </div>
  );
}
