/**
 * Typed FastAPI client for admin KPI dashboard (AIJOB-50).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';

export type RevenuePeriod = {
  period: string;
  amount: string;
};

export type TodaySchedule = {
  schedule_id: string;
  teacher_id: string;
  student_id: string;
  starts_at: string;
  ends_at: string;
  classroom: string | null;
};

export type AdminKpis = {
  student_count: number;
  teacher_count: number;
  today_schedule_count: number;
  unpaid_invoice_count: number;
  unpaid_invoice_total: string;
  revenue_final_amount_sum: string;
  revenue_by_period: RevenuePeriod[];
  today_schedules: TodaySchedule[];
};

/** Fetch tenant-scoped admin KPIs (ADMIN role required). */
export async function getAdminKpis(): Promise<AdminKpis> {
  return apiRequest<AdminKpis>(`${getApiBaseUrl()}/api/v1/admin/kpis`);
}
