'use client';
import { useState, useEffect } from 'react';
import TopBar from '@/components/layout/TopBar';
import ApplicationForm from '@/components/analysis/ApplicationForm';
import ProgressSteps from '@/components/analysis/ProgressSteps';
import AnalysisResult from '@/components/analysis/AnalysisResult';
import CitationPanel from '@/components/analysis/CitationPanel';
import { analyseApplication } from '@/lib/api';
import { AnalysisRequest, AnalysisResponse } from '@/lib/types';

export default function AnalysePage() {
  const [isAnalysing, setIsAnalysing] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeCitationId, setActiveCitationId] = useState<string | null>(null);

  // Handle escape key to close citation panel
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setActiveCitationId(null);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  const handleAnalyse = async (data: AnalysisRequest) => {
    setIsAnalysing(true);
    setResult(null);
    setError(null);
    setActiveCitationId(null);

    try {
      const res = await analyseApplication(data);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis');
    } finally {
      setIsAnalysing(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-50 relative overflow-hidden">
      <TopBar title="Analyse Application" />
      
      <div className="flex-1 overflow-y-auto p-8 relative">
        <div className="max-w-4xl mx-auto space-y-8 pb-12">
          
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
              <h3 className="font-bold text-red-800">Analysis Failed</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          )}

          {!isAnalysing && !result && (
            <ApplicationForm onSubmit={handleAnalyse} disabled={isAnalysing} />
          )}

          {isAnalysing && (
            <ProgressSteps />
          )}

          {result && !isAnalysing && (
            <>
              <div className="flex justify-between items-center mb-4 print:hidden">
                <button 
                  onClick={() => setResult(null)}
                  className="text-brand-sky hover:text-brand-navy font-medium text-sm flex items-center gap-1 transition-colors"
                >
                  &larr; Start New Analysis
                </button>
              </div>
              <AnalysisResult 
                result={result} 
                onViewCitation={setActiveCitationId} 
              />
            </>
          )}

        </div>
      </div>

      {/* Citation Slide-out Panel */}
      <div className={`absolute inset-0 transition-opacity z-40 ${activeCitationId ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
        <div 
          className="absolute inset-0 bg-slate-900/20" 
          onClick={() => setActiveCitationId(null)}
        />
        <div className={`absolute inset-y-0 right-0 w-full max-w-md transform transition-transform duration-300 ease-in-out ${activeCitationId ? 'translate-x-0' : 'translate-x-full'}`}>
          <CitationPanel 
            citationId={activeCitationId} 
            chunks={result?.retrieved_chunks || []} 
            onClose={() => setActiveCitationId(null)} 
          />
        </div>
      </div>

    </div>
  );
}
