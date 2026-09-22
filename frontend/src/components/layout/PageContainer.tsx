import React, { ReactNode } from 'react';

export default function PageContainer({ children }: { children: ReactNode }) {
  return (
    <main className="flex-1 overflow-auto p-6 bg-slate-50">
      <div className="max-w-7xl mx-auto h-full flex flex-col gap-6">
        {children}
      </div>
    </main>
  );
}
