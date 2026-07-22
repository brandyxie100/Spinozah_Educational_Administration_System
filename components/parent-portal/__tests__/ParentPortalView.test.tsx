/**
 * Presenter tests for ParentPortalView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { ParentPortalView } from '@/components/parent-portal/ParentPortalView';
import type {
  LinkedStudent,
  ParentDashboardReport,
  ParentInvoice,
} from '@/lib/api/parent';

const students: LinkedStudent[] = [
  {
    id: 'stu-1',
    full_name: 'Charlotte',
    email: null,
    is_active: true,
  },
];

const report: ParentDashboardReport = {
  student_id: 'stu-1',
  remaining_lessons: 2,
  total_lessons: 10,
  completed_lessons: 8,
  attendance_count: 8,
  invoice_count: 1,
  unpaid_invoice_count: 1,
};

const invoices: ParentInvoice[] = [
  {
    id: 'inv-1',
    student_id: 'stu-1',
    semester_label: '2026-S2',
    subtotal: '1200.00',
    credit: '0.00',
    final_amount: '1200.00',
    status: 'unpaid',
  },
];

describe('ParentPortalView', () => {
  it('renders magic-link request form when signed out', () => {
    const onRequest = jest.fn();
    render(
      <ParentPortalView
        isAuthenticated={false}
        parentName={null}
        students={[]}
        selectedStudentId=""
        enrolment={null}
        attendance={[]}
        invoices={[]}
        report={null}
        isLoading={false}
        isMutating={false}
        error={null}
        magicLinkHint={null}
        onRequestMagicLink={onRequest}
        onConsumeToken={jest.fn()}
        onSelectStudent={jest.fn()}
        onDownloadPdf={jest.fn()}
        onLogout={jest.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText(/Parent email/), {
      target: { value: 'parent@example.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send magic link' }));
    expect(onRequest).toHaveBeenCalledWith({
      tenantSlug: 'demo',
      email: 'parent@example.com',
    });
  });

  it('renders dashboard report and PDF action when signed in', () => {
    const onDownloadPdf = jest.fn();
    render(
      <ParentPortalView
        isAuthenticated
        parentName="Parent One"
        students={students}
        selectedStudentId="stu-1"
        enrolment={{
          id: 'enr-1',
          student_id: 'stu-1',
          status: 'active',
          total_lessons: 10,
          completed_lessons: 8,
          remaining_lessons: 2,
          extension_days: 0,
        }}
        attendance={[]}
        invoices={invoices}
        report={report}
        isLoading={false}
        isMutating={false}
        error={null}
        magicLinkHint={null}
        onRequestMagicLink={jest.fn()}
        onConsumeToken={jest.fn()}
        onSelectStudent={jest.fn()}
        onDownloadPdf={onDownloadPdf}
        onLogout={jest.fn()}
      />,
    );

    expect(screen.getByText(/Remaining lessons:/)).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Download PDF' }));
    expect(onDownloadPdf).toHaveBeenCalledWith('inv-1');
  });
});
