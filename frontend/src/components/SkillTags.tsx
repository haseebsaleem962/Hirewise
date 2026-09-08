'use client';
interface Props { skills: string[]; max?: number; }
export default function SkillTags({ skills, max }: Props) {
  if (!skills || skills.length === 0) return <span className="text-[11px] text-[var(--color-text-muted)]">—</span>;
  const show = max ? skills.slice(0, max) : skills;
  const rest = max ? skills.length - max : 0;
  return (
    <div className="flex flex-wrap gap-1">
      {show.map((s, i) => (
        <span key={i} className="inline-flex items-center px-2 py-0.5 rounded-md bg-[var(--color-primary-soft)] text-[var(--color-primary)] text-[10px] font-semibold">{s}</span>
      ))}
      {rest > 0 && <span className="px-2 py-0.5 rounded-md bg-[var(--color-surface-alt)] text-[var(--color-text-muted)] text-[10px] font-medium">+{rest}</span>}
    </div>
  );
}
