'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import TopBar from '@/components/layout/TopBar';
import StatusPill from '@/components/ui/StatusPill';
import { checkHealth, getAnalysisHistory, getDocuments } from '@/lib/api';
import { AnalysisHistoryRecord, DocumentRecord } from '@/lib/types';

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);
  const [history, setHistory] = useState<AnalysisHistoryRecord[]>([]);
  const [docs, setDocs] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    Promise.all([
      checkHealth().catch(() => null),
      getAnalysisHistory().catch(() => []),
      getDocuments().catch(() => [])
    ]).then(([h, hist, d]) => {
      if (h) setHealth(h);
      if (hist) setHistory(hist);
      if (d) setDocs(d);
    });
  }, []);

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-50">
      <TopBar title="Dashboard" />
      
      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        
        {/* Quick Start */}
        <div className="bg-brand-navy rounded-xl shadow-lg p-8 text-white flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold mb-2 text-brand-ice">Welcome to PILOT-AI Demo</h2>
            <p className="text-slate-300 max-w-xl">
              This is a zero-cost focus group prototype of an AI-powered UK planning decision-support assistant.
            </p>
          </div>
          <Link href="/analyse" className="bg-brand-teal hover:bg-brand-sky transition-colors text-white font-bold py-3 px-6 rounded-lg shadow-md whitespace-nowrap">
            Analyse a New Application &rarr;
          </Link>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <p className="text-sm font-medium text-slate-500 mb-1">Applications Analysed</p>
            <p className="text-3xl font-bold text-slate-800">{history.length}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <p className="text-sm font-medium text-slate-500 mb-1">Policy Documents</p>
            <p className="text-3xl font-bold text-slate-800">{docs.length}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <p className="text-sm font-medium text-slate-500 mb-1">Sections Searchable</p>
            <p className="text-3xl font-bold text-slate-800">{health?.total_chunks_indexed || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <p className="text-sm font-medium text-slate-500 mb-1">AI Model</p>
            <div className="flex items-center gap-2">
              <p className="text-xl font-bold text-slate-800 truncate" title="Groq Llama 3.3 70B">Llama 3.3 70B</p>
              <span className="bg-emerald-100 text-emerald-800 text-xs px-2 py-0.5 rounded font-medium">Free</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Analyses Table */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-800">Recent Analyses</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500 font-medium">
                  <tr>
                    <th className="px-6 py-3">Ref</th>
                    <th className="px-6 py-3">Site</th>
                    <th className="px-6 py-3">Type</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((record) => (
                    <tr key={record.analysis_id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">{record.application_ref}</td>
                      <td className="px-6 py-4 text-slate-600 truncate max-w-[200px]">{record.site_address}</td>
                      <td className="px-6 py-4 text-slate-600">{record.application_type}</td>
                      <td className="px-6 py-4"><StatusPill status={record.overall_status} /></td>
                      <td className="px-6 py-4">
                        <div className="w-24 bg-slate-200 rounded-full h-1.5 mt-1">
                          <div 
                            className={`h-1.5 rounded-full ${record.overall_confidence > 0.7 ? 'bg-emerald-500' : 'bg-amber-500'}`} 
                            style={{ width: `${Math.round(record.overall_confidence * 100)}%` }}
                          ></div>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                        No analyses found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-800">System Status</h2>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-600">AI Model</span>
                <div className="text-right">
                  <div className="font-medium text-slate-900">Groq llama-3.3-70b</div>
                  <div className="text-xs text-emerald-600 font-medium">✓ Free</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Fallback</span>
                <div className="text-right">
                  <div className="font-medium text-slate-900">Gemini 1.5 Flash</div>
                  <div className="text-xs text-emerald-600 font-medium">✓ Free</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Embeddings</span>
                <div className="text-right">
                  <div className="font-medium text-slate-900">all-MiniLM-L6-v2</div>
                  <div className="text-xs text-emerald-600 font-medium">✓ Free (Local CPU)</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Vector DB</span>
                <div className="text-right">
                  <div className="font-medium text-slate-900">ChromaDB</div>
                  <div className="text-xs text-emerald-600 font-medium">✓ Free (Local)</div>
                </div>
              </div>
              
              <div className="pt-4 mt-4 border-t border-slate-100 flex justify-between items-center">
                <span className="font-bold text-slate-800">Running Cost</span>
                <span className="font-bold text-emerald-600 text-lg">£0.00/month</span>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
