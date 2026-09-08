'use client';
import { useState, useRef } from 'react';
import { HiringCriteria } from '@/types';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { FileText, ChevronDown, ChevronUp, Plus, Trash2, Pencil } from 'lucide-react';

interface Props {
  onCreated: (c: HiringCriteria) => void;
  onUpdated: (c: HiringCriteria) => void;
  onDeleted: (id: number) => void;
  existingCriteria?: HiringCriteria[];
  selectedId?: number | null;
  onSelect?: (id: number) => void;
}

export default function HiringCriteriaForm({ onCreated, onUpdated, onDeleted, existingCriteria = [], selectedId, onSelect }: Props) {
  const [show, setShow] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [title, setTitle] = useState('');
  const [skills, setSkills] = useState('');
  const [jd, setJd] = useState('');
  const [exp, setExp] = useState('');
  const [minScore, setMinScore] = useState(70);
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; if (!file) return;
    setJd(await file.text());
  };

  const resetForm = () => {
    setTitle(''); setSkills(''); setJd(''); setExp(''); setMinScore(70);
    setEditId(null); setShow(false);
  };

  const startEdit = (c: HiringCriteria) => {
    setEditId(c.id);
    setTitle(c.role_title);
    setSkills(c.required_skills);
    setJd(c.job_description || '');
    setExp(c.required_experience || '');
    setMinScore(c.minimum_score);
    setShow(true);
  };

  const handleDelete = async (c: HiringCriteria) => {
    if (!confirm(`Delete "${c.role_title}" and all its ${c.candidate_count} candidate(s)? This cannot be undone.`)) return;
    try {
      await api.delete(`/hiring/${c.id}`);
      toast.success(`"${c.role_title}" deleted`);
      onDeleted(c.id);
    } catch {
      toast.error('Failed to delete');
    }
  };

  const submit = async () => {
    if (!title || !skills) { toast.error('Role title and skills required'); return; }
    setLoading(true);
    try {
      if (editId) {
        const r = await api.put(`/hiring/${editId}`, { role_title: title, required_skills: skills, required_experience: exp, minimum_score: minScore, job_description: jd });
        onUpdated(r.data.criteria);
        toast.success('Criteria updated');
      } else {
        const r = await api.post('/hiring', { role_title: title, required_skills: skills, required_experience: exp, minimum_score: minScore, job_description: jd });
        onCreated(r.data.criteria);
        toast.success('Criteria created');
      }
      resetForm();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } };
      toast.error(err.response?.data?.error || 'Failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="space-y-4">
      {existingCriteria.length > 0 && (
        <div>
          <p className="label">Select Existing Criteria</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {existingCriteria.map((c) => (
              <div key={c.id}
                className={`relative text-left p-4 rounded-[var(--radius-card)] border-2 transition-all cursor-pointer ${
                  selectedId === c.id ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]' : 'border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-primary)]/30'
                }`}
                onClick={() => onSelect?.(c.id)}
              >
                <p className="text-[13px] font-bold text-[var(--color-text)]">{c.role_title}</p>
                <p className="text-[11px] text-[var(--color-text-muted)] mt-1">Min Score {c.minimum_score}% · {c.candidate_count} candidates</p>
                {c.required_skills && (
                  <p className="text-[10px] text-[var(--color-text-secondary)] mt-1.5 truncate">Skills: {c.required_skills}</p>
                )}
                {/* Action buttons */}
                <div className="absolute top-3 right-3 flex items-center gap-1">
                  <button
                    onClick={(e) => { e.stopPropagation(); startEdit(c); }}
                    className="w-7 h-7 flex items-center justify-center rounded-lg text-[var(--color-text-muted)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-soft)] transition-all"
                    title="Edit criteria"
                  >
                    <Pencil size={12} />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(c); }}
                    className="w-7 h-7 flex items-center justify-center rounded-lg text-[var(--color-text-muted)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger-soft)] transition-all"
                    title="Delete criteria and all candidates"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <button onClick={() => { if (show) resetForm(); else setShow(true); }} className="flex items-center gap-2 text-[13px] font-semibold text-[var(--color-primary)] hover:opacity-80 transition-all">
        {show ? <ChevronUp size={15} /> : <Plus size={15} />}
        {show ? 'Close Form' : 'Create New Criteria'}
      </button>

      {show && (
        <div className="card-flat p-6 space-y-5">
          {editId && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-[var(--color-primary-soft)] border border-indigo-200/40">
              <Pencil size={13} className="text-[var(--color-primary)]" />
              <p className="text-[12px] font-semibold text-[var(--color-primary)]">Editing criteria — make changes and save below</p>
            </div>
          )}
          <div>
            <label className="label">Role Title *</label>
            <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g., Machine Learning Engineer" />
          </div>
          <div>
            <label className="label">Required Skills * (comma-separated)</label>
            <input className="input" value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="e.g., Python, Machine Learning, NLP, SQL" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="label mb-0">Job Description (paste or upload file)</label>
              <button onClick={() => fileRef.current?.click()} className="flex items-center gap-1.5 text-[11px] font-semibold text-[var(--color-primary)] hover:underline">
                <FileText size={12} /> Upload file
              </button>
              <input ref={fileRef} type="file" accept=".txt,.pdf,.docx" onChange={handleFile} className="hidden" />
            </div>
            <textarea className="input resize-none" rows={5} value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the full job description here... Include responsibilities, qualifications, requirements, etc." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Experience</label>
              <input className="input" value={exp} onChange={(e) => setExp(e.target.value)} placeholder="e.g., 3 years" />
            </div>
            <div>
              <label className="label">Min Score: {minScore}%</label>
              <input type="range" min={0} max={100} value={minScore} onChange={(e) => setMinScore(Number(e.target.value))} className="w-full mt-2 accent-[var(--color-primary)]" />
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={submit} disabled={loading} className="btn-primary flex-1 justify-center disabled:opacity-40">
              {loading ? (editId ? 'Updating...' : 'Creating...') : (editId ? 'Update Criteria' : 'Create Criteria')}
            </button>
            {editId && (
              <button onClick={resetForm} className="btn-ghost px-5">Cancel</button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

