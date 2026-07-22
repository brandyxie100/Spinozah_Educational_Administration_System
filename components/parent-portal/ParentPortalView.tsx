'use client';

/**
 * Presentational Parent Portal (login + linked-student dashboard).
 */

import { useState, type FormEvent } from 'react';
import type {
  LinkedStudent,
  ParentAttendance,
  ParentDashboardReport,
  ParentEnrolment,
  ParentInvoice,
} from '@/lib/api/parent';

export type ParentPortalViewProps = {
  isAuthenticated: boolean;
  parentName: string | null;
  students: LinkedStudent[];
  selectedStudentId: string;
  enrolment: ParentEnrolment | null;
  attendance: ParentAttendance[];
  invoices: ParentInvoice[];
  report: ParentDashboardReport | null;
  isLoading: boolean;
  isMutating: boolean;
  error: string | null;
  magicLinkHint: string | null;
  onRequestMagicLink: (input: { tenantSlug: string; email: string }) => void;
  onConsumeToken: (token: string) => void;
  onSelectStudent: (studentId: string) => void;
  onDownloadPdf: (invoiceId: string) => void;
  onLogout: () => void;
};

/** Pure UI for magic-link auth and parent student dashboard. */
export function ParentPortalView({
  isAuthenticated,
  parentName,
  students,
  selectedStudentId,
  enrolment,
  attendance,
  invoices,
  report,
  isLoading,
  isMutating,
  error,
  magicLinkHint,
  onRequestMagicLink,
  onConsumeToken,
  onSelectStudent,
  onDownloadPdf,
  onLogout,
}: ParentPortalViewProps) {
  const [tenantSlug, setTenantSlug] = useState('demo');
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');

  function handleRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!tenantSlug.trim() || !email.trim()) {
      return;
    }
    onRequestMagicLink({
      tenantSlug: tenantSlug.trim(),
      email: email.trim(),
    });
  }

  function handleConsume(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token.trim()) {
      return;
    }
    onConsumeToken(token.trim());
  }

  if (!isAuthenticated) {
    return (
      <div className="space-y-8">
        {error && (
          <p
            className="rounded-lg bg-red-50 p-3 text-sm text-red-700"
            role="alert"
          >
            {error}
          </p>
        )}
        {magicLinkHint && (
          <p className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">
            {magicLinkHint}
          </p>
        )}

        <section className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-bold">Request magic link</h2>
          <form onSubmit={handleRequest} className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm font-medium text-slate-700">
              Tenant slug
              <input
                type="text"
                value={tenantSlug}
                onChange={(event) => setTenantSlug(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Parent email
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
              />
            </label>
            <button
              type="submit"
              disabled={isMutating}
              className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2"
            >
              Send magic link
            </button>
          </form>
        </section>

        <section className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-bold">Enter magic-link token</h2>
          <p className="mb-3 text-sm text-slate-600">
            Paste the token from the email link (or open{' '}
            <code className="rounded bg-slate-100 px-1">/parent/magic-link</code>
            ).
          </p>
          <form onSubmit={handleConsume} className="flex flex-col gap-3">
            <input
              type="text"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="Magic-link token"
              className="block w-full rounded-lg border p-2 font-mono text-sm"
              required
            />
            <button
              type="submit"
              disabled={isMutating}
              className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50"
            >
              Sign in
            </button>
          </form>
        </section>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-slate-600">
          Signed in as <strong>{parentName ?? 'Parent'}</strong>
        </p>
        <button
          type="button"
          onClick={onLogout}
          className="rounded-lg border px-3 py-1.5 text-sm"
        >
          Sign out
        </button>
      </div>

      {error && (
        <p
          className="rounded-lg bg-red-50 p-3 text-sm text-red-700"
          role="alert"
        >
          {error}
        </p>
      )}

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Linked students</h2>
        {isLoading && students.length === 0 ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : students.length === 0 ? (
          <p className="text-sm text-slate-500">No linked students yet.</p>
        ) : (
          <label className="block text-sm font-medium text-slate-700">
            Student
            <select
              value={selectedStudentId}
              onChange={(event) => onSelectStudent(event.target.value)}
              className="mt-1 block w-full max-w-md rounded-lg border p-2"
            >
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.full_name}
                </option>
              ))}
            </select>
          </label>
        )}
      </section>

      {selectedStudentId && (
        <>
          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-bold">Dashboard report</h2>
            {isLoading && !report ? (
              <p className="text-sm text-slate-500">Loading…</p>
            ) : report ? (
              <ul className="grid gap-2 text-sm sm:grid-cols-2">
                <li>
                  Remaining lessons:{' '}
                  <strong>{report.remaining_lessons ?? '—'}</strong>
                </li>
                <li>
                  Completed:{' '}
                  <strong>{report.completed_lessons ?? '—'}</strong> /{' '}
                  {report.total_lessons ?? '—'}
                </li>
                <li>
                  Attendance records:{' '}
                  <strong>{report.attendance_count}</strong>
                </li>
                <li>
                  Invoices: <strong>{report.invoice_count}</strong> (
                  {report.unpaid_invoice_count} unpaid)
                </li>
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No report available.</p>
            )}
          </section>

          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-bold">Enrolment</h2>
            {enrolment ? (
              <p className="text-sm">
                Status <strong>{enrolment.status}</strong> ·{' '}
                {enrolment.remaining_lessons} remaining of{' '}
                {enrolment.total_lessons} ({enrolment.completed_lessons}{' '}
                completed)
                {enrolment.extension_days > 0
                  ? ` · +${enrolment.extension_days} extension days`
                  : ''}
              </p>
            ) : (
              <p className="text-sm text-slate-500">No active enrolment.</p>
            )}
          </section>

          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-bold">Attendance</h2>
            {attendance.length === 0 ? (
              <p className="text-sm text-slate-500">No attendance records.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {attendance.map((row) => (
                  <li key={row.id} className="rounded-lg border p-3">
                    <span className="font-medium">{row.status}</span>
                    <span className="ml-2 font-mono text-xs text-slate-500">
                      {row.id}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-bold">Invoices</h2>
            {invoices.length === 0 ? (
              <p className="text-sm text-slate-500">No invoices.</p>
            ) : (
              <ul className="space-y-3">
                {invoices.map((invoice) => (
                  <li
                    key={invoice.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-4 text-sm"
                  >
                    <div>
                      <p>
                        <strong>{invoice.semester_label}</strong> ·{' '}
                        {invoice.status}
                      </p>
                      <p className="text-slate-600">
                        Final: {invoice.final_amount}
                      </p>
                    </div>
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => onDownloadPdf(invoice.id)}
                      className="rounded-lg bg-slate-900 px-3 py-1.5 text-white disabled:opacity-50"
                    >
                      Download PDF
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
