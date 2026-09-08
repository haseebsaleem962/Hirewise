'use client';
import { Candidate, parseSkills } from '@/types';
import { useBlindMode } from '@/context/BlindModeContext';
import Link from 'next/link';
import StatusBadge from './StatusBadge';
import ScoreBar from './ScoreBar';
import SkillTags from './SkillTags';
import { User, Mail as MailIcon } from 'lucide-react';

interface Props {
  candidates: Candidate[];
  criteriaId?: number;
  onStatusChange?: (id: number, status: string) => void;
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
}

function isNew(createdAt: string): boolean {
  if (!createdAt) return false;
  // Backend timestamps are UTC without a timezone marker; append 'Z' so the
  // comparison isn't shifted by the local UTC offset.
  const hasZone = /Z$|[+-]\d{2}:?\d{2}$/.test(createdAt);
  const created = new Date(hasZone ? createdAt : `${createdAt}Z`);
  if (isNaN(created.getTime())) return false;
  const hoursDiff = (Date.now() - created.getTime()) / (1000 * 60 * 60);
  return hoursDiff >= 0 && hoursDiff < 24; // "New" badge for candidates added within last 24 hours
}

export default function CandidateTable({ candidates, onStatusChange, selectedIds, onSelectionChange }: Props) {
  const { blindMode } = useBlindMode();

  const allSelected = candidates.length > 0 && candidates.every((c) => selectedIds.includes(c.id));
  const someSelected = selectedIds.length > 0 && !allSelected;

  const toggleAll = () => {
    if (allSelected) {
      onSelectionChange([]);
    } else {
      onSelectionChange(candidates.map((c) => c.id));
    }
  };

  const toggleOne = (id: number) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((x) => x !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  return (
    <div className="overflow-hidden rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[var(--shadow-card)]">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-[var(--color-surface-alt)]">
              <th className="px-4 py-3 w-10">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => { if (el) el.indeterminate = someSelected; }}
                  onChange={toggleAll}
                  className="w-3.5 h-3.5 rounded accent-[var(--color-primary)] cursor-pointer"
                />
              </th>
              {['Candidate', 'Email', 'Category', 'Skills', 'Score', 'Status', 'Actions'].map((h) => (
                <th key={h} className={`px-5 py-3 text-[10px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider ${h === 'Score' || h === 'Status' || h === 'Actions' ? 'text-center' : 'text-left'}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border-light)]">
            {candidates.map((c) => {
              const selected = selectedIds.includes(c.id);
              const showNew = isNew(c.created_at);
              return (
                <tr key={c.id} className={`transition-colors ${selected ? 'bg-[var(--color-primary-soft)]' : 'hover:bg-[var(--color-surface-alt)]/50'}`}>
                  <td className="px-4 py-3.5">
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => toggleOne(c.id)}
                      className="w-3.5 h-3.5 rounded accent-[var(--color-primary)] cursor-pointer"
                    />
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-[var(--color-primary-soft)] flex items-center justify-center shrink-0">
                        <User size={13} className="text-[var(--color-primary)]" />
                      </div>
                      <div>
                        <div className="flex items-center gap-1.5">
                          <p className="text-[12px] font-semibold text-[var(--color-text)]">{blindMode ? 'Anonymous' : c.name}</p>
                          {showNew && (
                            <span className="px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase tracking-wider bg-emerald-500 text-white leading-none">New</span>
                          )}
                        </div>
                        <p className="text-[10px] text-[var(--color-text-muted)]">{blindMode ? '—' : `${c.gender || 'Unknown'} · ${c.location || 'Unknown'}`}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    {blindMode ? <span className="text-[10px] text-[var(--color-text-muted)]">—</span> : c.email ? (
                      <span className="inline-flex items-center gap-1 text-[11px] text-[var(--color-text-secondary)]">
                        <MailIcon size={10} className="shrink-0" />
                        <span className="truncate max-w-[160px]">{c.email}</span>
                      </span>
                    ) : (
                      <span className="text-[10px] text-[var(--color-text-muted)] italic">No email</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex px-2 py-0.5 rounded-md bg-[var(--color-surface-alt)] text-[10px] font-semibold text-[var(--color-text-secondary)]">{c.resume_category}</span>
                  </td>
                  <td className="px-5 py-3.5"><SkillTags skills={parseSkills(c.skills)} max={3} /></td>
                  <td className="px-5 py-3.5 w-28"><ScoreBar score={Math.round(c.match_score)} /></td>
                  <td className="px-5 py-3.5 text-center"><StatusBadge status={c.final_status} /></td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-center gap-1.5">
                      <Link href={blindMode ? `/candidates/${c.id}/blind` : `/candidates/${c.id}`}
                        className="px-3 py-1.5 rounded-lg bg-[var(--color-primary)] text-white text-[10px] font-semibold hover:opacity-90 transition-all">View</Link>
                      {onStatusChange && (c.final_status === 'Pending' || c.final_status === 'pending' || c.final_status === 'Not Shortlisted') && (
                        <button onClick={() => onStatusChange(c.id, 'shortlisted')}
                          className="px-3 py-1.5 rounded-lg bg-[var(--color-success-soft)] text-[var(--color-success)] text-[10px] font-semibold hover:opacity-80 transition-all">Shortlist</button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
