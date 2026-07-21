/**
 * Typed FastAPI helpers for teachers and teacher timetable (AIJOB-44).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type Teacher = {
  id: string;
  tenant_id: string;
  full_name: string;
  email: string | null;
  user_id: string | null;
  is_active: boolean;
};

export type TeacherListResponse = {
  items: Teacher[];
  page: number;
  page_size: number;
  total: number;
};

export type TimetableDisplayStatus =
  | 'in_progress'
  | 'absent'
  | 'starting_soon'
  | 'upcoming'
  | 'completed';

export type TeacherScheduleSlot = {
  schedule_id: string;
  student_id: string;
  student_name: string | null;
  classroom: string | null;
  starts_at: string;
  ends_at: string;
  status: string;
  display_status: TimetableDisplayStatus;
};

export type TeacherScheduleResponse = {
  teacher_id: string;
  range_start: string;
  range_end: string;
  items: TeacherScheduleSlot[];
};

/** List teachers for the timetable picker. */
export async function listTeachers(options?: {
  page?: number;
  pageSize?: number;
}): Promise<TeacherListResponse> {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 50;
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return apiRequest<TeacherListResponse>(
    `${getApiBaseUrl()}/api/v1/teachers?${params.toString()}`,
  );
}

/** Fetch expanded schedule slots for a teacher over a date range. */
export async function getTeacherSchedule(options: {
  teacherId: string;
  rangeStart: string;
  rangeEnd: string;
}): Promise<TeacherScheduleResponse> {
  const params = new URLSearchParams({
    range_start: options.rangeStart,
    range_end: options.rangeEnd,
  });
  return apiRequest<TeacherScheduleResponse>(
    `${getApiBaseUrl()}/api/v1/teachers/${options.teacherId}/schedule?${params.toString()}`,
  );
}
