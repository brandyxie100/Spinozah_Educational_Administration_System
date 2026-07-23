/**
 * Tests for teacher API helpers.
 */

import {
  createTeacher,
  getTeacherSchedule,
  listTeachers,
} from '@/lib/api/teachers';

describe('teachers API helpers', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('lists teachers from FastAPI', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ items: [], page: 1, page_size: 50, total: 0 }),
    }) as unknown as typeof fetch;

    await listTeachers({ page: 1, pageSize: 50 });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/teachers?page=1&page_size=50',
      expect.any(Object),
    );
  });

  it('creates a teacher via POST', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 't1',
        tenant_id: 'ten1',
        full_name: 'Ada',
        email: 'ada@example.com',
        user_id: null,
        is_active: true,
      }),
    }) as unknown as typeof fetch;

    await createTeacher({ full_name: 'Ada', email: 'ada@example.com' });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/teachers',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('fetches teacher schedule with date range', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        teacher_id: 't1',
        range_start: '2026-10-14',
        range_end: '2026-10-14',
        items: [],
      }),
    }) as unknown as typeof fetch;

    await getTeacherSchedule({
      teacherId: 't1',
      rangeStart: '2026-10-14',
      rangeEnd: '2026-10-14',
    });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/teachers/t1/schedule?range_start=2026-10-14&range_end=2026-10-14',
      expect.any(Object),
    );
  });
});
