'use client';

/**
 * TanStack Query hooks for attendance check-in and leave workflow.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  approveLeaveRequest,
  checkInAttendance,
  confirmAttendance,
  createLeaveRequest,
  getLeaveUsage,
  listAttendance,
  listLeaveRequests,
  rejectLeaveRequest,
  type AttendanceCheckInInput,
  type LeaveRequestCreateInput,
} from '@/lib/api/attendance';

export const attendanceQueryKey = ['attendance'] as const;
export const leaveRequestsQueryKey = ['leave-requests'] as const;
export const leaveUsageQueryKey = ['leave-usage'] as const;

/** Load attendance rows (default: pending confirmation). */
export function useAttendanceList(options?: {
  status?: string;
  studentId?: string;
}) {
  return useQuery({
    queryKey: [
      ...attendanceQueryKey,
      options?.status ?? 'all',
      options?.studentId ?? 'all',
    ],
    queryFn: () =>
      listAttendance({
        status: options?.status,
        studentId: options?.studentId,
      }),
  });
}

/** Load leave requests (default: all). */
export function useLeaveRequestsList(options?: {
  status?: string;
  studentId?: string;
}) {
  return useQuery({
    queryKey: [
      ...leaveRequestsQueryKey,
      options?.status ?? 'all',
      options?.studentId ?? 'all',
    ],
    queryFn: () =>
      listLeaveRequests({
        status: options?.status,
        studentId: options?.studentId,
      }),
  });
}

/** Load free-leave usage for a student when an id is selected. */
export function useLeaveUsage(studentId: string | null) {
  return useQuery({
    queryKey: [...leaveUsageQueryKey, studentId],
    queryFn: () => getLeaveUsage(studentId as string),
    enabled: Boolean(studentId),
  });
}

/** Create a pending check-in. */
export function useCheckInAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: AttendanceCheckInInput) => checkInAttendance(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: attendanceQueryKey });
    },
  });
}

/** Confirm present/absent. */
export function useConfirmAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      attendanceId,
      outcome,
    }: {
      attendanceId: string;
      outcome: 'present' | 'absent';
    }) => confirmAttendance(attendanceId, outcome),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: attendanceQueryKey });
    },
  });
}

/** Create a leave request. */
export function useCreateLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: LeaveRequestCreateInput) => createLeaveRequest(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveRequestsQueryKey });
      await queryClient.invalidateQueries({ queryKey: leaveUsageQueryKey });
    },
  });
}

/** Approve leave. */
export function useApproveLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (leaveId: string) => approveLeaveRequest(leaveId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveRequestsQueryKey });
      await queryClient.invalidateQueries({ queryKey: leaveUsageQueryKey });
    },
  });
}

/** Reject leave. */
export function useRejectLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (leaveId: string) => rejectLeaveRequest(leaveId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveRequestsQueryKey });
    },
  });
}
