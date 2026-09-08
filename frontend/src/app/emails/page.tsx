'use client';
import { useState, useEffect } from 'react';
import { HiringCriteria, Candidate, EmailLog } from '@/types';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { Send, Clock, CheckCircle2, XCircle, Wifi, WifiOff, Loader2, Mail, FileText, PenLine, Users, UserCheck, UserX, User as UserIcon } from 'lucide-react';

interface SmtpStatus { configured: boolean; smtp_host: string; smtp_user: string; smtp_sender: string; }

type Tab = 'templates' | 'custom' | 'history';

export default function EmailsPage() {
  const [criteriaList, setCriteriaList] = useState<HiringCriteria[]>([]);
  const [logs, setLogs] = useState<EmailLog[]>([]);
  const [sel, setSel] = useState<number | ''>('');
  const [sending, setSending] = useState(false);
  const [smtp, setSmtp] = useState<SmtpStatus | null>(null);
  const [testing, setTesting] = useState(false);
  const [tab, setTab] = useState<Tab>('templates');

  // Candidates for selected position
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);

  // Custom email
  const [customSubject, setCustomSubject] = useState('');
  const [customBody, setCustomBody] = useState('');
  const [customRecipientIds, setCustomRecipientIds] = useState<number[]>([]);
  const [customSending, setCustomSending] = useState(false);

  useEffect(() => {
    api.get('/hiring').then((r) => setCriteriaList(r.data.criteria)).catch(() => {});
    api.get('/email/config-status').then((r) => setSmtp(r.data)).catch(() => {});
    loadLogs();
  }, []);

  useEffect(() => {
    if (!sel) { setCandidates([]); setCustomRecipientIds([]); return; }
    setLoadingCandidates(true);
    api.get(`/candidates?criteria_id=${sel}`).then((r) => setCandidates(r.data.candidates || []))
      .catch(() => setCandidates([])).finally(() => setLoadingCandidates(false));
  }, [sel]);

  const loadLogs = async () => { try { setLogs((await api.get('/email/logs')).data.logs || []); } catch { /* */ } };

  const sendBulk = async (type: string) => {
    if (!sel) { toast.error('Select a position first'); return; }
    if (!smtp?.configured) { toast.error('SMTP not configured — edit backend/.env'); return; }
    setSending(true);
    try { toast.success((await api.post(`/email/bulk/${sel}`, { email_type: type })).data.message || 'Emails sent'); loadLogs(); } catch { toast.error('Failed'); }
    finally { setSending(false); }
  };

  const testSmtp = async () => {
    setTesting(true);
    try {
      const r = await api.post('/email/test', {});
      if (r.data.success) toast.success(r.data.message); else toast.error(r.data.error || 'Connection failed');
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } };
      toast.error(err.response?.data?.error || 'SMTP test failed');
    } finally { setTesting(false); }
  };

  const sendCustomBulk = async () => {
    if (!sel) { toast.error('Select a position first'); return; }
    if (!customSubject.trim() || !customBody.trim()) { toast.error('Please fill subject and body'); return; }
    if (!smtp?.configured) { toast.error('SMTP not configured'); return; }
    setCustomSending(true);
    try {
      const r = await api.post(`/email/bulk-custom/${sel}`, {
        subject: customSubject,
        body: customBody,
        candidate_ids: customRecipientIds.length > 0 ? customRecipientIds : undefined,
      });
      toast.success(r.data.message);
      setCustomSubject(''); setCustomBody(''); setCustomRecipientIds([]);
      loadLogs();
    } catch { toast.error('Failed to send'); } finally { setCustomSending(false); }
  };

  const toggleRecipient = (id: number) => {
    setCustomRecipientIds((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  };

  const allWithEmail = candidates.filter((c) => c.email);
  const allRecipientsSelected = allWithEmail.length > 0 && allWithEmail.every((c) => customRecipientIds.includes(c.id));

  const shortlistedCount = candidates.filter((c) => ['AI Shortlisted', 'Manually Shortlisted', 'Selected'].includes(c.final_status)).length;
  const rejectedCount = candidates.filter((c) => c.final_status === 'Rejected').length;
  const withEmailCount = candidates.filter((c) => c.email).length;
  const noEmailCount = candidates.filter((c) => !c.email).length;

  const tabs: { key: Tab; label: string; icon: typeof FileText }[] = [
    { key: 'templates', label: 'Built-in Templates', icon: FileText },
    { key: 'custom', label: 'Custom Email', icon: PenLine },
    { key: 'history', label: 'Email History', icon: Clock },
  ];

  return (
    <div className="max-w-[960px] mx-auto space-y-6">
      <div>
        <h1 className="text-[26px] font-extrabold text-[var(--color-text)] tracking-tight">Emails</h1>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">Send notifications and custom emails to candidates</p>
      </div>

      {/* SMTP Status Banner */}
      {smtp && (
        <div className={`flex items-center justify-between px-5 py-4 rounded-[var(--radius-card)] border ${
          smtp.configured
            ? 'bg-[var(--color-success-soft)] border-emerald-200/40 dark:border-emerald-800/30'
            : 'bg-[var(--color-warning-soft)] border-amber-200/40 dark:border-amber-800/30'
        }`}>
          <div className="flex items-center gap-3">
            {smtp.configured ? <Wifi size={18} className="text-[var(--color-success)]" /> : <WifiOff size={18} className="text-[var(--color-warning)]" />}
            <div>
              <p className={`text-[12px] font-bold ${smtp.configured ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]'}`}>
                {smtp.configured ? 'SMTP Connected' : 'SMTP Not Configured'}
              </p>
              <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5">
                {smtp.configured ? `Sending from ${smtp.smtp_sender || smtp.smtp_user}` : 'Edit backend/.env with your Gmail App Password'}
              </p>
            </div>
          </div>
          {smtp.configured && (
            <button onClick={testSmtp} disabled={testing} className="btn-ghost text-[10px] disabled:opacity-40">
              {testing ? <Loader2 size={12} className="animate-spin" /> : <Wifi size={12} />} Test Connection
            </button>
          )}
        </div>
      )}

      {/* Position Selector */}
      <div className="card p-5">
        <label className="label">Select Position</label>
        <select value={sel} onChange={(e) => { setSel(e.target.value ? Number(e.target.value) : ''); setCustomRecipientIds([]); }} className="input">
          <option value="">Choose a job position...</option>
          {criteriaList.map((c) => <option key={c.id} value={c.id}>{c.role_title} ({c.candidate_count} candidates)</option>)}
        </select>

        {sel && !loadingCandidates && candidates.length > 0 && (
          <div className="flex flex-wrap gap-3 mt-4">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--color-surface-alt)] text-[10px] font-semibold text-[var(--color-text-secondary)]">
              <Users size={10} /> {candidates.length} total
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/20 text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
              <UserCheck size={10} /> {shortlistedCount} shortlisted
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-50 dark:bg-red-900/20 text-[10px] font-semibold text-red-600 dark:text-red-400">
              <UserX size={10} /> {rejectedCount} rejected
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--color-info-soft)] text-[10px] font-semibold text-[var(--color-info)]">
              <Mail size={10} /> {withEmailCount} with email
            </span>
            {noEmailCount > 0 && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--color-warning-soft)] text-[10px] font-semibold text-[var(--color-warning)]">
                <UserIcon size={10} /> {noEmailCount} missing email
              </span>
            )}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-[var(--color-surface-alt)] border border-[var(--color-border-light)]">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-1 flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg text-[11px] font-bold transition-all ${
              tab === t.key
                ? 'bg-[var(--color-surface)] shadow-sm text-[var(--color-primary)]'
                : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
            }`}>
            <t.icon size={13} /> {t.label}
          </button>
        ))}
      </div>

      {/* TAB: Built-in Templates */}
      {tab === 'templates' && (
        <div className="card p-6 space-y-5">
          <h3 className="text-[14px] font-bold text-[var(--color-text)]">Built-in Email Templates</h3>
          <p className="text-[12px] text-[var(--color-text-secondary)]">Send pre-designed professional emails based on candidate status. Emails include candidate name, position title, and HireWise branding.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Shortlisted Template */}
            <div className="p-5 rounded-[var(--radius-card)] border border-emerald-200/50 dark:border-emerald-800/30 bg-emerald-50/50 dark:bg-emerald-900/10 space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center"><CheckCircle2 size={16} className="text-white" /></div>
                <div>
                  <p className="text-[13px] font-bold text-[var(--color-text)]">Shortlist Notification</p>
                  <p className="text-[10px] text-[var(--color-text-muted)]">Sent to: AI Shortlisted, Manually Shortlisted, Selected</p>
                </div>
              </div>
              <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
                Congratulations email with next steps info. Green branded header with candidate name and position personalization.
              </p>
              <button onClick={() => sendBulk('shortlisted')} disabled={sending || !sel}
                className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg bg-emerald-500 text-white text-[11px] font-bold hover:opacity-90 disabled:opacity-40 transition-all">
                {sending ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
                Send to Shortlisted ({shortlistedCount})
              </button>
            </div>

            {/* Rejected Template */}
            <div className="p-5 rounded-[var(--radius-card)] border border-slate-200/50 dark:border-slate-700/30 bg-slate-50/50 dark:bg-slate-800/10 space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-slate-500 flex items-center justify-center"><XCircle size={16} className="text-white" /></div>
                <div>
                  <p className="text-[13px] font-bold text-[var(--color-text)]">Rejection Notification</p>
                  <p className="text-[10px] text-[var(--color-text-muted)]">Sent to: Rejected candidates</p>
                </div>
              </div>
              <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
                Polite rejection email with encouragement. Slate branded header with candidate name and position personalization.
              </p>
              <button onClick={() => sendBulk('rejected')} disabled={sending || !sel}
                className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg bg-slate-500 text-white text-[11px] font-bold hover:opacity-90 disabled:opacity-40 transition-all">
                {sending ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
                Send to Rejected ({rejectedCount})
              </button>
            </div>
          </div>

          {!sel && <p className="text-[11px] text-[var(--color-text-muted)] text-center">Select a position above to enable sending</p>}
        </div>
      )}

      {/* TAB: Custom Email */}
      {tab === 'custom' && (
        <div className="card p-6 space-y-5">
          <h3 className="text-[14px] font-bold text-[var(--color-text)]">Custom Email</h3>
          <p className="text-[12px] text-[var(--color-text-secondary)]">Write your own email and send to selected candidates or all candidates with email addresses.</p>

          <div className="space-y-4">
            <div>
              <label className="label">Subject</label>
              <input type="text" value={customSubject} onChange={(e) => setCustomSubject(e.target.value)}
                placeholder="e.g., Interview Invitation for {position}" className="input" />
            </div>
            <div>
              <label className="label">Email Body</label>
              <textarea value={customBody} onChange={(e) => setCustomBody(e.target.value)} rows={8}
                placeholder="Dear {name},&#10;&#10;We would like to invite you for an interview for the {position} role...&#10;&#10;Best regards"
                className="input resize-none" />
            </div>

            <div className="flex items-center gap-2 text-[10px] text-[var(--color-text-muted)]">
              <span className="px-2 py-0.5 rounded bg-[var(--color-surface-alt)] font-mono">{'{name}'}</span>
              <span className="px-2 py-0.5 rounded bg-[var(--color-surface-alt)] font-mono">{'{position}'}</span>
              <span className="px-2 py-0.5 rounded bg-[var(--color-surface-alt)] font-mono">{'{email}'}</span>
              <span>— auto-replaced per candidate</span>
            </div>

            {/* Recipients */}
            {sel && candidates.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="label">Recipients ({customRecipientIds.length > 0 ? `${customRecipientIds.length} selected` : 'all with email'})</label>
                  <button onClick={() => {
                    if (allRecipientsSelected) setCustomRecipientIds([]);
                    else setCustomRecipientIds(allWithEmail.map((c) => c.id));
                  }} className="text-[10px] font-semibold text-[var(--color-primary)] hover:underline">
                    {allRecipientsSelected ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
                <div className="max-h-48 overflow-y-auto rounded-[var(--radius-card)] border border-[var(--color-border-light)] divide-y divide-[var(--color-border-light)]">
                  {candidates.map((c) => (
                    <label key={c.id} className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors ${customRecipientIds.includes(c.id) ? 'bg-[var(--color-primary-soft)]' : 'hover:bg-[var(--color-surface-alt)]/50'}`}>
                      <input type="checkbox" checked={customRecipientIds.includes(c.id)} onChange={() => toggleRecipient(c.id)}
                        className="w-3.5 h-3.5 rounded accent-[var(--color-primary)] cursor-pointer" />
                      <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-semibold text-[var(--color-text)] truncate">{c.name || 'Unknown'}</p>
                        <p className="text-[10px] text-[var(--color-text-muted)] truncate">{c.email || 'No email'} · Score: {Math.round(c.match_score)}%</p>
                      </div>
                      {!c.email && <span className="text-[9px] text-[var(--color-warning)] font-bold">NO EMAIL</span>}
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-2">
              <p className="text-[11px] text-[var(--color-text-muted)]">
                {customRecipientIds.length > 0
                  ? `Will send to ${customRecipientIds.length} selected candidate(s)`
                  : sel ? `Will send to all ${withEmailCount} candidate(s) with email` : 'Select a position first'}
              </p>
              <button onClick={sendCustomBulk} disabled={customSending || !sel || !customSubject.trim() || !customBody.trim()}
                className="flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-[var(--color-primary)] text-white text-[11px] font-bold hover:opacity-90 disabled:opacity-40 transition-all">
                {customSending ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
                Send Custom Email
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB: History */}
      {tab === 'history' && (
        <div className="card p-6">
          <h3 className="text-[14px] font-bold text-[var(--color-text)] mb-5">Email History</h3>
          {logs.length === 0 ? (
            <p className="text-[13px] text-[var(--color-text-muted)] text-center py-10">No emails sent yet</p>
          ) : (
            <div className="space-y-2">
              {logs.map((log) => (
                <div key={log.id} className="flex items-center justify-between px-4 py-3 rounded-[var(--radius-input)] bg-[var(--color-surface-alt)] border border-[var(--color-border-light)]">
                  <div className="flex items-center gap-3">
                    {log.email_status === 'sent' ? <CheckCircle2 size={14} className="text-[var(--color-success)]" /> : <XCircle size={14} className="text-[var(--color-danger)]" />}
                    <div>
                      <p className="text-[12px] font-semibold text-[var(--color-text)]">{log.candidate_name}</p>
                      <p className="text-[10px] text-[var(--color-text-muted)]">
                        {log.email_type === 'custom' ? (
                          <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 font-bold">Custom</span>
                        ) : log.email_type === 'shortlisted' ? (
                          <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 font-bold">Shortlisted</span>
                        ) : (
                          <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 font-bold">Rejected</span>
                        )}
                        <span className="ml-1.5">{log.email_status}</span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] text-[var(--color-text-muted)]">
                    <Clock size={11} />{new Date(log.sent_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
