/**
 * Unit tests for admin KPI API client.
 */

import { getAdminKpis } from '@/lib/api/admin';
import * as client from '@/lib/api/client';

jest.mock('@/lib/api/client', () => {
  const actual = jest.requireActual('@/lib/api/client') as typeof client;
  return {
    ...actual,
    apiRequest: jest.fn(),
    getApiBaseUrl: () => 'http://localhost:8000',
  };
});

describe('getAdminKpis', () => {
  it('should request /api/v1/admin/kpis', async () => {
    const mocked = client.apiRequest as jest.MockedFunction<typeof client.apiRequest>;
    mocked.mockResolvedValueOnce({
      student_count: 1,
      teacher_count: 1,
      today_schedule_count: 0,
      unpaid_invoice_count: 0,
      unpaid_invoice_total: '0.00',
      revenue_final_amount_sum: '0.00',
      revenue_by_period: [],
      today_schedules: [],
    });
    const result = await getAdminKpis();
    expect(mocked).toHaveBeenCalledWith('http://localhost:8000/api/v1/admin/kpis');
    expect(result.student_count).toBe(1);
  });
});
