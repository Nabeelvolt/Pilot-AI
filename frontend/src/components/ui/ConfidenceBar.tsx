import React from 'react';

export default function ConfidenceBar({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100);
  
  let color = 'bg-emerald-500';
  if (percentage < 70) color = 'bg-amber-500';
  if (percentage < 50) color = 'bg-red-500';

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-slate-700">AI Confidence Score</span>
        <span className="font-bold text-slate-900">{percentage}%</span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2.5">
        <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${percentage}%` }}></div>
      </div>
      <p className="text-xs text-slate-500 mt-1">
        AI Confidence reflects how much relevant policy was retrieved. It is not a prediction of the planning outcome.
      </p>
    </div>
  );
}
