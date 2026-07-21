'use client';

/**
 * Presentational admin KPI dashboard: counts, unpaid alerts, revenue chart,
 * and today's schedule overview.
 */

import type { AdminKpis } from '@/lib/api/admin';

export type AdminDashboardViewProps = {
  data: AdminKpis | undefined;
  isLoading: boolean;
  error: string | null;
};

function maxAmount(periods: AdminKpis['revenue_by_period']): number {
  let max = 0;
  for (const row of periods) {
    const value = Number(row.amount);
    if (!Number.isNaN(value) && value > max) {
      max = value;
    }
  }
  return max > 0 ? max : 1;
}

/** Pure UI for the Admin KPI dashboard module. */
export function AdminDashboardView({
  data,
  isLoading,
  error,
}: AdminDashboardViewProps) {
  if (isLoading) {
    return <p className="text-slate-600">Loading admin KPIs…</p>;
  }
  if (error) {
    return (
      <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
        {error}
      </p>
    );
  }
  if (!data) {
    return <p className="text-slate-600">No KPI data available.</p>;
  }

  const chartMax = maxAmount(data.revenue_by_period);

  return (
    <div className="space-y-8">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Students</p>
          <p className="mt-2 text-3xl font-bold">{data.student_count}</p>
        </div>
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Teachers</p>
          <p className="mt-2 text-3xl font-bold">{data.teacher_count}</p>
        </div>
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Today&apos;s lessons</p>
          <p className="mt-2 text-3xl font-bold">{data.today_schedule_count}</p>
        </div>
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Paid revenue</p>
          <p className="mt-2 text-3xl font-bold">{data.revenue_final_amount_sum}</p>
        </div>
      </div>

      {data.unpaid_invoice_count > 0 ? (
        <div
          role="alert"
          className="rounded-xl border border-amber-300 bg-amber-50 px-5 py-4 text-amber-900"
        >
          <p className="font-semibold">Unpaid invoice alert</p>
          <p className="mt-1 text-sm">
            {data.unpaid_invoice_count} unpaid invoice
            {data.unpaid_invoice_count === 1 ? '' : 's'} totaling{' '}
            {data.unpaid_invoice_total}.
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-emerald-900">
          No unpaid invoices.
        </div>
      )}

      <section className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold">Revenue by period</h2>
        <p className="mt-1 text-sm text-slate-500">Paid invoice totals by semester</p>
        {data.revenue_by_period.length === 0 ? (
          <p className="mt-4 text-slate-500">No paid revenue yet.</p>
        ) : (
          <div className="mt-6 flex h-48 items-end gap-4">
            {data.revenue_by_period.map((row) => {
              const heightPct = Math.max(8, (Number(row.amount) / chartMax) * 100);
              return (
                <div key={row.period} className="flex flex-1 flex-col items-center gap-2">
                  <div
                    className="w-full max-w-[4rem] rounded-t-md bg-slate-800"
                    style={{ height: `${heightPct}%` }}
                    title={`${row.period}: ${row.amount}`}
                  />
                  <span className="text-xs font-medium text-slate-600">{row.period}</span>
                  <span className="text-xs text-slate-500">{row.amount}</span>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <section className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold">Today&apos;s schedule</h2>
        {data.today_schedules.length === 0 ? (
          <p className="mt-3 text-slate-500">No lessons scheduled for today.</p>
        ) : (
          <ul className="mt-4 divide-y divide-slate-100">
            {data.today_schedules.map((slot) => (
              <li key={`${slot.schedule_id}-${slot.starts_at}`} className="py-3 text-sm">
                <p className="font-medium text-slate-900">
                  {new Date(slot.starts_at).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}{' '}
                  –{' '}
                  {new Date(slot.ends_at).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                  {slot.classroom ? ` · ${slot.classroom}` : ''}
                </p>
                <p className="text-slate-500">
                  Teacher {slot.teacher_id.slice(0, 8)}… · Student{' '}
                  {slot.student_id.slice(0, 8)}…
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
