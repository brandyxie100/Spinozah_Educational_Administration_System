/**
 * TanStack Query hook for admin KPI dashboard.
 */

import { useQuery } from '@tanstack/react-query';

import { getAdminKpis } from '@/lib/api/admin';

export const adminKpiQueryKey = ['admin', 'kpis'] as const;

/** Load admin operational KPIs for the current tenant. */
export function useAdminKpis() {
  return useQuery({
    queryKey: adminKpiQueryKey,
    queryFn: () => getAdminKpis(),
  });
}
