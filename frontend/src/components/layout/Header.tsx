import React from 'react';
import { useLocation } from 'react-router-dom';
import { UserCircle, Bell } from 'lucide-react';

export default function Header() {
  const location = useLocation();
  
  const getPageTitle = (path: string) => {
    switch (path) {
      case '/dashboard': return 'Dashboard';
      case '/priority-queue': return 'Priority Queue';
      case '/methodology': return 'Methodology';
      case '/download-report': return 'Download Report';
      default: return '';
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 shrink-0">
      <div className="flex flex-col">
        <h2 className="text-lg font-semibold text-slate-800">
          {getPageTitle(location.pathname)}
        </h2>
        <span className="text-xs text-slate-500 font-medium">Gosikhurd Reservoir (Mock Active)</span>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="text-slate-400 hover:text-slate-600 relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="flex items-center gap-2 pl-4 border-l border-slate-200">
          <div className="flex flex-col items-end">
            <span className="text-sm font-medium text-slate-700">Authorized Officer</span>
            <span className="text-xs text-slate-500">Environmental Dept</span>
          </div>
          <UserCircle className="w-8 h-8 text-slate-400" />
        </div>
      </div>
    </header>
  );
}
