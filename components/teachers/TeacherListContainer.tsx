'use client';

/**
 * Container: wires teacher list/create/update hooks into TeacherListView.
 */

import { TeacherListView } from '@/components/teachers/TeacherListView';
import {
  useCreateTeacher,
  useTeachersList,
  useUpdateTeacher,
} from '@/hooks/useTeacherSchedule';
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
  return 'Something went wrong loading teachers';
}

/** Teacher Management module container (data + mutations). */
export function TeacherListContainer() {
  const listQuery = useTeachersList({ page: 1, pageSize: 50 });
  const createMutation = useCreateTeacher();
  const updateMutation = useUpdateTeacher();

  const displayError = errorMessage(
    createMutation.error ?? updateMutation.error ?? listQuery.error,
  );

  return (
    <TeacherListView
      teachers={listQuery.data?.items ?? []}
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
      onUpdate={({ teacherId, full_name, email, is_active }) => {
        updateMutation.mutate({
          teacherId,
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
