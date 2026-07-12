import { AnalysisRequest, AnalysisResponse, DocumentRecord, AnalysisHistoryRecord } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
export const API_BASE = `${BASE_URL}/api`;

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health status');
  return res.json();
}

export async function analyseApplication(request: AnalysisRequest): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/applications/analyse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Analysis failed');
  }
  return res.json();
}

export async function getAnalysisHistory(): Promise<AnalysisHistoryRecord[]> {
  const res = await fetch(`${API_BASE}/applications/history`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function getDocuments(): Promise<DocumentRecord[]> {
  const res = await fetch(`${API_BASE}/documents/`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function uploadDocument(formData: FormData) {
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}
