/**
 * Typed FastAPI client helpers for student CRUD (AIJOB-41).
 *
 * Paths are absolute (`NEXT_PUBLIC_API_URL` + `/api/v1/students`) so they are
 * not treated as same-origin Next.js BFF routes under `/api/`.
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type Student = {
  id: string;
  tenant_id: string;
  full_name: string;
  email: string | null;
  is_active: boolean;
};

export type StudentListResponse = {
  items: Student[];
  page: number;
  page_size: number;
  total: number;
};

export type StudentCreateInput = {
  full_name: string;
  email?: string | null;
};

export type StudentUpdateInput = {
  full_name: string;
  email?: string | null;
  is_active: boolean;
};

function studentsCollectionUrl(query?: { page: number; pageSize: number }): string {
  const base = `${getApiBaseUrl()}/api/v1/students`;
  if (!query) {
    return base;
  }
  const params = new URLSearchParams({
    page: String(query.page),
    page_size: String(query.pageSize),
  });
  return `${base}?${params.toString()}`;
}

function studentItemUrl(studentId: string): string {
  return `${getApiBaseUrl()}/api/v1/students/${studentId}`;
}

/** Fetch a paginated student list for the caller's tenant. */
export async function listStudents(options?: {
  page?: number;
  pageSize?: number;
}): Promise<StudentListResponse> {
  const page = options?.page ?? 1;
  const pageSize = options?.pageSize ?? 20;
  return apiRequest<StudentListResponse>(studentsCollectionUrl({ page, pageSize }));
}

/** Create a student in the caller's tenant. */
export async function createStudent(input: StudentCreateInput): Promise<Student> {
  return apiRequest<Student>(studentsCollectionUrl(), {
    method: 'POST',
    body: JSON.stringify({
      full_name: input.full_name,
      email: input.email ?? null,
    }),
  });
}

/** Replace student fields (PUT). */
export async function updateStudent(
  studentId: string,
  input: StudentUpdateInput,
): Promise<Student> {
  return apiRequest<Student>(studentItemUrl(studentId), {
    method: 'PUT',
    body: JSON.stringify({
      full_name: input.full_name,
      email: input.email ?? null,
      is_active: input.is_active,
    }),
  });
}
