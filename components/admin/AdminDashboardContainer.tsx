'use client';

/**
 * Container: wires useAdminKpis into AdminDashboardView.
 */

import { AdminDashboardView } from '@/components/admin/AdminDashboardView';
import { useAdminKpis } from '@/hooks/useAdminKpis';
import { ApiError } from '@/lib/api';

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Something went wrong loading admin KPIs';
}

/** Admin KPI dashboard module container. */
export function AdminDashboardContainer() {
  const query = useAdminKpis();
  return (
    <AdminDashboardView
      data={query.data}
      isLoading={query.isLoading}
      error={errorMessage(query.error)}
    />
  );
}
