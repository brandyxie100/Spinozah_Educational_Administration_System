/**
 * Typed FastAPI client helpers for attendance check-in and leave workflow.
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type AttendanceRecord = {
  id: string;
  tenant_id: string;
  schedule_id: string;
  student_id: string;
  enrolment_id: string;
  status: 'pending_confirmation' | 'present' | 'absent' | string;
  remaining_lessons: number | null;
};

export type LeaveRequest = {
  id: string;
  tenant_id: string;
  student_id: string;
  enrolment_id: string;
  leave_date: string;
  kind: 'sick' | 'personal' | string;
  reason: string | null;
  status: 'pending' | 'approved' | 'rejected' | string;
  is_free: boolean | null;
  extension_days_applied: number;
};

export type LeaveUsage = {
  student_id: string;
  enrolment_id: string;
  approved_count: number;
  free_used: number;
  free_remaining: number;
  free_limit: number;
};

export type AttendanceCheckInInput = {
  schedule_id: string;
  enrolment_id?: string;
};

export type LeaveRequestCreateInput = {
  student_id: string;
  leave_date: string;
  kind: 'sick' | 'personal';
  reason?: string;
  enrolment_id?: string;
};

function attendanceBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/attendance`;
}

/**
 * List attendance records (optional status / student filters).
 */
export async function listAttendance(options?: {
  status?: string;
  studentId?: string;
  limit?: number;
}): Promise<AttendanceRecord[]> {
  const params = new URLSearchParams();
  if (options?.status) {
    params.set('status', options.status);
  }
  if (options?.studentId) {
    params.set('student_id', options.studentId);
  }
  if (options?.limit !== undefined) {
    params.set('limit', String(options.limit));
  }
  const query = params.toString();
  const url = query ? `${attendanceBaseUrl()}?${query}` : attendanceBaseUrl();
  return apiRequest<AttendanceRecord[]>(url);
}

/** Create a pending check-in for a schedule. */
export async function checkInAttendance(
  input: AttendanceCheckInInput,
): Promise<AttendanceRecord> {
  return apiRequest<AttendanceRecord>(`${attendanceBaseUrl()}/check-in`, {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

/** Teacher confirms present or absent. */
export async function confirmAttendance(
  attendanceId: string,
  outcome: 'present' | 'absent',
): Promise<AttendanceRecord> {
  return apiRequest<AttendanceRecord>(
    `${attendanceBaseUrl()}/${attendanceId}/confirm`,
    {
      method: 'POST',
      body: JSON.stringify({ outcome }),
    },
  );
}

/** List leave requests for frontdesk. */
export async function listLeaveRequests(options?: {
  status?: string;
  studentId?: string;
  limit?: number;
}): Promise<LeaveRequest[]> {
  const params = new URLSearchParams();
  if (options?.status) {
    params.set('status', options.status);
  }
  if (options?.studentId) {
    params.set('student_id', options.studentId);
  }
  if (options?.limit !== undefined) {
    params.set('limit', String(options.limit));
  }
  const query = params.toString();
  const url = query
    ? `${attendanceBaseUrl()}/leave-requests?${query}`
    : `${attendanceBaseUrl()}/leave-requests`;
  return apiRequest<LeaveRequest[]>(url);
}

/** Submit a leave request. */
export async function createLeaveRequest(
  input: LeaveRequestCreateInput,
): Promise<LeaveRequest> {
  return apiRequest<LeaveRequest>(`${attendanceBaseUrl()}/leave-requests`, {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

/** Approve a pending leave request. */
export async function approveLeaveRequest(
  leaveId: string,
): Promise<LeaveRequest> {
  return apiRequest<LeaveRequest>(
    `${attendanceBaseUrl()}/leave-requests/${leaveId}/approve`,
    { method: 'POST' },
  );
}

/** Reject a pending leave request. */
export async function rejectLeaveRequest(leaveId: string): Promise<LeaveRequest> {
  return apiRequest<LeaveRequest>(
    `${attendanceBaseUrl()}/leave-requests/${leaveId}/reject`,
    { method: 'POST' },
  );
}

/** Free-leave usage for a student's active enrolment. */
export async function getLeaveUsage(studentId: string): Promise<LeaveUsage> {
  const params = new URLSearchParams({ student_id: studentId });
  return apiRequest<LeaveUsage>(
    `${attendanceBaseUrl()}/leave-usage?${params.toString()}`,
  );
}
