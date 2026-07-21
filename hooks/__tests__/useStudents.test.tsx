/**
 * Hook tests for TanStack Query student hooks.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { useCreateStudent, useStudentsList } from '@/hooks/useStudents';
import * as studentsApi from '@/lib/api/students';

jest.mock('@/lib/api/students', () => ({
  listStudents: jest.fn(),
  createStudent: jest.fn(),
  updateStudent: jest.fn(),
}));

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  }

  return Wrapper;
}

describe('useStudents hooks', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should load students via listStudents', async () => {
    (studentsApi.listStudents as jest.Mock).mockResolvedValue({
      items: [
        {
          id: 's1',
          tenant_id: 't1',
          full_name: 'Charlotte',
          email: null,
          is_active: true,
        },
      ],
      page: 1,
      page_size: 20,
      total: 1,
    });

    const { result } = renderHook(() => useStudentsList(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.total).toBe(1);
    expect(studentsApi.listStudents).toHaveBeenCalled();
  });

  it('should create a student via createStudent', async () => {
    (studentsApi.createStudent as jest.Mock).mockResolvedValue({
      id: 's2',
      tenant_id: 't1',
      full_name: 'Zoe',
      email: 'zoe@example.com',
      is_active: true,
    });
    (studentsApi.listStudents as jest.Mock).mockResolvedValue({
      items: [],
      page: 1,
      page_size: 20,
      total: 0,
    });

    const { result } = renderHook(() => useCreateStudent(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ full_name: 'Zoe', email: 'zoe@example.com' });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(studentsApi.createStudent).toHaveBeenCalledWith({
      full_name: 'Zoe',
      email: 'zoe@example.com',
    });
  });
});
