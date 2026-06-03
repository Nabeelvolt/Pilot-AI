export interface AnalysisRequest {
  application_ref?: string;
  site_address?: string;
  application_type: string;
  proposed_development: string;
  site_constraints?: string[];
}

export interface PolicyFinding {
  policy_reference: string;
  document_title: string;
  finding: string;
  confidence: number;
  explanation: string;
  citation_id: string;
}

export interface KeyIssue {
  severity: string;
  policy_reference: string;
  issue: string;
  citation_id: string;
}

export interface Citation {
  chunk_id: string;
  text: string;
  relevance: number;
  doc_type: string;
  document_title: string;
  policy_reference: string;
  section_title: string;
  page_number: string;
  lpa_code: string;
  date_effective: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  overall_status: string;
  overall_confidence: number;
  summary: string;
  policy_findings: PolicyFinding[];
  key_issues: KeyIssue[];
  recommended_actions: string[];
  uncertainty_flags: string[];
  retrieved_chunks: Citation[];
  processing_time_seconds: number;
}

export interface DocumentRecord {
  doc_id: string;
  filename: string;
  document_title: string;
  doc_type: string;
  lpa_code: string;
  chunk_count: number;
  status: string;
  created_at: string;
}

export interface AnalysisHistoryRecord {
  analysis_id: string;
  application_ref: string;
  site_address: string;
  application_type: string;
  overall_status: string;
  overall_confidence: number;
  processing_time_seconds: number;
  created_at: string;
}
