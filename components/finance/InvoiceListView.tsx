'use client';

/**
 * Presentational Finance & Invoice dashboard (no data fetching).
 */

import { useState, type FormEvent } from 'react';
import type { Invoice, PaymentStatus } from '@/lib/api/invoices';
import type { Student } from '@/lib/api/students';

export type InvoiceListViewProps = {
  invoices: Invoice[];
  students: Student[];
  isLoading: boolean;
  error: string | null;
  isMutating: boolean;
  onCreate: (input: {
    studentId: string;
    semesterLabel: string;
    subtotal: string;
    credit: string;
  }) => void;
  onStatusChange: (invoiceId: string, status: PaymentStatus) => void;
  onDownloadPdf: (invoiceId: string) => void;
};

const STATUS_OPTIONS: PaymentStatus[] = ['unpaid', 'partial', 'paid', 'void'];

/** Pure UI for listing invoices, creating, status update, and PDF download. */
export function InvoiceListView({
  invoices,
  students,
  isLoading,
  error,
  isMutating,
  onCreate,
  onStatusChange,
  onDownloadPdf,
}: InvoiceListViewProps) {
  const [studentId, setStudentId] = useState('');
  const [semesterLabel, setSemesterLabel] = useState('2026-S2');
  const [subtotal, setSubtotal] = useState('1200.00');
  const [credit, setCredit] = useState('0.00');

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!studentId || !semesterLabel.trim() || !subtotal.trim()) {
      return;
    }
    onCreate({
      studentId,
      semesterLabel: semesterLabel.trim(),
      subtotal: subtotal.trim(),
      credit: credit.trim() || '0.00',
    });
  }

  const studentName = (id: string) =>
    students.find((student) => student.id === id)?.full_name ?? id.slice(0, 8);

  return (
    <div className="space-y-8">
      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
          {error}
        </p>
      )}

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Create semester invoice</h2>
        <form onSubmit={handleCreate} className="grid gap-3 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Student
            <select
              value={studentId}
              onChange={(event) => setStudentId(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              required
            >
              <option value="">Select…</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.full_name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Semester label
            <input
              type="text"
              value={semesterLabel}
              onChange={(event) => setSemesterLabel(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              required
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Subtotal
            <input
              type="text"
              value={subtotal}
              onChange={(event) => setSubtotal(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2 font-mono"
              required
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Credit
            <input
              type="text"
              value={credit}
              onChange={(event) => setCredit(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2 font-mono"
            />
          </label>
          <button
            type="submit"
            disabled={isMutating || !studentId}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2"
          >
            Generate invoice
          </button>
        </form>
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Invoices</h2>
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : invoices.length === 0 ? (
          <p className="text-sm text-slate-500">No invoices yet.</p>
        ) : (
          <ul className="space-y-3">
            {invoices.map((invoice) => (
              <li
                key={invoice.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-4"
              >
                <div className="text-sm">
                  <p>
                    <strong>{studentName(invoice.student_id)}</strong> ·{' '}
                    {invoice.semester_label}
                  </p>
                  <p className="text-slate-600">
                    Final: {invoice.final_amount} (subtotal {invoice.subtotal} −
                    credit {invoice.credit})
                  </p>
                  <p className="font-mono text-xs text-slate-500">{invoice.id}</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <label className="text-sm">
                    Status
                    <select
                      value={invoice.status}
                      disabled={isMutating}
                      onChange={(event) =>
                        onStatusChange(
                          invoice.id,
                          event.target.value as PaymentStatus,
                        )
                      }
                      className="ml-2 rounded-lg border p-1.5"
                    >
                      {STATUS_OPTIONS.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button
                    type="button"
                    disabled={isMutating}
                    onClick={() => onDownloadPdf(invoice.id)}
                    className="rounded-lg bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                  >
                    Download PDF
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
