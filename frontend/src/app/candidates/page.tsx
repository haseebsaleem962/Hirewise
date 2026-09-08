'use client';
import { useState, useEffect } from 'react';
import { HiringCriteria, Candidate } from '@/types';
import api from '@/lib/api';
import CandidateTable from '@/components/CandidateTable';
import toast from 'react-hot-toast';
import { Trash2, XCircle } from 'lucide-react';

export default function CandidatesPage() {
  const [criteriaList, setCriteriaList] = useState<HiringCriteria[]>([]);
  const [sel, setSel] = useState<number | ''>('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  useEffect(() => { api.get('/hiring').then((r) => setCriteriaList(r.data.criteria)).catch(() => {}); }, []);

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (sel) params.criteria_id = sel.toString();
      if (filter) params.status = filter;
      setCandidates((await api.get('/candidates', { params })).data.candidates || []);
    } catch { toast.error('Failed to load'); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [sel, filter]);

  // Clear selection when filter/position changes
  useEffect(() => { setSelectedIds([]); }, [sel, filter]);

  const updateStatus = async (id: number, status: string) => {
    try { await api.put(`/candidates/${id}/status`, { status }); toast.success(`Candidate ${status}`); load(); } catch { toast.error('Failed'); }
  };

  const deleteSelected = async () => {
    if (selectedIds.length === 0) return;
    if (!confirm(`Delete ${selectedIds.length} selected candidate(s)? This cannot be undone.`)) return;
    try {
      await api.post('/candidates/bulk-delete', { ids: selectedIds });
      toast.success(`${selectedIds.length} candidate(s) deleted`);
      setSelectedIds([]);
      load();
    } catch { toast.error('Failed to delete'); }
  };

  const deleteAll = async () => {
    const label = sel ? (criteriaList.find((c) => c.id === sel)?.role_title || 'this position') : 'ALL positions';
    if (!confirm(`Delete ALL candidates for "${label}"? This cannot be undone.`)) return;
    try {
      const ep = sel ? `/candidates/all/${sel}` : '/candidates/all';
      const r = await api.delete(ep);
      toast.success(r.data.message || 'All candidates deleted');
      setSelectedIds([]);
      load();
    } catch { toast.error('Failed to delete'); }
  };

  const filters = ['', 'Pending', 'AI Shortlisted', 'Manually Shortlisted', 'Not Shortlisted', 'Selected', 'Rejected', 'On Hold'];

  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      <div>
        <h1 className="text-[26px] font-extrabold text-[var(--color-text)] tracking-tight">Candidates</h1>
        <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">Review and manage all screened candidates</p>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <select value={sel} onChange={(e) => setSel(e.target.value ? Number(e.target.value) : '')} className="input w-auto min-w-[180px]">
          <option value="">All Positions</option>
          {criteriaList.map((c) => <option key={c.id} value={c.id}>{c.role_title}</option>)}
        </select>
        <div className="flex gap-1">
          {filters.map((s) => (
            <button key={s} onClick={() => setFilter(s)}
              className={`px-3 py-[7px] rounded-[var(--radius-btn)] text-[10px] font-bold transition-all ${
                filter === s ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-[var(--color-surface-alt)]'
              }`}>{s || 'All'}</button>
          ))}
        </div>
        {candidates.length > 0 && (
          <button onClick={deleteAll}
            className="ml-auto flex items-center gap-1.5 px-3 py-[7px] rounded-[var(--radius-btn)] text-[10px] font-bold text-[var(--color-danger)] bg-[var(--color-danger-soft)] border border-transparent hover:opacity-80 transition-all">
            <XCircle size={12} /> Remove All
          </button>
        )}
      </div>

      {/* Bulk action bar */}
      {selectedIds.length > 0 && (
        <div className="flex items-center justify-between px-5 py-3 rounded-[var(--radius-card)] bg-[var(--color-primary-soft)] border border-indigo-200/40 dark:border-indigo-800/30">
          <p className="text-[12px] font-semibold text-[var(--color-primary)]">
            {selectedIds.length} candidate(s) selected
          </p>
          <div className="flex items-center gap-2">
            <button onClick={() => setSelectedIds([])}
              className="px-3 py-1.5 rounded-lg text-[10px] font-semibold text-[var(--color-text-secondary)] bg-[var(--color-surface)] border border-[var(--color-border)] hover:bg-[var(--color-surface-alt)] transition-all">
              Clear
            </button>
            <button onClick={deleteSelected}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-[var(--color-danger)] text-white text-[10px] font-bold hover:opacity-90 transition-all shadow-sm">
              <Trash2 size={12} /> Delete Selected
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-20"><div className="w-7 h-7 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin" /></div>
      ) : candidates.length === 0 ? (
        <div className="card-flat p-16 text-center text-[13px] text-[var(--color-text-muted)]">No candidates found</div>
      ) : (
        <CandidateTable
          candidates={candidates}
          criteriaId={sel ? Number(sel) : undefined}
          onStatusChange={updateStatus}
          selectedIds={selectedIds}
          onSelectionChange={setSelectedIds}
        />
      )}
    </div>
  );
}
