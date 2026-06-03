'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Analyse Application', path: '/analyse' },
    { name: 'Policy Library', path: '/documents' },
    { name: 'About & Focus Group', path: '/about' },
  ];

  return (
    <div className="w-64 bg-brand-navy text-white h-full flex flex-col shadow-xl flex-shrink-0">
      <div className="p-6 border-b border-white/10">
        <h1 className="text-2xl font-bold tracking-tight text-brand-ice mb-1">
          PILOT-AI
        </h1>
        <span className="bg-brand-teal text-white text-xs px-2 py-0.5 rounded font-medium">
          DEMO v0.1-free
        </span>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`block px-4 py-2.5 rounded-md transition-colors ${
                isActive 
                  ? 'bg-brand-sky text-white font-medium shadow-sm' 
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              }`}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/10 text-xs text-slate-400 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
        Free demo — no cloud costs
      </div>
    </div>
  );
}
