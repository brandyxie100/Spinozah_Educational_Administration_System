'use client';

/**
 * TanStack Query hooks for teacher timetable (AIJOB-44).
 */

import { useQuery } from '@tanstack/react-query';
import { getTeacherSchedule, listTeachers } from '@/lib/api/teachers';

export const teachersQueryKey = ['teachers'] as const;
export const teacherScheduleQueryKey = ['teacher-schedule'] as const;

/** Load teachers for the timetable picker. */
export function useTeachersList(options?: { page?: number; pageSize?: number }) {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 50;
  return useQuery({
    queryKey: [...teachersQueryKey, page, pageSize],
    queryFn: () => listTeachers({ page, pageSize }),
  });
}

/** Load a teacher's expanded schedule for a date range. */
export function useTeacherSchedule(options: {
  teacherId: string | null;
  rangeStart: string;
  rangeEnd: string;
}) {
  return useQuery({
    queryKey: [
      ...teacherScheduleQueryKey,
      options.teacherId,
      options.rangeStart,
      options.rangeEnd,
    ],
    queryFn: () =>
      getTeacherSchedule({
        teacherId: options.teacherId as string,
        rangeStart: options.rangeStart,
        rangeEnd: options.rangeEnd,
      }),
    enabled: Boolean(options.teacherId),
  });
}
