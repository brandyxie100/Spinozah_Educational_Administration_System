'use client';

/**
 * TanStack Query hooks for teachers list/CRUD and timetable (AIJOB-44/63).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createTeacher,
  getTeacherSchedule,
  listTeachers,
  updateTeacher,
  type TeacherCreateInput,
  type TeacherUpdateInput,
} from '@/lib/api/teachers';

export const teachersQueryKey = ['teachers'] as const;
export const teacherScheduleQueryKey = ['teacher-schedule'] as const;

/** Load teachers for the timetable picker / management list. */
export function useTeachersList(options?: { page?: number; pageSize?: number }) {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 50;
  return useQuery({
    queryKey: [...teachersQueryKey, page, pageSize],
    queryFn: () => listTeachers({ page, pageSize }),
  });
}

/** Create a teacher and invalidate the teachers list. */
export function useCreateTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: TeacherCreateInput) => createTeacher(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: teachersQueryKey });
    },
  });
}

/** Update a teacher and invalidate the teachers list. */
export function useUpdateTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      teacherId,
      input,
    }: {
      teacherId: string;
      input: TeacherUpdateInput;
    }) => updateTeacher(teacherId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: teachersQueryKey });
    },
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
