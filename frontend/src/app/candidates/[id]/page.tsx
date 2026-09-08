'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Candidate, parseSkills } from '@/types';
import { useBlindMode } from '@/context/BlindModeContext';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import ScoreBar from '@/components/ScoreBar';
import StatusBadge from '@/components/StatusBadge';
import SkillTags from '@/components/SkillTags';
import { ArrowLeft, User, Mail, MapPin, GraduationCap, CheckCircle2, XCircle, Briefcase, Pencil, Send, Save, X } from 'lucide-react';

export default function CandidateDetail() {
  const { id } = useParams();
  const router = useRouter();
  const { blindMode } = useBlindMode();
  const [c, setC] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingEmail, setEditingEmail] = useState(false);
  const [emailValue, setEmailValue] = useState('');
  const [savingEmail, setSavingEmail] = useState(false);

  // Custom email state
  const [showCustomEmail, setShowCustomEmail] = useState(false);
  const [customSubject, setCustomSubject] = useState('');
  const [customBody, setCustomBody] = useState('');
  const [sendingCustom, setSendingCustom] = useState(false);

  useEffect(() => {
    const ep = blindMode ? `/candidates/${id}/blind` : `/candidates/${id}`;
    api.get(ep).then((r) => {
      setC(r.data.candidate);
      setEmailValue(r.data.candidate.email || '');
    }).catch(() => {}).finally(() => setLoading(false));
  }, [id, blindMode]);

  const update = async (status: string) => {
    try { await api.put(`/candidates/${id}/status`, { status }); toast.success(`Candidate ${status}`); setC((p) => p ? { ...p, final_status: status } : p); } catch { toast.error('Failed'); }
  };
  const sendEmail = async (type: string) => {
    try { await api.post(`/email/send/${id}`, { email_type: type }); toast.success('Email sent'); } catch { toast.error('Email failed'); }
  };

  const saveEmail = async () => {
    setSavingEmail(true);
    try {
      const res = await api.put(`/candidates/${id}`, { email: emailValue.trim() });
      setC((p) => p ? { ...p, email: emailValue.trim() } : p);
      setEditingEmail(false);
      toast.success('Email updated');
    } catch {
      toast.error('Failed to update email');
    } finally { setSavingEmail(false); }
  };

  const sendCustom = async () => {
    if (!customSubject.trim() || !customBody.trim()) { toast.error('Please fill subject and body'); return; }
    setSendingCustom(true);
    try {
      await api.post(`/email/send-custom/${id}`, { subject: customSubject, body: customBody });
      toast.success('Custom email sent!');
      setShowCustomEmail(false);
      setCustomSubject('');
      setCustomBody('');
    } catch { toast.error('Failed to send'); } finally { setSendingCustom(false); }
  };

  if (loading) return <div className="flex justify-center py-20"><div className="w-7 h-7 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin" /></div>;
  if (!c) return <p className="text-center py-20 text-[13px] text-[var(--color-text-muted)]">Candidate not found</p>;

  return (
    <div className="max-w-[900px] mx-auto space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-[12px] font-semibold text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors">
        <ArrowLeft size={14} /> Back
      </button>

      {/* Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[var(--color-primary-soft)] flex items-center justify-center">
              <User size={22} className="text-[var(--color-primary)]" />
            </div>
            <div>
              <h1 className="text-[20px] font-extrabold text-[var(--color-text)]">{blindMode ? 'Anonymous Candidate' : c.name}</h1>
              <p className="text-[13px] text-[var(--color-text-muted)] mt-0.5">{c.resume_category} · {c.experience || '—'} experience</p>
            </div>
          </div>
          <StatusBadge status={c.final_status} />
        </div>
        {!blindMode && (
          <div className="flex flex-wrap gap-4 mt-4 text-[12px] text-[var(--color-text-secondary)]">
            {/* Email with edit */}
            <span className="flex items-center gap-1.5">
              <Mail size={12} />
              {editingEmail ? (
                <span className="flex items-center gap-1">
                  <input
                    type="email"
                    value={emailValue}
                    onChange={(e) => setEmailValue(e.target.value)}
                    className="px-2 py-0.5 rounded border border-[var(--color-border)] text-[11px] w-56 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
                    placeholder="candidate@email.com"
                    autoFocus
                  />
                  <button onClick={saveEmail} disabled={savingEmail} className="p-0.5 text-[var(--color-success)] hover:opacity-70"><Save size={12} /></button>
                  <button onClick={() => { setEditingEmail(false); setEmailValue(c.email || ''); }} className="p-0.5 text-[var(--color-text-muted)] hover:opacity-70"><X size={12} /></button>
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  {c.email || <span className="italic text-[var(--color-text-muted)]">No email</span>}
                  <button onClick={() => { setEditingEmail(true); setEmailValue(c.email || ''); }} className="p-0.5 text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors">
                    <Pencil size={10} />
                  </button>
                </span>
              )}
            </span>
            {c.location && <span className="flex items-center gap-1.5"><MapPin size={12} />{c.location}</span>}
            {c.institute && <span className="flex items-center gap-1.5"><GraduationCap size={12} />{c.institute}</span>}
          </div>
        )}
      </div>

      {/* Score */}
      <div className="card p-6">
        <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-3">Match Score</h3>
        <div className="max-w-xs"><ScoreBar score={Math.round(c.match_score)} /></div>
        <div className="grid grid-cols-2 gap-6 mt-5">
          <div>
            <p className="label">Matched Skills</p>
            <SkillTags skills={parseSkills(c.matched_skills)} />
          </div>
          <div>
            <p className="label">Missing Skills</p>
            <div className="flex flex-wrap gap-1">
              {parseSkills(c.missing_skills).map((s, i) => (
                <span key={i} className="px-2 py-0.5 rounded-md bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-[10px] font-semibold">{s}</span>
              ))}
              {parseSkills(c.missing_skills).length === 0 && <span className="text-[11px] text-[var(--color-text-muted)]">None</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Skills & Experience */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-3">All Skills</h3>
          <SkillTags skills={parseSkills(c.skills)} />
        </div>
        <div className="card p-6">
          <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-3">Experience</h3>
          <p className="text-[12px] text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">{c.experience || 'Not specified'}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="card p-6">
        <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-4">Status Actions</h3>
        <div className="flex flex-wrap gap-2.5">
          <button onClick={() => update('shortlisted')} className="btn-ghost text-[var(--color-success)] bg-[var(--color-success-soft)] border-transparent hover:opacity-80">
            <CheckCircle2 size={14} /> Shortlist
          </button>
          <button onClick={() => update('selected')} className="btn-ghost text-[var(--color-info)] bg-[var(--color-info-soft)] border-transparent hover:opacity-80">
            <CheckCircle2 size={14} /> Select
          </button>
          <button onClick={() => update('rejected')} className="btn-ghost text-[var(--color-danger)] bg-[var(--color-danger-soft)] border-transparent hover:opacity-80">
            <XCircle size={14} /> Reject
          </button>
          <button onClick={() => update('on_hold')} className="btn-ghost text-[var(--color-warning)] bg-[var(--color-warning-soft)] border-transparent hover:opacity-80">
            <Briefcase size={14} /> Hold
          </button>
        </div>
      </div>

      {/* Email Section */}
      {!blindMode && (
        <div className="card p-6">
          <h3 className="text-[13px] font-bold text-[var(--color-text)] mb-4">Send Email</h3>
          {!c.email && !editingEmail && (
            <p className="text-[11px] text-[var(--color-warning)] mb-3">No email address on file. Edit the email above before sending.</p>
          )}
          <div className="flex flex-wrap gap-2.5 mb-4">
            <button onClick={() => sendEmail('shortlisted')} disabled={!c.email}
              className="btn-ghost text-[var(--color-success)] bg-[var(--color-success-soft)] border-transparent hover:opacity-80 disabled:opacity-40 disabled:cursor-not-allowed">
              <Send size={14} /> Shortlist Email
            </button>
            <button onClick={() => sendEmail('rejected')} disabled={!c.email}
              className="btn-ghost text-[var(--color-danger)] bg-[var(--color-danger-soft)] border-transparent hover:opacity-80 disabled:opacity-40 disabled:cursor-not-allowed">
              <Send size={14} /> Rejection Email
            </button>
            <button onClick={() => setShowCustomEmail(!showCustomEmail)} disabled={!c.email}
              className="btn-ghost disabled:opacity-40 disabled:cursor-not-allowed">
              <Mail size={14} /> Custom Email
            </button>
          </div>

          {/* Custom Email Form */}
          {showCustomEmail && (
            <div className="mt-4 p-4 rounded-[var(--radius-card)] bg-[var(--color-surface-alt)] border border-[var(--color-border-light)] space-y-3">
              <input
                type="text"
                value={customSubject}
                onChange={(e) => setCustomSubject(e.target.value)}
                placeholder="Subject (use {name} for candidate name, {position} for role)"
                className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-[12px] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
              />
              <textarea
                value={customBody}
                onChange={(e) => setCustomBody(e.target.value)}
                placeholder="Email body... Use {name} for candidate name, {position} for role title"
                rows={6}
                className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-[12px] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
              />
              <div className="flex items-center justify-between">
                <p className="text-[10px] text-[var(--color-text-muted)]">Variables: {'{name}'}, {'{position}'}, {'{email}'}</p>
                <div className="flex gap-2">
                  <button onClick={() => { setShowCustomEmail(false); setCustomSubject(''); setCustomBody(''); }}
                    className="px-3 py-1.5 rounded-lg text-[11px] font-semibold text-[var(--color-text-muted)] hover:bg-[var(--color-surface-alt)]">Cancel</button>
                  <button onClick={sendCustom} disabled={sendingCustom || !customSubject.trim() || !customBody.trim()}
                    className="px-4 py-1.5 rounded-lg bg-[var(--color-primary)] text-white text-[11px] font-semibold hover:opacity-90 disabled:opacity-40 flex items-center gap-1.5">
                    {sendingCustom ? <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send size={12} />}
                    Send Custom
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
