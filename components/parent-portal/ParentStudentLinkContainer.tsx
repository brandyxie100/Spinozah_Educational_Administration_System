'use client';

/**
 * Container: wires users/students lists and parent↔student link mutation.
 */

import { useMemo, useState } from 'react';
import { ParentStudentLinkView } from '@/components/parent-portal/ParentStudentLinkView';
import { useCreateParentStudentLink } from '@/hooks/useParentPortal';
import { useStudentsList } from '@/hooks/useStudents';
import { useUsersList } from '@/hooks/useUsers';
import { ApiError } from '@/lib/api';
import type { ParentStudentLink } from '@/lib/api/parent';

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    if (error.status === 400) {
      return 'Selected user is not a parent. Create or update a user with the parent role first.';
    }
    if (error.status === 404) {
      return 'Parent user or student was not found in this tenant.';
    }
    if (error.status === 403) {
      return 'You need admin or frontdesk access to link parents (listing parents requires admin).';
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Something went wrong creating the parent↔student link';
}

/** Staff module to link parent users to students. */
export function ParentStudentLinkContainer() {
  const [createdLinks, setCreatedLinks] = useState<ParentStudentLink[]>([]);
  const usersQuery = useUsersList({ page: 1, pageSize: 100 });
  const studentsQuery = useStudentsList({ page: 1, pageSize: 100 });
  const createMutation = useCreateParentStudentLink();

  const parents = useMemo(
    () =>
      (usersQuery.data?.items ?? []).filter(
        (user) => user.role === 'parent' && user.is_active,
      ),
    [usersQuery.data?.items],
  );

  const displayError = errorMessage(
    createMutation.error ?? usersQuery.error ?? studentsQuery.error,
  );

  return (
    <ParentStudentLinkView
      parents={parents}
      students={studentsQuery.data?.items ?? []}
      createdLinks={createdLinks}
      isLoadingOptions={usersQuery.isLoading || studentsQuery.isLoading}
      isSaving={createMutation.isPending}
      error={displayError}
      onCreate={({ parentUserId, studentId }) => {
        createMutation.mutate(
          {
            parent_user_id: parentUserId,
            student_id: studentId,
          },
          {
            onSuccess: (link) => {
              setCreatedLinks((prev) => [link, ...prev]);
            },
          },
        );
      }}
    />
  );
}
