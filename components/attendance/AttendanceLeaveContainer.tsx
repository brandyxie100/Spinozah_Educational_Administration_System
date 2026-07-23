'use client';

/**
 * Container: wires attendance/leave hooks, students, and timetable slots.
 */

import { useState } from 'react';
import { AttendanceLeaveView } from '@/components/attendance/AttendanceLeaveView';
import {
  useApproveLeaveRequest,
  useAttendanceList,
  useCheckInAttendance,
  useConfirmAttendance,
  useCreateLeaveRequest,
  useLeaveRequestsList,
  useLeaveUsage,
  useRejectLeaveRequest,
} from '@/hooks/useAttendance';
import { useStudentsList } from '@/hooks/useStudents';
import { useTeacherSchedule, useTeachersList } from '@/hooks/useTeacherSchedule';
import { ApiError } from '@/lib/api';

function todayIsoDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Something went wrong loading attendance';
}

/** Attendance & Leave module container (data + mutations). */
export function AttendanceLeaveContainer() {
  const [usageStudentId, setUsageStudentId] = useState('');
  const [checkInTeacherId, setCheckInTeacherId] = useState('');
  const [checkInDate, setCheckInDate] = useState(todayIsoDate);

  const studentsQuery = useStudentsList({ page: 1, pageSize: 100 });
  const teachersQuery = useTeachersList({ page: 1, pageSize: 100 });
  const scheduleQuery = useTeacherSchedule({
    teacherId: checkInTeacherId || null,
    rangeStart: checkInDate,
    rangeEnd: checkInDate,
  });
  const attendanceQuery = useAttendanceList({
    status: 'pending_confirmation',
  });
  const leaveQuery = useLeaveRequestsList();
  const usageQuery = useLeaveUsage(usageStudentId || null);

  const checkInMutation = useCheckInAttendance();
  const confirmMutation = useConfirmAttendance();
  const createLeaveMutation = useCreateLeaveRequest();
  const approveMutation = useApproveLeaveRequest();
  const rejectMutation = useRejectLeaveRequest();

  const mutationError =
    checkInMutation.error ??
    confirmMutation.error ??
    createLeaveMutation.error ??
    approveMutation.error ??
    rejectMutation.error;
  const queryError =
    studentsQuery.error ??
    teachersQuery.error ??
    scheduleQuery.error ??
    attendanceQuery.error ??
    leaveQuery.error ??
    usageQuery.error;
  const displayError = errorMessage(mutationError ?? queryError);

  const isMutating =
    checkInMutation.isPending ||
    confirmMutation.isPending ||
    createLeaveMutation.isPending ||
    approveMutation.isPending ||
    rejectMutation.isPending;

  return (
    <AttendanceLeaveView
      attendance={attendanceQuery.data ?? []}
      leaveRequests={leaveQuery.data ?? []}
      students={studentsQuery.data?.items ?? []}
      teachers={teachersQuery.data?.items ?? []}
      scheduleSlots={scheduleQuery.data?.items ?? []}
      checkInTeacherId={checkInTeacherId}
      checkInDate={checkInDate}
      leaveUsage={usageQuery.data ?? null}
      usageStudentId={usageStudentId}
      isLoading={
        studentsQuery.isLoading ||
        attendanceQuery.isLoading ||
        leaveQuery.isLoading
      }
      isLoadingSlots={
        Boolean(checkInTeacherId) &&
        (teachersQuery.isLoading || scheduleQuery.isLoading)
      }
      error={displayError}
      isMutating={isMutating}
      onUsageStudentChange={setUsageStudentId}
      onCheckInTeacherChange={setCheckInTeacherId}
      onCheckInDateChange={setCheckInDate}
      onCheckIn={(scheduleId) => {
        checkInMutation.mutate({ schedule_id: scheduleId });
      }}
      onConfirm={(attendanceId, outcome) => {
        confirmMutation.mutate({ attendanceId, outcome });
      }}
      onCreateLeave={({ studentId, leaveDate, kind, reason }) => {
        createLeaveMutation.mutate({
          student_id: studentId,
          leave_date: leaveDate,
          kind,
          reason: reason.length > 0 ? reason : undefined,
        });
      }}
      onApproveLeave={(leaveId) => {
        approveMutation.mutate(leaveId);
      }}
      onRejectLeave={(leaveId) => {
        rejectMutation.mutate(leaveId);
      }}
    />
  );
}
