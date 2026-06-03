'use client';
import { AnalysisResponse, Citation } from '@/lib/types';
import ConfidenceBar from '../ui/ConfidenceBar';
import Badge from '../ui/Badge';
import StatusPill from '../ui/StatusPill';

interface Props {
  result: AnalysisResponse;
  onViewCitation: (citationId: string) => void;
}

export default function AnalysisResult({ result, onViewCitation }: Props) {
  
  const getStatusColor = () => {
    if (result.overall_status === 'LIKELY_COMPLIANT') return 'bg-emerald-50 border-emerald-200 text-emerald-900';
    if (result.overall_status === 'REQUIRES_FURTHER_INFO') return 'bg-amber-50 border-amber-200 text-amber-900';
    if (result.overall_status === 'LIKELY_NON_COMPLIANT') return 'bg-red-50 border-red-200 text-red-900';
    return 'bg-slate-50 border-slate-200 text-slate-900';
  };

  const getFindingBadge = (finding: string) => {
    if (finding === 'COMPLIES') return <Badge variant="success">COMPLIES</Badge>;
    if (finding === 'POTENTIAL_CONFLICT') return <Badge variant="warning">POTENTIAL CONFLICT</Badge>;
    if (finding === 'NOT_APPLICABLE') return <Badge variant="default">N/A</Badge>;
    return <Badge variant="info">INSUFFICIENT INFO</Badge>;
  };

  const getSeverityBadge = (severity: string) => {
    if (severity === 'HIGH') return <Badge variant="danger">HIGH</Badge>;
    if (severity === 'MEDIUM') return <Badge variant="warning">MEDIUM</Badge>;
    return <Badge variant="info">LOW</Badge>;
  };

  return (
    <div className="space-y-6 print:space-y-4" id="analysis-report">
      
      {/* A. Overall Status Banner */}
      <div className={`rounded-xl border p-6 ${getStatusColor()}`}>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider opacity-80 mb-1">Overall Assessment</h2>
            <div className="text-2xl font-bold">{result.overall_status.replace(/_/g, ' ')}</div>
          </div>
          <div className="w-full md:w-64 bg-white/50 p-3 rounded-lg">
            <ConfidenceBar confidence={result.overall_confidence} />
          </div>
        </div>
      </div>

      {/* B. Summary paragraph */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="font-bold text-slate-800 mb-2">Executive Summary</h3>
        <p className="text-slate-700 leading-relaxed">{result.summary}</p>
      </div>

      {/* C. Policy Compliance Table */}
      {result.policy_findings.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50">
            <h3 className="font-bold text-slate-800">Policy Assessment</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                <tr>
                  <th className="px-4 py-3">Policy / Source</th>
                  <th className="px-4 py-3">Finding</th>
                  <th className="px-4 py-3">Explanation</th>
                  <th className="px-4 py-3 w-24">Citation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {result.policy_findings.map((f, i) => (
                  <tr key={i}>
                    <td className="px-4 py-3 align-top">
                      <div className="font-medium text-slate-900">{f.policy_reference}</div>
                      <div className="text-xs text-slate-500 mt-1">{f.document_title}</div>
                    </td>
                    <td className="px-4 py-3 align-top">
                      {getFindingBadge(f.finding)}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {f.explanation}
                    </td>
                    <td className="px-4 py-3 align-top">
                      {f.citation_id ? (
                        <button 
                          onClick={() => onViewCitation(f.citation_id)}
                          className="text-xs bg-slate-100 hover:bg-brand-sky hover:text-white transition-colors text-slate-600 font-medium px-2 py-1 rounded"
                        >
                          {f.citation_id} 🔍
                        </button>
                      ) : (
                        <span className="text-slate-400 text-xs">None</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* D. Key Issues panel */}
      {result.key_issues.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 border-l-4 border-l-amber-500 p-6">
          <h3 className="font-bold text-slate-800 mb-4">Key Issues Identified</h3>
          <div className="space-y-4">
            {result.key_issues.map((issue, i) => (
              <div key={i} className="flex gap-4 items-start">
                <div className="mt-0.5">{getSeverityBadge(issue.severity)}</div>
                <div>
                  <div className="font-medium text-slate-900">{issue.policy_reference}</div>
                  <p className="text-slate-700 text-sm mt-1">{issue.issue}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* E. Recommended Actions */}
      {result.recommended_actions.length > 0 && (
        <div className="bg-emerald-50 rounded-xl border border-emerald-100 p-6">
          <h3 className="font-bold text-emerald-900 mb-4">Recommended Actions</h3>
          <ol className="list-decimal pl-5 space-y-2 text-emerald-800 text-sm">
            {result.recommended_actions.map((act, i) => (
              <li key={i} className="pl-1">{act}</li>
            ))}
          </ol>
        </div>
      )}

      {/* F. Uncertainty Flags */}
      {result.uncertainty_flags.length > 0 && (
        <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
          <h4 className="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
            <span>⚠️</span> AI Uncertainty Notes
          </h4>
          <ul className="list-disc pl-5 space-y-1 text-slate-600 text-xs">
            {result.uncertainty_flags.map((flag, i) => (
              <li key={i}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end pt-4 print:hidden">
        <button 
          onClick={() => window.print()}
          className="bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 font-medium py-2 px-4 rounded shadow-sm"
        >
          🖨️ Print Report
        </button>
      </div>

      {/* G. AI Transparency Footer */}
      <div className="bg-slate-100 p-4 rounded-lg text-xs text-slate-500 mt-8 border border-slate-200">
        Generated by PILOT-AI using Groq Llama 3.3 70B. Decision-support only — planning officer must apply professional judgement. Every finding is linked to retrieved policy text. Processing time: {result.processing_time_seconds.toFixed(1)}s. Running cost for this analysis: £0.00.
      </div>
    </div>
  );
}
