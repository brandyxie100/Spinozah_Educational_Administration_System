'use client';

/**
 * TanStack Query hooks for student list/create/update (AIJOB-41).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createStudent,
  listStudents,
  updateStudent,
  type StudentCreateInput,
  type StudentUpdateInput,
} from '@/lib/api/students';

export const studentsQueryKey = ['students'] as const;

/** Load paginated students from FastAPI via the typed API client. */
export function useStudentsList(options?: { page?: number; pageSize?: number }) {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 20;

  return useQuery({
    queryKey: [...studentsQueryKey, page, pageSize],
    queryFn: () => listStudents({ page, pageSize }),
  });
}

/** Create a student and invalidate the students list cache. */
export function useCreateStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: StudentCreateInput) => createStudent(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: studentsQueryKey });
    },
  });
}

/** Update a student and invalidate the students list cache. */
export function useUpdateStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      studentId,
      input,
    }: {
      studentId: string;
      input: StudentUpdateInput;
    }) => updateStudent(studentId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: studentsQueryKey });
    },
  });
}
