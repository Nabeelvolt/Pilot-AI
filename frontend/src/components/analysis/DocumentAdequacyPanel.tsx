import React, { useState, useEffect } from 'react';
import { API_BASE } from '@/lib/api';

interface DocumentAssessment {
  doc_id: string;
  document_title: string;
  doc_category: string;
  is_adequate: boolean;
  summary: string;
  issues: string[];
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
        // We'll call the endpoint that returns validation and assessments
        const res = await fetch(`${API_BASE}/document-analysis/${analysisId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.error) {
            throw new Error(data.error);
          }
          setValidationResult(data.validation);
          setAssessments(data.assessments || []);
        } else {
          // If the get endpoint doesn't exist yet, we might need to call validate?
          // The prompt says GET /api/document-analysis/{analysis_id} should return both.
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
      <div className="mb-8">
        <h3 className="text-lg font-bold text-slate-800 mb-3">Validation Checklist</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-600 border border-slate-200 rounded-lg overflow-hidden">
            <thead className="text-xs text-slate-700 bg-slate-50 border-b border-slate-200 uppercase">
              <tr>
                <th scope="col" className="px-4 py-3">Document</th>
                <th scope="col" className="px-4 py-3">Requirement</th>
                <th scope="col" className="px-4 py-3 text-center">Required</th>
                <th scope="col" className="px-4 py-3 text-center">Submitted</th>
                <th scope="col" className="px-4 py-3 text-center">Adequate</th>
              </tr>
            </thead>
            <tbody>
              {validationResult.required_documents?.map((req, idx) => (
                <tr key={idx} className="bg-white border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {req.document_name}
                    {req.notes && <p className="text-xs text-slate-500 font-normal mt-1">{req.notes}</p>}
                  </td>
                  <td className="px-4 py-3 text-xs">{req.requirement_type}</td>
                  <td className="px-4 py-3 text-center">
                    {req.required ? (
                      <span className="text-green-600 font-bold">✓</span>
                    ) : (
                      <span className="text-slate-400 font-bold">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {req.required ? (
                      req.present ? (
                        <span className="text-green-600 font-bold">✓</span>
                      ) : (
                        <span className="text-red-600 font-bold">✗</span>
                      )
                    ) : (
                      <span className="text-slate-400 font-bold">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {req.required && req.present ? (
                      req.adequate === true ? (
                        <span className="text-green-600 font-bold">✓</span>
                      ) : req.adequate === false ? (
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
            <div key={assessment.doc_id} className="border border-slate-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold text-slate-800">{assessment.document_title}</h4>
                  <span className="text-xs text-slate-500">{assessment.doc_category}</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-bold ${assessment.is_adequate ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                  {assessment.is_adequate ? 'Adequate' : 'Issues Found'}
                </span>
              </div>
              
              <p className="text-sm text-slate-600 mb-3">{assessment.summary}</p>
              
              {assessment.issues && assessment.issues.length > 0 && (
                <div className="bg-amber-50 p-3 rounded border border-amber-100">
                  <h5 className="text-xs font-semibold text-amber-800 mb-1">Identified Issues:</h5>
                  <ul className="list-disc pl-4 text-xs text-amber-700">
                    {assessment.issues.map((issue, idx) => (
                      <li key={idx}>{issue}</li>
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
