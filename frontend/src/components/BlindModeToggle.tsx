'use client';
import { useBlindMode } from '@/context/BlindModeContext';
import { EyeOff, Eye } from 'lucide-react';
export default function BlindModeToggle() {
  const { blindMode, toggleBlindMode } = useBlindMode();
  return (
    <button onClick={toggleBlindMode} className={`flex items-center gap-2 px-5 py-2.5 rounded-[var(--radius-btn)] text-[12px] font-semibold transition-all ${
      blindMode ? 'bg-amber-500 text-white shadow-md shadow-amber-500/20 hover:bg-amber-600' : 'bg-[var(--color-surface-alt)] text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-[var(--color-border)]'
    }`}>
      {blindMode ? <EyeOff size={14} /> : <Eye size={14} />}
      Blind Mode {blindMode ? 'ON' : 'OFF'}
    </button>
  );
}
