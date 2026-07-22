/**
 * @jest-environment node
 */
import { listAttendance } from '../attendance';

describe('attendance api client', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('test_listAttendance_buildsQueryAndReturnsJson', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => [
        {
          id: 'att-1',
          tenant_id: 't1',
          schedule_id: 'sch-1',
          student_id: 'stu-1',
          enrolment_id: 'enr-1',
          status: 'pending_confirmation',
          remaining_lessons: 8,
        },
      ],
    }) as unknown as typeof fetch;

    const rows = await listAttendance({ status: 'pending_confirmation' });
    expect(rows).toHaveLength(1);
    expect(global.fetch).toHaveBeenCalled();
    const calledUrl = String((global.fetch as jest.Mock).mock.calls[0]?.[0]);
    expect(calledUrl).toContain('/api/v1/attendance');
    expect(calledUrl).toContain('status=pending_confirmation');
  });
});
