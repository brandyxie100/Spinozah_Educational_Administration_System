/**
 * Typed FastAPI client helpers for parent portal (AIJOB-58).
 */

import {
  apiRequest,
  apiRequestBlob,
  getApiBaseUrl,
} from '@/lib/api/client';

export type ParentUser = {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: string;
};

export type ParentTokenResponse = {
  access_token: string;
  token_type: string;
  user: ParentUser;
};

export type MagicLinkRequestResponse = {
  detail: string;
  magic_url: string | null;
};

export type LinkedStudent = {
  id: string;
  full_name: string;
  email: string | null;
  is_active: boolean;
};

export type ParentEnrolment = {
  id: string;
  student_id: string;
  status: string;
  total_lessons: number;
  completed_lessons: number;
  remaining_lessons: number;
  extension_days: number;
};

export type ParentAttendance = {
  id: string;
  schedule_id: string;
  student_id: string;
  enrolment_id: string;
  status: string;
};

export type ParentInvoice = {
  id: string;
  student_id: string;
  semester_label: string;
  subtotal: string;
  credit: string;
  final_amount: string;
  status: string;
};

export type ParentDashboardReport = {
  student_id: string;
  remaining_lessons: number | null;
  total_lessons: number | null;
  completed_lessons: number | null;
  attendance_count: number;
  invoice_count: number;
  unpaid_invoice_count: number;
};

function parentBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/parent`;
}

/** Request a magic-link email (may return magic_url when API debug is on). */
export async function requestMagicLink(input: {
  tenantSlug: string;
  email: string;
}): Promise<MagicLinkRequestResponse> {
  return apiRequest<MagicLinkRequestResponse>(
    `${parentBaseUrl()}/magic-link/request`,
    {
      method: 'POST',
      body: JSON.stringify({
        tenant_slug: input.tenantSlug,
        email: input.email,
      }),
    },
  );
}

/** Exchange a magic-link token for an access JWT. */
export async function consumeMagicLink(
  token: string,
): Promise<ParentTokenResponse> {
  return apiRequest<ParentTokenResponse>(
    `${parentBaseUrl()}/magic-link/consume`,
    {
      method: 'POST',
      body: JSON.stringify({ token }),
    },
  );
}

/** List students linked to the authenticated parent. */
export async function listLinkedStudents(): Promise<LinkedStudent[]> {
  return apiRequest<LinkedStudent[]>(`${parentBaseUrl()}/students`);
}

/** Enrolment balance for a linked student. */
export async function getStudentEnrolment(
  studentId: string,
): Promise<ParentEnrolment> {
  return apiRequest<ParentEnrolment>(
    `${parentBaseUrl()}/students/${studentId}/enrolment`,
  );
}

/** Attendance history for a linked student. */
export async function listStudentAttendance(
  studentId: string,
): Promise<ParentAttendance[]> {
  return apiRequest<ParentAttendance[]>(
    `${parentBaseUrl()}/students/${studentId}/attendance`,
  );
}

/** Invoices for a linked student. */
export async function listStudentInvoices(
  studentId: string,
): Promise<ParentInvoice[]> {
  return apiRequest<ParentInvoice[]>(
    `${parentBaseUrl()}/students/${studentId}/invoices`,
  );
}

/** Aggregate dashboard report for a linked student. */
export async function getStudentDashboardReport(
  studentId: string,
): Promise<ParentDashboardReport> {
  return apiRequest<ParentDashboardReport>(
    `${parentBaseUrl()}/students/${studentId}/report`,
  );
}

/** Download a linked student's invoice PDF. */
export async function downloadStudentInvoicePdf(
  studentId: string,
  invoiceId: string,
): Promise<Blob> {
  return apiRequestBlob(
    `${parentBaseUrl()}/students/${studentId}/invoices/${invoiceId}/pdf`,
  );
}
