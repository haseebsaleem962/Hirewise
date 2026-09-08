'use client';
import { ReactNode } from 'react';
interface Props { title: string; value: string | number; icon: ReactNode; color?: string; subtitle?: string; }
export default function StatCard({ title, value, icon, subtitle }: Props) {
  return (
    <div className="card p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider">{title}</p>
        {icon}
      </div>
      <p className="text-[28px] font-extrabold text-[var(--color-text)] leading-none tracking-tight">{value}</p>
      {subtitle && <p className="text-[11px] text-[var(--color-text-muted)]">{subtitle}</p>}
    </div>
  );
}
