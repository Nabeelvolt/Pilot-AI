'use client';
import { useEffect, useState } from 'react';

const STEPS = [
  "Reading your application...",
  "Embedding query locally...",
  "Searching policy library...",
  "Retrieving relevant clauses...",
  "Generating compliance analysis...",
  "Verifying citations..."
];

export default function ProgressSteps() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Simulate progress
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < STEPS.length - 1) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 2500); // Progress every 2.5s
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 flex flex-col items-center justify-center min-h-[400px]">
      <div className="w-16 h-16 border-4 border-brand-ice border-t-brand-teal rounded-full animate-spin mb-8"></div>
      
      <div className="space-y-4 w-full max-w-md">
        {STEPS.map((step, idx) => {
          const isPast = idx < currentStep;
          const isCurrent = idx === currentStep;
          
          return (
            <div key={idx} className={`flex items-center gap-3 transition-opacity duration-500 ${isPast || isCurrent ? 'opacity-100' : 'opacity-30'}`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isPast ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-brand-sky text-white animate-pulse' : 'bg-slate-200 text-slate-500'}`}>
                {isPast ? '✓' : idx + 1}
              </div>
              <span className={`font-medium ${isPast ? 'text-emerald-700' : isCurrent ? 'text-brand-sky' : 'text-slate-500'}`}>
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
