'use client';
interface Props { status: string; }
const map: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-600', Pending: 'bg-slate-100 text-slate-600',
  shortlisted: 'bg-emerald-50 text-emerald-700', 'AI Shortlisted': 'bg-emerald-50 text-emerald-700', 'Manually Shortlisted': 'bg-emerald-50 text-emerald-700',
  'Not Shortlisted': 'bg-red-50 text-red-600',
  rejected: 'bg-red-50 text-red-600', Rejected: 'bg-red-50 text-red-600',
  selected: 'bg-indigo-50 text-indigo-700', Selected: 'bg-indigo-50 text-indigo-700',
  on_hold: 'bg-amber-50 text-amber-700', 'On Hold': 'bg-amber-50 text-amber-700',
};
export default function StatusBadge({ status }: Props) {
  return (
    <span className={`inline-flex px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${map[status] || map.pending}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}
