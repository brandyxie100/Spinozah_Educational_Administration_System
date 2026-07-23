/**
 * Tests for schedule API helpers.
 */

import { createSchedule } from '@/lib/api/schedules';

describe('schedules API helpers', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('creates a schedule via POST', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 'sch1',
        tenant_id: 'ten1',
        teacher_id: 't1',
        student_id: 's1',
        classroom: 'A1',
        starts_at: '2026-07-21T10:00:00Z',
        ends_at: '2026-07-21T11:00:00Z',
        status: 'scheduled',
        is_recurring: false,
        recurrence_weekday: null,
        recurrence_until: null,
      }),
    }) as unknown as typeof fetch;

    await createSchedule({
      teacher_id: 't1',
      student_id: 's1',
      starts_at: '2026-07-21T10:00:00.000Z',
      ends_at: '2026-07-21T11:00:00.000Z',
      classroom: 'A1',
    });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/schedules',
      expect.objectContaining({ method: 'POST' }),
    );
    const init = (global.fetch as jest.Mock).mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(init.body))).toEqual({
      teacher_id: 't1',
      student_id: 's1',
      starts_at: '2026-07-21T10:00:00.000Z',
      ends_at: '2026-07-21T11:00:00.000Z',
      classroom: 'A1',
      is_recurring: false,
      recurrence_until: null,
    });
  });
});
