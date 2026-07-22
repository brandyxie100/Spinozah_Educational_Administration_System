/**
 * Presenter tests for InvoiceListView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { InvoiceListView } from '@/components/finance/InvoiceListView';
import type { Invoice } from '@/lib/api/invoices';
import type { Student } from '@/lib/api/students';

const students: Student[] = [
  {
    id: 'stu-1',
    tenant_id: 't1',
    full_name: 'Ada Lovelace',
    email: null,
    is_active: true,
  },
];

const invoices: Invoice[] = [
  {
    id: 'inv-1',
    tenant_id: 't1',
    student_id: 'stu-1',
    enrolment_id: null,
    semester_label: '2026-S2',
    subtotal: '1200.00',
    credit: '100.00',
    final_amount: '1100.00',
    status: 'unpaid',
    line_items: [],
  },
];

describe('InvoiceListView', () => {
  it('renders invoices and fires status / PDF actions', () => {
    const onStatusChange = jest.fn();
    const onDownloadPdf = jest.fn();

    render(
      <InvoiceListView
        invoices={invoices}
        students={students}
        isLoading={false}
        error={null}
        isMutating={false}
        onCreate={jest.fn()}
        onStatusChange={onStatusChange}
        onDownloadPdf={onDownloadPdf}
      />,
    );

    expect(screen.getAllByText(/Ada Lovelace/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Final: 1100.00/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Download PDF' }));
    expect(onDownloadPdf).toHaveBeenCalledWith('inv-1');

    fireEvent.change(screen.getByDisplayValue('unpaid'), {
      target: { value: 'paid' },
    });
    expect(onStatusChange).toHaveBeenCalledWith('inv-1', 'paid');
  });
});
