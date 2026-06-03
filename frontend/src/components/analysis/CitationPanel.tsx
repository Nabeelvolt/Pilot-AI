'use client';
import { Citation } from '@/lib/types';
import Badge from '../ui/Badge';

interface Props {
  citationId: string | null;
  chunks: Citation[];
  onClose: () => void;
}

export default function CitationPanel({ citationId, chunks, onClose }: Props) {
  const citation = citationId ? chunks.find(c => c.chunk_id === citationId) : null;

  return (
    <div className="h-full w-full bg-white shadow-2xl border-l border-slate-200 flex flex-col">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
        <h2 className="font-bold text-slate-800">Source Verification</h2>
        <button 
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 p-1"
        >
          ✕
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        {citation ? (
          <div className="space-y-6">
            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Document</div>
              <div className="font-medium text-slate-900">{citation.document_title}</div>
              <div className="mt-2"><Badge>{citation.doc_type}</Badge></div>
            </div>

            <div className="grid grid-cols-2 gap-4 border-y border-slate-100 py-4">
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Policy Ref</div>
                <div className="font-medium text-slate-800">{citation.policy_reference || 'N/A'}</div>
              </div>
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Page</div>
                <div className="font-medium text-slate-800">{citation.page_number || 'N/A'}</div>
              </div>
            </div>

            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex justify-between items-center">
                <span>Retrieved Text</span>
                <Badge variant="info">Relevance: {(citation.relevance * 100).toFixed(0)}%</Badge>
              </div>
              <blockquote className="bg-brand-ice/50 border-l-4 border-brand-sky p-4 text-sm text-slate-800 rounded-r whitespace-pre-wrap leading-relaxed">
                {citation.text}
              </blockquote>
            </div>
          </div>
        ) : (
          <div className="text-slate-500 text-center mt-12">
            Citation {citationId} not found in retrieved context.
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-50 border-t border-slate-200 text-xs text-slate-500">
        This text was retrieved by PILOT-AI's local semantic search. The AI used this passage to assess compliance.
      </div>
    </div>
  );
}
