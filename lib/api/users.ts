/**
 * Typed FastAPI client helpers for admin user management (AIJOB-62).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type UserRole = 'admin' | 'frontdesk' | 'teacher' | 'parent';

export type User = {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: UserRole | string;
  is_active: boolean;
};

export type UserListResponse = {
  items: User[];
  page: number;
  page_size: number;
  total: number;
};

export type UserCreateInput = {
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
};

export type UserUpdateInput = {
  full_name?: string;
  role?: UserRole;
  password?: string;
};

function usersCollectionUrl(query?: { page: number; pageSize: number }): string {
  const base = `${getApiBaseUrl()}/api/v1/users`;
  if (!query) {
    return base;
  }
  const params = new URLSearchParams({
    page: String(query.page),
    page_size: String(query.pageSize),
  });
  return `${base}?${params.toString()}`;
}

function userItemUrl(userId: string): string {
  return `${getApiBaseUrl()}/api/v1/users/${userId}`;
}

/** Fetch a paginated user list (admin only). */
export async function listUsers(options?: {
  page?: number;
  pageSize?: number;
}): Promise<UserListResponse> {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 20;
  return apiRequest<UserListResponse>(usersCollectionUrl({ page, pageSize }));
}

/** Create a tenant user. */
export async function createUser(input: UserCreateInput): Promise<User> {
  return apiRequest<User>(usersCollectionUrl(), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

/** Partially update a tenant user. */
export async function updateUser(
  userId: string,
  input: UserUpdateInput,
): Promise<User> {
  return apiRequest<User>(userItemUrl(userId), {
    method: 'PATCH',
    body: JSON.stringify(input),
  });
}

/** Soft-deactivate a tenant user. */
export async function deactivateUser(userId: string): Promise<User> {
  return apiRequest<User>(`${userItemUrl(userId)}/deactivate`, {
    method: 'POST',
  });
}
