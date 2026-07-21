/**
 * Tests for student FastAPI client helpers.
 */

import { createStudent, listStudents, updateStudent } from '@/lib/api/students';

describe('students API helpers', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('lists students against FastAPI /api/v1/students', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        items: [],
        page: 1,
        page_size: 20,
        total: 0,
      }),
    }) as unknown as typeof fetch;

    await listStudents({ page: 1, pageSize: 20 });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/students?page=1&page_size=20',
      expect.any(Object),
    );
  });

  it('creates a student with POST JSON body', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 's1',
        tenant_id: 't1',
        full_name: 'Alex',
        email: 'alex@example.com',
        is_active: true,
      }),
    }) as unknown as typeof fetch;

    await createStudent({ full_name: 'Alex', email: 'alex@example.com' });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/students',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          full_name: 'Alex',
          email: 'alex@example.com',
        }),
      }),
    );
  });

  it('updates a student with PUT JSON body', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 's1',
        tenant_id: 't1',
        full_name: 'Alex Updated',
        email: null,
        is_active: false,
      }),
    }) as unknown as typeof fetch;

    await updateStudent('s1', {
      full_name: 'Alex Updated',
      email: null,
      is_active: false,
    });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/students/s1',
      expect.objectContaining({
        method: 'PUT',
      }),
    );
  });
});
