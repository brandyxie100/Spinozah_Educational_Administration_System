/**
 * Presenter tests for AdminDashboardView.
 */

import { render, screen } from '@testing-library/react';

import { AdminDashboardView } from '@/components/admin/AdminDashboardView';
import type { AdminKpis } from '@/lib/api/admin';

const sample: AdminKpis = {
  student_count: 12,
  teacher_count: 3,
  today_schedule_count: 1,
  unpaid_invoice_count: 2,
  unpaid_invoice_total: '300.00',
  revenue_final_amount_sum: '900.00',
  revenue_by_period: [{ period: '2026-S1', amount: '900.00' }],
  today_schedules: [
    {
      schedule_id: '11111111-1111-1111-1111-111111111111',
      teacher_id: '22222222-2222-2222-2222-222222222222',
      student_id: '33333333-3333-3333-3333-333333333333',
      starts_at: '2026-07-22T09:00:00.000Z',
      ends_at: '2026-07-22T10:00:00.000Z',
      classroom: 'A1',
    },
  ],
};

describe('AdminDashboardView', () => {
  it('should render KPI counts, unpaid alert, and revenue chart', () => {
    render(<AdminDashboardView data={sample} isLoading={false} error={null} />);
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText(/Unpaid invoice alert/i)).toBeInTheDocument();
    expect(screen.getByText('2026-S1')).toBeInTheDocument();
    expect(screen.getByText(/A1/)).toBeInTheDocument();
  });

  it('should show error state', () => {
    render(
      <AdminDashboardView data={undefined} isLoading={false} error="Not authenticated" />,
    );
    expect(screen.getByText('Not authenticated')).toBeInTheDocument();
  });
});
