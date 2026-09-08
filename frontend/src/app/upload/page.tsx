'use client';

import { useState, useEffect } from 'react';
import { HiringCriteria } from '@/types';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import ResumeUpload from '@/components/ResumeUpload';
import HiringCriteriaForm from '@/components/HiringCriteriaForm';
import { Upload, Target, ChevronRight } from 'lucide-react';

export default function UploadPage() {
  const [criteriaList, setCriteriaList] = useState<HiringCriteria[]>([]);
  const [selectedCriteriaId, setSelectedCriteriaId] = useState<number | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<{ total: number; processed: number; shortlisted: number } | null>(null);

  const loadCriteria = async () => {
    try { const r = await api.get('/hiring'); setCriteriaList(r.data.criteria); } catch { /* */ }
  };
  useEffect(() => { loadCriteria(); }, []);

  const handleCreated = (c: HiringCriteria) => { setCriteriaList((p) => [c, ...p]); setSelectedCriteriaId(c.id); };
  const handleUpdated = (c: HiringCriteria) => { setCriteriaList((p) => p.map((x) => x.id === c.id ? c : x)); };
  const handleDeleted = (id: number) => {
    setCriteriaList((p) => p.filter((x) => x.id !== id));
    if (selectedCriteriaId === id) setSelectedCriteriaId(null);
  };

  const handleUpload = async (files: File[]) => {
    if (!selectedCriteriaId) { toast.error('Select or create hiring criteria first'); return; }
    setIsUploading(true); setResult(null);
    const fd = new FormData();
    fd.append('criteria_id', selectedCriteriaId.toString());
    files.forEach((f) => fd.append('files', f));
    try {
      const r = await api.post('/candidates/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 });
      const d = r.data;
      setResult({ total: d.total_files || d.processed || 0, processed: d.processed || 0, shortlisted: d.shortlisted || 0 });
      toast.success(`${d.processed || 0} resumes processed!`);
      if (d.errors?.length) toast.error(`${d.errors.length} file(s) failed — ${d.errors[0]}`);
      loadCriteria();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } };
      toast.error(err.response?.data?.error || 'Upload failed');
    } finally { setIsUploading(false); }
  };

  const selected = criteriaList.find((c) => c.id === selectedCriteriaId);

  return (
    <div className="max-w-[1100px] mx-auto space-y-8">
      <div>
        <h1 className="text-[26px] font-extrabold text-[var(--color-text)] tracking-tight">Upload & Screen</h1>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">Paste a job description and upload up to 80 resumes for AI screening</p>
      </div>

      {/* Step 1 */}
      <div className="card p-6 lg:p-7">
        <div className="flex items-center gap-2.5 mb-6">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Target size={13} className="text-white" strokeWidth={2.5} />
          </div>
          <h2 className="text-[14px] font-bold text-[var(--color-text)]">Step 1 — Hiring Criteria & Job Description</h2>
        </div>
        <HiringCriteriaForm onCreated={handleCreated} onUpdated={handleUpdated} onDeleted={handleDeleted} existingCriteria={criteriaList} selectedId={selectedCriteriaId} onSelect={setSelectedCriteriaId} />
      </div>

      {/* Step 2 */}
      <div className="card p-6 lg:p-7">
        <div className="flex items-center gap-2.5 mb-6">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Upload size={13} className="text-white" strokeWidth={2.5} />
          </div>
          <h2 className="text-[14px] font-bold text-[var(--color-text)]">Step 2 — Upload Resumes</h2>
        </div>

        {selected ? (
          <div className="mb-5 flex items-center gap-3 p-4 rounded-[var(--radius-input)] bg-[var(--color-primary-soft)] border border-indigo-200/40 dark:border-indigo-800/30">
            <ChevronRight size={16} className="text-[var(--color-primary)] shrink-0" />
            <div className="min-w-0">
              <p className="text-[12px] font-semibold text-[var(--color-primary)]">Screening for: {selected.role_title}</p>
              <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5 truncate">Min score {selected.minimum_score}% · {selected.required_skills.substring(0, 100)}{selected.required_skills.length > 100 ? '...' : ''}</p>
            </div>
          </div>
        ) : (
          <div className="mb-5 p-4 rounded-[var(--radius-input)] bg-[var(--color-warning-soft)] border border-amber-200/40 dark:border-amber-800/30">
            <p className="text-[12px] font-medium text-[var(--color-warning)]">Select or create hiring criteria first</p>
          </div>
        )}

        <ResumeUpload onFilesSelected={handleUpload} isUploading={isUploading} />
      </div>

      {/* Result */}
      {result && (
        <div className="card p-6 lg:p-7">
          <h3 className="text-[14px] font-bold text-[var(--color-text)] mb-5">Upload Results</h3>
          <div className="grid grid-cols-3 gap-4">
            {[
              { val: result.total, label: 'Uploaded', color: '' },
              { val: result.processed, label: 'Processed', color: '' },
              { val: result.shortlisted, label: 'Shortlisted', color: 'text-[var(--color-success)]' },
            ].map((d) => (
              <div key={d.label} className="text-center p-5 rounded-[var(--radius-card)] bg-[var(--color-surface-alt)]">
                <p className={`text-[32px] font-extrabold leading-none tracking-tight ${d.color || 'text-[var(--color-text)]'}`}>{d.val}</p>
                <p className="text-[10px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider mt-2">{d.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
