'use client';

/**
 * TanStack Query hooks for staff enrolment management (AIJOB-66).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createEnrolment,
  listEnrolments,
  updateEnrolment,
  type EnrolmentCreateInput,
  type EnrolmentUpdateInput,
} from '@/lib/api/enrolments';

export const enrolmentsQueryKey = ['enrolments'] as const;

/** Load enrolments, optionally for one student. */
export function useEnrolmentsList(options?: { studentId?: string | null }) {
  const studentId = options?.studentId ?? null;
  return useQuery({
    queryKey: [...enrolmentsQueryKey, studentId],
    queryFn: () =>
      listEnrolments(
        studentId ? { studentId } : undefined,
      ),
  });
}

/** Create an enrolment and invalidate lists. */
export function useCreateEnrolment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: EnrolmentCreateInput) => createEnrolment(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: enrolmentsQueryKey });
    },
  });
}

/** Update an enrolment and invalidate lists. */
export function useUpdateEnrolment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      enrolmentId,
      input,
    }: {
      enrolmentId: string;
      input: EnrolmentUpdateInput;
    }) => updateEnrolment(enrolmentId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: enrolmentsQueryKey });
    },
  });
}
