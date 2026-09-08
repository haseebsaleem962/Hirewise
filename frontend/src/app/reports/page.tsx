'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { BarChart3, PieChart, Cpu } from 'lucide-react';

interface Stats { total_candidates: number; shortlisted: number; rejected: number; selected: number; on_hold: number; pending: number; avg_match_score: number; category_breakdown: Record<string, number>; }

export default function ReportsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [model, setModel] = useState<{ model_type: string; accuracy: number; train_samples: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/dashboard/stats'), api.get('/ml/model-status').catch(() => ({ data: null }))])
      .then(([s, m]) => { setStats(s.data); setModel(m.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-20"><div className="w-7 h-7 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin" /></div>;
  if (!stats) return <p className="text-center py-20 text-[13px] text-[var(--color-text-muted)]">Failed to load</p>;

  const pie = [
    { label: 'Shortlisted', value: stats.shortlisted, color: '#059669' },
    { label: 'Selected', value: stats.selected, color: '#6366f1' },
    { label: 'Rejected', value: stats.rejected, color: '#dc2626' },
    { label: 'On Hold', value: stats.on_hold, color: '#d97706' },
    { label: 'Pending', value: stats.pending, color: '#94a3b8' },
  ].filter((d) => d.value > 0);
  const total = pie.reduce((a, d) => a + d.value, 0);
  const cats = Object.entries(stats.category_breakdown).sort((a, b) => b[1] - a[1]);

  return (
    <div className="max-w-[1200px] mx-auto space-y-8">
      <div>
        <h1 className="text-[26px] font-extrabold text-[var(--color-text)] tracking-tight">Analytics</h1>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">Insights into your hiring pipeline</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-5"><PieChart size={16} className="text-[var(--color-primary)]" /><h3 className="text-[14px] font-bold text-[var(--color-text)]">Status Distribution</h3></div>
          {total > 0 ? (
            <div className="space-y-3">
              {pie.map((d) => (
                <div key={d.label} className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: d.color }} />
                  <span className="text-[12px] font-medium text-[var(--color-text-secondary)] w-24">{d.label}</span>
                  <div className="flex-1 h-[6px] bg-[var(--color-surface-alt)] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700" style={{ width: `${(d.value / total) * 100}%`, backgroundColor: d.color }} />
                  </div>
                  <span className="text-[12px] font-bold text-[var(--color-text)] tabular-nums w-7 text-right">{d.value}</span>
                </div>
              ))}
            </div>
          ) : <p className="text-[13px] text-[var(--color-text-muted)] text-center py-10">No data</p>}
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-2 mb-5"><BarChart3 size={16} className="text-[var(--color-primary)]" /><h3 className="text-[14px] font-bold text-[var(--color-text)]">Category Breakdown</h3></div>
          {cats.length > 0 ? (
            <div className="space-y-3">
              {cats.map(([cat, count]) => (
                <div key={cat} className="flex items-center gap-3">
                  <span className="text-[12px] font-medium text-[var(--color-text-secondary)] w-28 truncate">{cat}</span>
                  <div className="flex-1 h-6 bg-[var(--color-surface-alt)] rounded-lg overflow-hidden relative">
                    <div className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-lg" style={{ width: `${(count / stats.total_candidates) * 100}%` }} />
                    <span className="absolute inset-0 flex items-center justify-end pr-2 text-[10px] font-bold text-white">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="text-[13px] text-[var(--color-text-muted)] text-center py-10">No data</p>}
        </div>

        {model && (
          <div className="card p-6 lg:col-span-2">
            <div className="flex items-center gap-2 mb-5"><Cpu size={16} className="text-[var(--color-primary)]" /><h3 className="text-[14px] font-bold text-[var(--color-text)]">ML Model</h3></div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-5 rounded-[var(--radius-card)] bg-[var(--color-surface-alt)]">
                <p className="text-[18px] font-extrabold text-[var(--color-text)]">{model.model_type || 'N/A'}</p>
                <p className="label mt-2">Model</p>
              </div>
              <div className="text-center p-5 rounded-[var(--radius-card)] bg-[var(--color-success-soft)]">
                <p className="text-[18px] font-extrabold text-[var(--color-success)]">{(model.accuracy * 100).toFixed(1)}%</p>
                <p className="label mt-2">Accuracy</p>
              </div>
              <div className="text-center p-5 rounded-[var(--radius-card)] bg-[var(--color-surface-alt)]">
                <p className="text-[18px] font-extrabold text-[var(--color-text)]">{model.train_samples}</p>
                <p className="label mt-2">Samples</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
