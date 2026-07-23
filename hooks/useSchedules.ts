'use client';

/**
 * TanStack Query hooks for schedule create (AIJOB-64).
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createSchedule,
  type ScheduleCreateInput,
} from '@/lib/api/schedules';

export const schedulesQueryKey = ['schedules'] as const;

/** Create a schedule; callers keep returned rows for confirmation UI. */
export function useCreateSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ScheduleCreateInput) => createSchedule(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: schedulesQueryKey });
    },
  });
}
