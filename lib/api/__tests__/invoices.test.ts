/**
 * @jest-environment node
 */
import { listInvoices } from '../invoices';

describe('invoices api client', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('test_listInvoices_buildsQueryAndReturnsJson', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => [
        {
          id: 'inv-1',
          tenant_id: 't1',
          student_id: 'stu-1',
          enrolment_id: null,
          semester_label: '2026-S2',
          subtotal: '1200.00',
          credit: '0.00',
          final_amount: '1200.00',
          status: 'unpaid',
          line_items: [],
        },
      ],
    }) as unknown as typeof fetch;

    const rows = await listInvoices({ studentId: 'stu-1' });
    expect(rows).toHaveLength(1);
    expect(global.fetch).toHaveBeenCalled();
    const calledUrl = String((global.fetch as jest.Mock).mock.calls[0]?.[0]);
    expect(calledUrl).toContain('/api/v1/invoices');
    expect(calledUrl).toContain('student_id=stu-1');
  });
});
