'use client';

import { useBlindMode } from '@/context/BlindModeContext';
import { EyeOff, Eye, Moon, Sun, Menu } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Navbar({ onMenuClick }: { onMenuClick: () => void }) {
  const { blindMode, toggleBlindMode } = useBlindMode();
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  return (
    <header className="h-[60px] bg-[var(--color-surface)] border-b border-[var(--color-border)] flex items-center justify-between px-4 sm:px-6 lg:px-8 shrink-0">
      <button
        onClick={onMenuClick}
        className="lg:hidden w-9 h-9 flex items-center justify-center rounded-[10px] bg-[var(--color-surface-alt)] text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-[var(--color-border)] transition-all"
        aria-label="Open navigation menu"
      >
        <Menu size={17} />
      </button>
      <div className="flex items-center gap-2">
        <button
          onClick={toggleBlindMode}
          className={`flex items-center gap-2 px-4 py-[7px] rounded-[10px] text-[12px] font-semibold transition-all duration-200 ${
            blindMode
              ? 'bg-amber-500 text-white shadow-md shadow-amber-500/20 hover:bg-amber-600'
              : 'bg-[var(--color-surface-alt)] text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-[var(--color-border)]'
          }`}
        >
          {blindMode ? <EyeOff size={14} /> : <Eye size={14} />}
          {blindMode ? 'Blind Mode ON' : 'Blind Mode'}
        </button>

        <button
          onClick={() => setDarkMode(!darkMode)}
          className="w-9 h-9 flex items-center justify-center rounded-[10px] bg-[var(--color-surface-alt)] text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-[var(--color-border)] transition-all"
        >
          {darkMode ? <Sun size={15} /> : <Moon size={15} />}
        </button>
      </div>
    </header>
  );
}
