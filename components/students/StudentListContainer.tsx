'use client';

/**
 * Container: wires TanStack Query student hooks into StudentListView.
 */

import { StudentListView } from '@/components/students/StudentListView';
import {
  useCreateStudent,
  useStudentsList,
  useUpdateStudent,
} from '@/hooks/useStudents';
import { ApiError } from '@/lib/api';

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
  return 'Something went wrong loading students';
}

/** Student Management module container (data + mutations). */
export function StudentListContainer() {
  const listQuery = useStudentsList({ page: 1, pageSize: 50 });
  const createMutation = useCreateStudent();
  const updateMutation = useUpdateStudent();

  const mutationError = createMutation.error ?? updateMutation.error;
  const queryError = listQuery.error;
  const displayError = errorMessage(mutationError ?? queryError);

  return (
    <StudentListView
      students={listQuery.data?.items ?? []}
      total={listQuery.data?.total ?? 0}
      isLoading={listQuery.isLoading}
      error={displayError}
      isSaving={createMutation.isPending || updateMutation.isPending}
      onCreate={({ full_name, email }) => {
        createMutation.mutate({
          full_name,
          email: email.length > 0 ? email : null,
        });
      }}
      onUpdate={({ studentId, full_name, email, is_active }) => {
        updateMutation.mutate({
          studentId,
          input: {
            full_name,
            email: email.length > 0 ? email : null,
            is_active,
          },
        });
      }}
    />
  );
}
