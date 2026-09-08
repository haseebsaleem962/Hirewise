'use client';

import { BlindModeProvider } from '@/context/BlindModeContext';
import { Toaster } from 'react-hot-toast';
import Sidebar from '@/components/Sidebar';
import Navbar from '@/components/Navbar';

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <BlindModeProvider>
      <div className="flex h-screen overflow-hidden bg-[var(--color-bg)]">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto px-6 py-6 lg:px-8 lg:py-8">
            {children}
          </main>
        </div>
      </div>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            borderRadius: '12px',
            background: 'var(--color-surface)',
            color: 'var(--color-text)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-dropdown)',
            fontSize: '13px',
            fontWeight: '500',
          },
        }}
      />
    </BlindModeProvider>
  );
}
