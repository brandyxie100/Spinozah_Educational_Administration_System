'use client';

/**
 * Container: wires TanStack Query user hooks into UserListView.
 */

import { UserListView } from '@/components/users/UserListView';
import {
  useCreateUser,
  useDeactivateUser,
  useUpdateUser,
  useUsersList,
} from '@/hooks/useUsers';
import { ApiError } from '@/lib/api';
import type { UserRole } from '@/lib/api/users';

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
  return 'Something went wrong loading users';
}

/** User Management module container (data + mutations). */
export function UserListContainer() {
  const listQuery = useUsersList({ page: 1, pageSize: 50 });
  const createMutation = useCreateUser();
  const updateMutation = useUpdateUser();
  const deactivateMutation = useDeactivateUser();

  const mutationError =
    createMutation.error ??
    updateMutation.error ??
    deactivateMutation.error;
  const displayError = errorMessage(mutationError ?? listQuery.error);

  return (
    <UserListView
      users={listQuery.data?.items ?? []}
      total={listQuery.data?.total ?? 0}
      isLoading={listQuery.isLoading}
      error={displayError}
      isSaving={
        createMutation.isPending ||
        updateMutation.isPending ||
        deactivateMutation.isPending
      }
      onCreate={(input) => {
        createMutation.mutate(input);
      }}
      onUpdate={({ userId, full_name, role, password }) => {
        const input: {
          full_name: string;
          role: UserRole;
          password?: string;
        } = { full_name, role };
        if (password.trim().length >= 8) {
          input.password = password.trim();
        }
        updateMutation.mutate({ userId, input });
      }}
      onDeactivate={(userId) => {
        deactivateMutation.mutate(userId);
      }}
    />
  );
}
