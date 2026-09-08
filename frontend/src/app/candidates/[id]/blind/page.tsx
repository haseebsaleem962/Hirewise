'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Candidate, parseSkills } from '@/types';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import ScoreBar from '@/components/ScoreBar';
import StatusBadge from '@/components/StatusBadge';
import SkillTags from '@/components/SkillTags';
import { ArrowLeft, EyeOff, Shield, CheckCircle2, XCircle, Briefcase } from 'lucide-react';

export default function BlindReview() {
  const { id } = useParams();
  const router = useRouter();
  const [c, setC] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { api.get(`/candidates/${id}/blind`).then((r) => setC(r.data.candidate)).catch(() => {}).finally(() => setLoading(false)); }, [id]);

  const update = async (status: string) => {
    try { await api.put(`/candidates/${id}/status`, { status }); toast.success(`Candidate ${status}`); setC((p) => p ? { ...p, final_status: status } : p); } catch { toast.error('Failed'); }
  };

  if (loading) return <div className="flex justify-center py-20"><div className="w-7 h-7 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin" /></div>;
  if (!c) return <p className="text-center py-20 text-[13px] text-[var(--color-text-muted)]">Candidate not found</p>;

  return (
    <div className="max-w-[900px] mx-auto space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-[12px] font-semibold text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors">
        <ArrowLeft size={14} /> Back
      </button>

      {/* Banner */}
      <div className="rounded-[var(--radius-card)] bg-gradient-to-r from-amber-500 to-orange-500 p-5 flex items-center gap-3 shadow-lg shadow-amber-500/20">
        <Shield size={22} className="text-white" />
        <div>
          <p className="text-[14px] font-bold text-white">Blind Review Mode</p>
          <p className="text-[12px] text-white/80">All personally identifiable information is hidden for unbiased evaluation</p>
        </div>
      </div>

      {/* Candidate */}
      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center">
              <EyeOff size={22} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <h1 className="text-[20px] font-extrabold text-[var(--color-text)]">Anonymous Candidate #{c.id}</h1>
              <p className="text-[13px] text-[var(--color-text-muted)] mt-0.5">Identity hidden for fair evaluation</p>
            </div>
          </div>
          <StatusBadge status={c.final_status} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
          {['Name', 'Gender', 'Location', 'Institute'].map((l) => (
            <div key={l} className="px-4 py-3 rounded-[var(--radius-input)] bg-[var(--color-surface-alt)] border border-[var(--color-border)]">
              <p className="label mb-0">{l}</p>
              <p className="text-[12px] font-bold text-[var(--color-text-muted)] italic mt-1">Hidden</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-3">Match Score</h3>
        <div className="max-w-xs"><ScoreBar score={Math.round(c.match_score)} /></div>
        <div className="grid grid-cols-2 gap-6 mt-5">
          <div><p className="label">Matched Skills</p><SkillTags skills={parseSkills(c.matched_skills)} /></div>
          <div>
            <p className="label">Missing Skills</p>
            <div className="flex flex-wrap gap-1">
              {parseSkills(c.missing_skills).map((s, i) => <span key={i} className="px-2 py-0.5 rounded-md bg-red-50 dark:bg-red-900/20 text-red-600 text-[10px] font-semibold">{s}</span>)}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6"><h3 className="text-[13px] font-bold text-[var(--color-text)] mb-3">Skills</h3><SkillTags skills={parseSkills(c.skills)} /></div>
        <div className="card p-6"><h3 className="text-[13px] font-bold text-[var(--color-text)] mb-3">Experience</h3><p className="text-[12px] text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">{c.experience || 'Not specified'}</p></div>
      </div>

      <div className="card p-6">
        <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-4">Evaluation</h3>
        <div className="flex flex-wrap gap-2.5">
          <button onClick={() => update('shortlisted')} className="btn-ghost text-[var(--color-success)] bg-[var(--color-success-soft)] border-transparent hover:opacity-80"><CheckCircle2 size={14} /> Shortlist</button>
          <button onClick={() => update('selected')} className="btn-ghost text-[var(--color-info)] bg-[var(--color-info-soft)] border-transparent hover:opacity-80"><CheckCircle2 size={14} /> Select</button>
          <button onClick={() => update('rejected')} className="btn-ghost text-[var(--color-danger)] bg-[var(--color-danger-soft)] border-transparent hover:opacity-80"><XCircle size={14} /> Reject</button>
          <button onClick={() => update('on_hold')} className="btn-ghost text-[var(--color-warning)] bg-[var(--color-warning-soft)] border-transparent hover:opacity-80"><Briefcase size={14} /> Hold</button>
        </div>
      </div>
    </div>
  );
}
