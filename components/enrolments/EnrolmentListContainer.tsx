'use client';

/**
 * Container: wires students + enrolment hooks into the enrolment view.
 */

import { useState } from 'react';
import { EnrolmentListView } from '@/components/enrolments/EnrolmentListView';
import {
  useCreateEnrolment,
  useEnrolmentsList,
  useUpdateEnrolment,
} from '@/hooks/useEnrolments';
import { useStudentsList } from '@/hooks/useStudents';
import { ApiError } from '@/lib/api';

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return 'Student or enrolment was not found in this tenant.';
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Something went wrong loading enrolments';
}

/** Enrolment management module container. */
export function EnrolmentListContainer() {
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const studentsQuery = useStudentsList({ page: 1, pageSize: 100 });
  const enrolmentsQuery = useEnrolmentsList({
    studentId: selectedStudentId || null,
  });
  const createMutation = useCreateEnrolment();
  const updateMutation = useUpdateEnrolment();

  const displayError = errorMessage(
    createMutation.error ??
      updateMutation.error ??
      studentsQuery.error ??
      enrolmentsQuery.error,
  );

  return (
    <EnrolmentListView
      students={studentsQuery.data?.items ?? []}
      enrolments={enrolmentsQuery.data ?? []}
      selectedStudentId={selectedStudentId}
      isLoading={studentsQuery.isLoading || enrolmentsQuery.isLoading}
      error={displayError}
      isSaving={createMutation.isPending || updateMutation.isPending}
      onSelectStudent={setSelectedStudentId}
      onCreate={({ studentId, totalLessons }) => {
        createMutation.mutate({
          student_id: studentId,
          total_lessons: totalLessons,
        });
      }}
      onUpdateRemaining={({ enrolmentId, remainingLessons }) => {
        updateMutation.mutate({
          enrolmentId,
          input: { remaining_lessons: remainingLessons },
        });
      }}
    />
  );
}
