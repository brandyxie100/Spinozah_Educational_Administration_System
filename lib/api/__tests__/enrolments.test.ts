/**
 * Tests for enrolment API helpers.
 */

import {
  createEnrolment,
  listEnrolments,
  updateEnrolment,
} from '@/lib/api/enrolments';

describe('enrolments API helpers', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('lists enrolments with optional student filter', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => [],
    }) as unknown as typeof fetch;

    await listEnrolments({ studentId: 'stu-1' });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/enrolments?student_id=stu-1',
      expect.any(Object),
    );
  });

  it('creates and updates enrolments', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 'enr-1',
        tenant_id: 't1',
        student_id: 'stu-1',
        total_lessons: 10,
        completed_lessons: 0,
        remaining_lessons: 10,
        extension_days: 0,
        status: 'active',
      }),
    }) as unknown as typeof fetch;

    await createEnrolment({ student_id: 'stu-1', total_lessons: 10 });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/enrolments',
      expect.objectContaining({ method: 'POST' }),
    );

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 'enr-1',
        tenant_id: 't1',
        student_id: 'stu-1',
        total_lessons: 8,
        completed_lessons: 0,
        remaining_lessons: 8,
        extension_days: 0,
        status: 'active',
      }),
    }) as unknown as typeof fetch;

    await updateEnrolment('enr-1', { remaining_lessons: 8 });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/enrolments/enr-1',
      expect.objectContaining({ method: 'PATCH' }),
    );
  });
});
