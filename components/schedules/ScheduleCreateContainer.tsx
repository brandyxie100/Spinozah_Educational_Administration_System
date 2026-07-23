'use client';

/**
 * Container: wires teachers/students lists and schedule create mutation.
 */

import { useState } from 'react';
import { ScheduleCreateView } from '@/components/schedules/ScheduleCreateView';
import { useCreateSchedule } from '@/hooks/useSchedules';
import { useStudentsList } from '@/hooks/useStudents';
import { useTeachersList } from '@/hooks/useTeacherSchedule';
import { ApiError } from '@/lib/api';
import type { Schedule } from '@/lib/api/schedules';

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'Schedule conflict: teacher, student, or classroom overlaps an existing lesson.';
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Something went wrong creating the schedule';
}

/** Schedule create module container. */
export function ScheduleCreateContainer() {
  const [createdSchedules, setCreatedSchedules] = useState<Schedule[]>([]);
  const teachersQuery = useTeachersList({ page: 1, pageSize: 100 });
  const studentsQuery = useStudentsList({ page: 1, pageSize: 100 });
  const createMutation = useCreateSchedule();

  const displayError = errorMessage(
    createMutation.error ?? teachersQuery.error ?? studentsQuery.error,
  );

  return (
    <ScheduleCreateView
      teachers={teachersQuery.data?.items ?? []}
      students={studentsQuery.data?.items ?? []}
      createdSchedules={createdSchedules}
      isLoadingOptions={teachersQuery.isLoading || studentsQuery.isLoading}
      isSaving={createMutation.isPending}
      error={displayError}
      onCreate={({
        teacherId,
        studentId,
        startsAt,
        endsAt,
        classroom,
        isRecurring,
        recurrenceUntil,
      }) => {
        createMutation.mutate(
          {
            teacher_id: teacherId,
            student_id: studentId,
            starts_at: startsAt,
            ends_at: endsAt,
            classroom: classroom.length > 0 ? classroom : null,
            is_recurring: isRecurring,
            recurrence_until:
              isRecurring && recurrenceUntil.length > 0
                ? recurrenceUntil
                : null,
          },
          {
            onSuccess: (schedule) => {
              setCreatedSchedules((prev) => [schedule, ...prev]);
            },
          },
        );
      }}
    />
  );
}
