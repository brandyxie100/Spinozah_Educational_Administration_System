/**
 * Typed FastAPI client helpers for lesson schedules (AIJOB-64).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type Schedule = {
  id: string;
  tenant_id: string;
  teacher_id: string;
  student_id: string;
  classroom: string | null;
  starts_at: string;
  ends_at: string;
  status: string;
  is_recurring: boolean;
  recurrence_weekday: number | null;
  recurrence_until: string | null;
};

export type ScheduleCreateInput = {
  teacher_id: string;
  student_id: string;
  starts_at: string;
  ends_at: string;
  classroom?: string | null;
  is_recurring?: boolean;
  recurrence_until?: string | null;
};

function schedulesBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/schedules`;
}

/** Create a lesson schedule (409 on conflict). */
export async function createSchedule(
  input: ScheduleCreateInput,
): Promise<Schedule> {
  return apiRequest<Schedule>(schedulesBaseUrl(), {
    method: 'POST',
    body: JSON.stringify({
      teacher_id: input.teacher_id,
      student_id: input.student_id,
      starts_at: input.starts_at,
      ends_at: input.ends_at,
      classroom: input.classroom ?? null,
      is_recurring: input.is_recurring ?? false,
      recurrence_until: input.recurrence_until ?? null,
    }),
  });
}
