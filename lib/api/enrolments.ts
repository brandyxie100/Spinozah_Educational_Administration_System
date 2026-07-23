/**
 * Typed FastAPI client helpers for staff enrolment management (AIJOB-66).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type EnrolmentStatus = 'active' | 'completed' | 'cancelled';

export type Enrolment = {
  id: string;
  tenant_id: string;
  student_id: string;
  total_lessons: number;
  completed_lessons: number;
  remaining_lessons: number;
  extension_days: number;
  status: EnrolmentStatus | string;
};

export type EnrolmentCreateInput = {
  student_id: string;
  total_lessons: number;
};

export type EnrolmentUpdateInput = {
  total_lessons?: number;
  completed_lessons?: number;
  remaining_lessons?: number;
  status?: EnrolmentStatus;
};

function enrolmentsBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/enrolments`;
}

/** List enrolments, optionally filtered by student. */
export async function listEnrolments(options?: {
  studentId?: string;
}): Promise<Enrolment[]> {
  const params = new URLSearchParams();
  if (options?.studentId) {
    params.set('student_id', options.studentId);
  }
  const query = params.toString();
  const url = query
    ? `${enrolmentsBaseUrl()}?${query}`
    : enrolmentsBaseUrl();
  return apiRequest<Enrolment[]>(url);
}

/** Create a lesson package for a student. */
export async function createEnrolment(
  input: EnrolmentCreateInput,
): Promise<Enrolment> {
  return apiRequest<Enrolment>(enrolmentsBaseUrl(), {
    method: 'POST',
    body: JSON.stringify({
      student_id: input.student_id,
      total_lessons: input.total_lessons,
    }),
  });
}

/** Update lesson counts and/or status. */
export async function updateEnrolment(
  enrolmentId: string,
  input: EnrolmentUpdateInput,
): Promise<Enrolment> {
  return apiRequest<Enrolment>(`${enrolmentsBaseUrl()}/${enrolmentId}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  });
}
