'use client';
import { useState, useEffect } from 'react';
import TopBar from '@/components/layout/TopBar';
import ApplicationForm from '@/components/analysis/ApplicationForm';
import ProgressSteps from '@/components/analysis/ProgressSteps';
import AnalysisResult from '@/components/analysis/AnalysisResult';
import CitationPanel from '@/components/analysis/CitationPanel';
import DocumentAdequacyPanel from '@/components/analysis/DocumentAdequacyPanel';
import { analyseApplication } from '@/lib/api';
import { AnalysisRequest, AnalysisResponse } from '@/lib/types';

export default function AnalysePage() {
  const [isAnalysing, setIsAnalysing] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeCitationId, setActiveCitationId] = useState<string | null>(null);
  const [resultsTab, setResultsTab] = useState<'compliance' | 'documents'>('compliance');
  const [formData, setFormData] = useState<AnalysisRequest | null>(null);

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
    setFormData(data);
    setResultsTab('compliance');

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

          {result && !isAnalysing && formData && (
            <>
              <div className="flex justify-between items-center mb-4 print:hidden">
                <button 
                  onClick={() => {
                    setResult(null);
                    setFormData(null);
                  }}
                  className="text-brand-sky hover:text-brand-navy font-medium text-sm flex items-center gap-1 transition-colors"
                >
                  &larr; Start New Analysis
                </button>
              </div>
              
              <div>
                {/* Results tab bar */}
                <div className="flex border-b border-gray-200 mb-6">
                  {[
                    { key: 'compliance', label: '📋 Policy Compliance' },
                    { key: 'documents', label: '📄 Document Adequacy & Validation' },
                  ].map(tab => (
                    <button
                      key={tab.key}
                      onClick={() => setResultsTab(tab.key as 'compliance' | 'documents')}
                      className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                        resultsTab === tab.key
                          ? 'border-brand-teal text-brand-teal'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Policy Compliance tab — existing component, untouched */}
                {resultsTab === 'compliance' && (
                  <AnalysisResult 
                    result={result} 
                    onViewCitation={setActiveCitationId} 
                  />
                )}

                {/* Document Adequacy tab — new component */}
                {resultsTab === 'documents' && (
                  <DocumentAdequacyPanel
                    analysisId={formData.analysis_id || result.analysis_id}
                    applicationType={formData.application_type}
                    siteConstraints={formData.site_constraints || []}
                  />
                )}
              </div>
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
