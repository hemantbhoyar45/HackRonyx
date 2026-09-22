import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ListOrdered, FileSearch, FileDown, Droplets } from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Priority Queue', path: '/priority-queue', icon: ListOrdered },
    { name: 'Methodology', path: '/methodology', icon: FileSearch },
    { name: 'Download Report', path: '/download-report', icon: FileDown },
  ];

  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-full border-r border-slate-800">
      <div className="p-6 flex items-center gap-3 border-b border-slate-800">
        <Droplets className="text-brand-500 w-8 h-8" />
        <div>
          <h1 className="font-bold text-lg tracking-tight">Water Intelligence</h1>
          <p className="text-xs text-slate-400">Authorized Access Only</p>
        </div>
      </div>
      
      <nav className="flex-1 py-6">
        <ul className="space-y-1 px-3">
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive 
                      ? 'bg-brand-600 text-white' 
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-slate-800 bg-slate-900/50">
        <div className="text-xs text-slate-400 mb-1">System Status</div>
        <div className="flex items-center gap-2 text-sm text-green-400">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Operational
        </div>
      </div>
    </div>
  );
}
