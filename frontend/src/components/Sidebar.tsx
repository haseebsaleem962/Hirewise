'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutGrid, Upload, Users, Mail, BarChart3, Sparkles } from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutGrid },
  { href: '/upload', label: 'Upload & Screen', icon: Upload },
  { href: '/candidates', label: 'Candidates', icon: Users },
  { href: '/emails', label: 'Emails', icon: Mail },
  { href: '/reports', label: 'Analytics', icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[250px] bg-[var(--color-sidebar)] flex flex-col h-screen shrink-0 select-none">
      {/* Brand */}
      <div className="px-5 pt-6 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-[10px] bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Sparkles size={16} className="text-white" strokeWidth={2.5} />
          </div>
          <div>
            <span className="text-[15px] font-extrabold text-white tracking-tight">HireWise</span>
            <span className="block text-[9.5px] font-bold tracking-[0.15em] text-slate-500 uppercase -mt-0.5">Smart Hiring</span>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-5 h-px bg-white/[0.06]" />

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p className="px-3 pb-2 text-[9.5px] font-bold tracking-[0.15em] text-slate-600 uppercase">Menu</p>
        {navItems.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group relative flex items-center gap-3 px-3 py-[9px] rounded-[10px] text-[13px] font-medium transition-all duration-200 ${
                active
                  ? 'bg-[var(--color-sidebar-active)] text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
              }`}
            >
              {active && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-indigo-500" />
              )}
              <item.icon size={17} strokeWidth={active ? 2.2 : 1.8} className={active ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-400'} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-[11px] font-bold shadow-sm">
            R
          </div>
          <div className="min-w-0">
            <p className="text-[12px] font-semibold text-white truncate">Recruiter</p>
            <p className="text-[10px] text-slate-500 truncate">AI-Powered Screening</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
