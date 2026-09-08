'use client';
interface Props { score: number; showLabel?: boolean; }
export default function ScoreBar({ score, showLabel = true }: Props) {
  const color = score >= 80 ? 'from-emerald-500 to-emerald-400' : score >= 60 ? 'from-blue-500 to-blue-400' : score >= 40 ? 'from-amber-500 to-amber-400' : 'from-red-500 to-red-400';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-[5px] bg-[var(--color-surface-alt)] rounded-full overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${color} rounded-full transition-all duration-700`} style={{ width: `${Math.min(score, 100)}%` }} />
      </div>
      {showLabel && <span className="text-[11px] font-bold text-[var(--color-text)] tabular-nums w-8 text-right">{score}%</span>}
    </div>
  );
}
