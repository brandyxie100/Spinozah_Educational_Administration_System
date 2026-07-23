'use client';

/**
 * TanStack Query hooks for admin user CRUD (AIJOB-62).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createUser,
  deactivateUser,
  listUsers,
  updateUser,
  type UserCreateInput,
  type UserUpdateInput,
} from '@/lib/api/users';

export const usersQueryKey = ['users'] as const;

/** Load paginated users from FastAPI. */
export function useUsersList(options?: { page?: number; pageSize?: number }) {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 20;

  return useQuery({
    queryKey: [...usersQueryKey, page, pageSize],
    queryFn: () => listUsers({ page, pageSize }),
  });
}

/** Create a user and invalidate the list. */
export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: UserCreateInput) => createUser(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: usersQueryKey });
    },
  });
}

/** Update a user and invalidate the list. */
export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      userId,
      input,
    }: {
      userId: string;
      input: UserUpdateInput;
    }) => updateUser(userId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: usersQueryKey });
    },
  });
}

/** Deactivate a user and invalidate the list. */
export function useDeactivateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => deactivateUser(userId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: usersQueryKey });
    },
  });
}
