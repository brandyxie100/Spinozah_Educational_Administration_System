'use client';

/**
 * TanStack Query hooks for parent portal magic-link and dashboard (AIJOB-58).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  consumeMagicLink,
  createParentStudentLink,
  downloadStudentInvoicePdf,
  getStudentDashboardReport,
  getStudentEnrolment,
  listLinkedStudents,
  listStudentAttendance,
  listStudentInvoices,
  requestMagicLink,
  type ParentStudentLinkCreateInput,
} from '@/lib/api/parent';
import { setParentAccessToken } from '@/lib/parent-session';

export const parentStudentsQueryKey = ['parent', 'students'] as const;
export const parentStudentLinksQueryKey = ['parent', 'student-links'] as const;

/** Request a magic-link email. */
export function useRequestMagicLink() {
  return useMutation({
    mutationFn: (input: { tenantSlug: string; email: string }) =>
      requestMagicLink(input),
  });
}

/** Consume magic-link token and store the resulting access JWT. */
export function useConsumeMagicLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (token: string) => consumeMagicLink(token),
    onSuccess: async (data) => {
      setParentAccessToken(data.access_token);
      await queryClient.invalidateQueries({ queryKey: ['parent'] });
    },
  });
}

/** Linked students for the authenticated parent. */
export function useLinkedStudents(enabled: boolean) {
  return useQuery({
    queryKey: parentStudentsQueryKey,
    queryFn: listLinkedStudents,
    enabled,
  });
}

/** Enrolment for the selected linked student. */
export function useParentEnrolment(
  studentId: string | null,
  enabled: boolean,
) {
  return useQuery({
    queryKey: ['parent', 'enrolment', studentId],
    queryFn: () => getStudentEnrolment(studentId!),
    enabled: enabled && Boolean(studentId),
  });
}

/** Attendance history for the selected linked student. */
export function useParentAttendance(
  studentId: string | null,
  enabled: boolean,
) {
  return useQuery({
    queryKey: ['parent', 'attendance', studentId],
    queryFn: () => listStudentAttendance(studentId!),
    enabled: enabled && Boolean(studentId),
  });
}

/** Invoices for the selected linked student. */
export function useParentInvoices(studentId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ['parent', 'invoices', studentId],
    queryFn: () => listStudentInvoices(studentId!),
    enabled: enabled && Boolean(studentId),
  });
}

/** Aggregate report for the selected linked student. */
export function useParentReport(studentId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ['parent', 'report', studentId],
    queryFn: () => getStudentDashboardReport(studentId!),
    enabled: enabled && Boolean(studentId),
  });
}

/** Download invoice PDF and trigger a browser save. */
export function useDownloadParentInvoicePdf() {
  return useMutation({
    mutationFn: async ({
      studentId,
      invoiceId,
    }: {
      studentId: string;
      invoiceId: string;
    }) => {
      const blob = await downloadStudentInvoicePdf(studentId, invoiceId);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `invoice-${invoiceId}.pdf`;
      anchor.click();
      URL.revokeObjectURL(url);
    },
  });
}

/** Staff: create a parent↔student link (admin/frontdesk). */
export function useCreateParentStudentLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ParentStudentLinkCreateInput) =>
      createParentStudentLink(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: parentStudentLinksQueryKey,
      });
      await queryClient.invalidateQueries({ queryKey: parentStudentsQueryKey });
    },
  });
}
