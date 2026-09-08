'use client';

import { useEffect, useState } from 'react';
import { Users, CheckCircle2, XCircle, Clock, TrendingUp, BarChart3, User } from 'lucide-react';
import ScoreBar from '@/components/ScoreBar';
import api from '@/lib/api';

interface Stats { total_candidates: number; total_criteria: number; shortlisted: number; rejected: number; selected: number; on_hold: number; pending: number; avg_match_score: number; category_breakdown: Record<string, number>; status_breakdown: Record<string, number>; }
interface Recent { id: number; name: string; resume_category: string; match_score: number; final_status: string; }

const statConfig = [
  { key: 'total_candidates', label: 'Total Candidates', icon: Users, color: 'text-indigo-600', bg: 'bg-indigo-50', ring: 'ring-indigo-100' },
  { key: 'shortlisted', label: 'Shortlisted', icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50', ring: 'ring-emerald-100' },
  { key: 'rejected', label: 'Rejected', icon: XCircle, color: 'text-red-500', bg: 'bg-red-50', ring: 'ring-red-100' },
  { key: 'selected', label: 'Selected', icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50', ring: 'ring-blue-100' },
  { key: 'on_hold', label: 'On Hold', icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50', ring: 'ring-amber-100' },
  { key: 'avg_match_score', label: 'Avg Score', icon: BarChart3, color: 'text-violet-600', bg: 'bg-violet-50', ring: 'ring-violet-100', format: true },
];

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recent, setRecent] = useState<Recent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/dashboard/stats'), api.get('/dashboard/recent')])
      .then(([s, r]) => { setStats(s.data); setRecent(r.data.candidates || []); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-7 h-7 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
    </div>
  );
  if (!stats) return <p className="text-center text-[var(--color-text-muted)] py-20">Failed to load</p>;

  return (
    <div className="max-w-[1400px] mx-auto space-y-8">
      <div>
        <h1 className="text-[26px] font-extrabold text-[var(--color-text)] tracking-tight leading-none">Dashboard</h1>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">Overview of your hiring pipeline</p>
      </div>

      {/* Stat Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {statConfig.map(({ key, label, icon: Icon, color, bg, ring, format }) => {
          const val = (stats as unknown as Record<string, unknown>)[key] as number;
          return (
            <div key={key} className="card p-5 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <p className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider">{label}</p>
                <div className={`w-8 h-8 rounded-lg ${bg} ring-1 ${ring} flex items-center justify-center`}>
                  <Icon size={15} className={color} />
                </div>
              </div>
              <p className="text-[30px] font-extrabold text-[var(--color-text)] leading-none tracking-tight">
                {format ? `${Math.round(val)}%` : val}
              </p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Category Distribution - 3 cols */}
        <div className="card p-6 lg:col-span-3">
          <h3 className="text-[14px] font-bold text-[var(--color-text)] mb-5">Category Distribution</h3>
          {Object.keys(stats.category_breakdown).length > 0 ? (
            <div className="space-y-3.5">
              {Object.entries(stats.category_breakdown).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([cat, count]) => (
                <div key={cat} className="flex items-center gap-3">
                  <span className="text-[12px] font-medium text-[var(--color-text-secondary)] w-36 truncate shrink-0">{cat}</span>
                  <div className="flex-1 h-[6px] bg-[var(--color-surface-alt)] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-700"
                      style={{ width: `${(count / stats.total_candidates) * 100}%` }}
                    />
                  </div>
                  <span className="text-[12px] font-bold text-[var(--color-text)] tabular-nums w-7 text-right">{count}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-12 text-[13px] text-[var(--color-text-muted)]">
              No data yet — upload resumes to see categories
            </div>
          )}
        </div>

        {/* Recent Uploads - 2 cols */}
        <div className="card p-6 lg:col-span-2">
          <h3 className="text-[14px] font-bold text-[var(--color-text)] mb-5">Recent Uploads</h3>
          {recent.length > 0 ? (
            <div className="space-y-3">
              {recent.slice(0, 6).map((c) => (
                <div key={c.id} className="flex items-center justify-between py-2.5 border-b border-[var(--color-border-light)] last:border-0">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-[var(--color-primary-soft)] flex items-center justify-center shrink-0">
                      <User size={14} className="text-[var(--color-primary)]" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[12px] font-semibold text-[var(--color-text)] truncate">{c.name || 'Unknown'}</p>
                      <p className="text-[10px] text-[var(--color-text-muted)]">{c.resume_category}</p>
                    </div>
                  </div>
                  <div className="w-20 shrink-0">
                    <ScoreBar score={Math.round(c.match_score)} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-12 text-[13px] text-[var(--color-text-muted)]">
              No candidates uploaded yet
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
