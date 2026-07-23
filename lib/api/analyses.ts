/**
 * Typed FastAPI client for persisted exam/essay analyses (AIJOB-68).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type AnalysisKind = 'exam' | 'essay';

export type AnalysisRecord = {
  id: string;
  tenant_id: string;
  kind: AnalysisKind | string;
  student_id: string | null;
  student_name: string | null;
  title: string | null;
  payload: Record<string, unknown>;
};

export type AnalysisCreateInput = {
  kind: AnalysisKind;
  payload: Record<string, unknown>;
  student_id?: string | null;
};

function analysesBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/analyses`;
}

/** Persist an exam or essay analysis report. */
export async function createAnalysis(
  input: AnalysisCreateInput,
): Promise<AnalysisRecord> {
  return apiRequest<AnalysisRecord>(analysesBaseUrl(), {
    method: 'POST',
    body: JSON.stringify({
      kind: input.kind,
      payload: input.payload,
      student_id: input.student_id ?? null,
    }),
  });
}

/** List analyses with optional filters. */
export async function listAnalyses(options?: {
  kind?: AnalysisKind;
  studentId?: string;
}): Promise<AnalysisRecord[]> {
  const params = new URLSearchParams();
  if (options?.kind) {
    params.set('kind', options.kind);
  }
  if (options?.studentId) {
    params.set('student_id', options.studentId);
  }
  const query = params.toString();
  const url = query ? `${analysesBaseUrl()}?${query}` : analysesBaseUrl();
  return apiRequest<AnalysisRecord[]>(url);
}

/** Fetch one analysis by id. */
export async function getAnalysis(analysisId: string): Promise<AnalysisRecord> {
  return apiRequest<AnalysisRecord>(`${analysesBaseUrl()}/${analysisId}`);
}
