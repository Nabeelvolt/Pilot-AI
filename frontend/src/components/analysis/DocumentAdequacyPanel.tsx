import React, { useState, useEffect } from 'react';
import { API_BASE } from '@/lib/api';

interface DocumentAssessment {
  assessment_id: string;
  document_category: string;
  overall_adequacy: string;
  sections_present: string[];
  sections_missing: string[];
  policy_conflicts: string[];
  recommendations: string[];
}

interface ValidationReq {
  document_name: string;
  requirement_type: string;
  required: boolean;
  present: boolean | null;
  adequate: boolean | null;
  notes?: string;
}

interface ValidationResult {
  status?: string;
  overall_status?: string;
  required_documents: ValidationReq[];
  missing_documents: string[];
  inadequate_documents?: string[];
}

interface Props {
  analysisId?: string;
  applicationType?: string;
  siteConstraints?: string[];
}

export default function DocumentAdequacyPanel({ analysisId, applicationType, siteConstraints }: Props) {
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [assessments, setAssessments] = useState<DocumentAssessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      if (!analysisId) return;
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/document-analysis/${analysisId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.error) {
            throw new Error(data.error);
          }
          setValidationResult(data.validation);
          setAssessments(data.assessments || []);
        } else {
          setError('Failed to fetch document analysis data.');
        }
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [analysisId]);

  if (loading) return <div className="p-6 text-center text-slate-500">Loading document adequacy...</div>;
  if (error) return <div className="p-6 text-center text-red-500">{error}</div>;
  if (!validationResult) return null;

  const status = validationResult.overall_status || validationResult.status || 'UNKNOWN';

  const validationStatusConfig: Record<string, { label: string; color: string; bg: string }> = {
    VALID: { label: 'Valid', color: 'text-green-700', bg: 'bg-green-100 border-green-200' },
    INVALID: { label: 'Invalid - Missing Information', color: 'text-red-700', bg: 'bg-red-100 border-red-200' },
    REQUIRES_REVIEW: { label: 'Requires Review - Inadequate Content', color: 'text-amber-700', bg: 'bg-amber-100 border-amber-200' },
    UNKNOWN: { label: 'Unknown', color: 'text-slate-700', bg: 'bg-slate-100 border-slate-200' }
  };

  const statusConfig = validationStatusConfig[status] || validationStatusConfig['UNKNOWN'];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mt-6">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Validation & Document Adequacy</h2>
      
      {/* Overall Validation Status */}
      <div className={`p-4 rounded-lg border ${statusConfig.bg} mb-6`}>
        <div className="flex items-center space-x-3">
          <h3 className={`text-lg font-bold ${statusConfig.color}`}>
            Overall Validation Status: {statusConfig.label}
          </h3>
        </div>
        
        {validationResult.missing_documents && validationResult.missing_documents.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-semibold text-red-800 mb-1">Missing Documents:</h4>
            <ul className="list-disc pl-5 text-sm text-red-700">
              {validationResult.missing_documents.map((doc, idx) => (
                <li key={idx}>{doc}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Validation Checklist Table */}
      <h3 className="text-lg font-bold text-slate-800 mb-4">Validation Checklist</h3>
      <div className="border border-slate-200 rounded-lg overflow-hidden mb-8">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">DOCUMENT</th>
                <th className="py-3 px-4">REQUIREMENT</th>
                <th className="py-3 px-4 text-center">REQUIRED</th>
                <th className="py-3 px-4 text-center">SUBMITTED</th>
                <th className="py-3 px-4 text-center">ADEQUATE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {validationResult.required_documents.map((req, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-3 px-4">
                    <div className="font-medium text-slate-800">{req.document_name}</div>
                    {req.notes && <div className="text-xs text-slate-500 mt-1">{req.notes}</div>}
                  </td>
                  <td className="py-3 px-4 text-slate-600">
                    {req.requirement_type}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {req.required ? (
                      <span className="text-green-600 font-bold">✓</span>
                    ) : (
                      <span className="text-slate-400 font-bold">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {req.required ? (
                      req.present ? (
                        <span className="text-green-600 font-bold">✓</span>
                      ) : (
                        <span className="text-red-600 font-bold">X</span>
                      )
                    ) : (
                      <span className="text-slate-400 font-bold">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {req.required && req.present ? (
                      req.adequate === true || req.adequate === 'ADEQUATE' ? (
                        <span className="text-green-600 font-bold">✓</span>
                      ) : req.adequate === false || req.adequate === 'INADEQUATE' ? (
                        <span className="text-amber-600 font-bold text-lg">!</span>
                      ) : (
                        <span className="text-slate-400 font-bold">-</span>
                      )
                    ) : (
                      <span className="text-slate-400 font-bold">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Document Assessments */}
      <h3 className="text-lg font-bold text-slate-800 mb-4">Document Assessments</h3>
      
      {assessments.length === 0 ? (
        <p className="text-sm text-slate-500 italic mb-8">No document assessments available.</p>
      ) : (
        <div className="space-y-4 mb-8">
          {assessments.map((assessment) => (
            <div key={assessment.assessment_id} className="border border-slate-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold text-slate-800">{assessment.document_category.replace(/_/g, ' ').toUpperCase()}</h4>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-bold ${assessment.overall_adequacy === 'ADEQUATE' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                  {assessment.overall_adequacy === 'ADEQUATE' ? 'Adequate' : 'Issues Found'}
                </span>
              </div>
              
              {assessment.recommendations && assessment.recommendations.length > 0 && (
                <p className="text-sm text-slate-600 mb-3">{assessment.recommendations.join(" ")}</p>
              )}
              
              {((assessment.sections_missing && assessment.sections_missing.length > 0) || (assessment.policy_conflicts && assessment.policy_conflicts.length > 0)) && (
                <div className="bg-amber-50 p-3 rounded border border-amber-100">
                  <h5 className="text-xs font-semibold text-amber-800 mb-1">Identified Issues:</h5>
                  <ul className="list-disc pl-4 text-xs text-amber-700">
                    {assessment.sections_missing?.map((issue, idx) => (
                      <li key={`missing-${idx}`}>Missing: {issue}</li>
                    ))}
                    {assessment.policy_conflicts?.map((issue, idx) => (
                      <li key={`conflict-${idx}`}>Conflict: {issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Source Attribution */}
      <div className="mt-8 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-500 italic">
          Validation requirements sourced from: GOV.UK National Validation Requirements (updated May 2025) and Central Lincolnshire Local Validation Lists (City of Lincoln / North Kesteven / West Lindsey — adopted May 2024).
        </p>
      </div>
    </div>
  );
}
