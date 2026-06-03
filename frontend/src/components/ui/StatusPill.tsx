import React from 'react';

export default function StatusPill({ status }: { status: string }) {
  const getStyle = () => {
    switch (status) {
      case 'LIKELY_COMPLIANT':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'REQUIRES_FURTHER_INFO':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'LIKELY_NON_COMPLIANT':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  const getLabel = () => {
    return status.replace(/_/g, ' ');
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStyle()}`}>
      {getLabel()}
    </span>
  );
}
