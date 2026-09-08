'use client';
import { Candidate, parseSkills } from '@/types';
import { useBlindMode } from '@/context/BlindModeContext';
import Link from 'next/link';
import StatusBadge from './StatusBadge';
import ScoreBar from './ScoreBar';
import SkillTags from './SkillTags';
import { User, Eye } from 'lucide-react';

interface Props { candidate: Candidate; onShortlist?: () => void; onReject?: () => void; }

export default function CandidateCard({ candidate: c, onShortlist, onReject }: Props) {
  const { blindMode } = useBlindMode();
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[var(--color-primary-soft)] flex items-center justify-center">
            <User size={16} className="text-[var(--color-primary)]" />
          </div>
          <div>
            <h3 className="text-[13px] font-bold text-[var(--color-text)]">{blindMode ? 'Anonymous' : c.name}</h3>
            <p className="text-[10px] text-[var(--color-text-muted)]">{c.resume_category}</p>
          </div>
        </div>
        <StatusBadge status={c.final_status} />
      </div>
      <div className="mb-3"><ScoreBar score={Math.round(c.match_score)} /></div>
      <div className="mb-4"><SkillTags skills={parseSkills(c.skills)} max={5} /></div>
      <div className="flex items-center gap-2">
        <Link href={blindMode ? `/candidates/${c.id}/blind` : `/candidates/${c.id}`} className="btn-primary flex-1 justify-center text-[11px] py-2">
          {blindMode && <Eye size={12} />} View Details
        </Link>
        {(c.final_status === 'Pending' || c.final_status === 'pending') && onShortlist && (
          <button onClick={onShortlist} className="btn-ghost flex-1 justify-center text-[11px] py-2 text-[var(--color-success)] bg-[var(--color-success-soft)] border-transparent hover:opacity-80">Shortlist</button>
        )}
        {(c.final_status === 'Pending' || c.final_status === 'pending') && onReject && (
          <button onClick={onReject} className="btn-ghost flex-1 justify-center text-[11px] py-2 text-[var(--color-danger)] bg-[var(--color-danger-soft)] border-transparent hover:opacity-80">Reject</button>
        )}
      </div>
    </div>
  );
}
