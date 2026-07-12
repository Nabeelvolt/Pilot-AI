'use client';

import React, { useState, useEffect } from 'react';

interface Props {
  children: React.ReactNode;
}

export default function AuthGate({ children }: Props) {
  const [unlocked, setUnlocked] = useState(false);
  const [code, setCode] = useState('');
  
  // If no access code is configured, bypass auth automatically
  useEffect(() => {
    if (!process.env.NEXT_PUBLIC_ACCESS_CODE) {
      setUnlocked(true);
    }
  }, []);

  if (unlocked) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-navy w-full z-50">
      <div className="bg-white rounded-xl p-8 w-80 shadow-xl text-center">
        <h1 className="text-2xl font-bold text-brand-navy mb-2">PILOT-AI</h1>
        <p className="text-sm text-slate-500 mb-6">University of Lincoln — Research Demo</p>
        <input
          type="password"
          placeholder="Access code"
          value={code}
          onChange={e => setCode(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && setUnlocked(code === process.env.NEXT_PUBLIC_ACCESS_CODE)}
          className="w-full border rounded-lg px-4 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-brand-teal text-slate-800"
        />
        <button
          onClick={() => setUnlocked(code === process.env.NEXT_PUBLIC_ACCESS_CODE)}
          className="w-full bg-brand-teal text-white py-2 rounded-lg text-sm font-medium hover:bg-brand-navy transition-colors"
        >
          Enter
        </button>
      </div>
    </div>
  );
}
