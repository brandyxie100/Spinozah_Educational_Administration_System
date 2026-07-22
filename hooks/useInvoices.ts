'use client';

/**
 * TanStack Query hooks for invoice list/create/status/PDF (AIJOB-57).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createInvoice,
  downloadInvoicePdf,
  listInvoices,
  updateInvoicePaymentStatus,
  type InvoiceCreateInput,
  type PaymentStatus,
} from '@/lib/api/invoices';

export const invoicesQueryKey = ['invoices'] as const;

/** Load invoices (optional student filter). */
export function useInvoicesList(options?: { studentId?: string }) {
  return useQuery({
    queryKey: [...invoicesQueryKey, options?.studentId ?? 'all'],
    queryFn: () => listInvoices({ studentId: options?.studentId }),
  });
}

/** Create an invoice and invalidate the list. */
export function useCreateInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: InvoiceCreateInput) => createInvoice(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: invoicesQueryKey });
    },
  });
}

/** Update payment status and invalidate the list. */
export function useUpdateInvoicePaymentStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      invoiceId,
      status,
    }: {
      invoiceId: string;
      status: PaymentStatus;
    }) => updateInvoicePaymentStatus(invoiceId, status),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: invoicesQueryKey });
    },
  });
}

/** Download PDF and trigger a browser save. */
export function useDownloadInvoicePdf() {
  return useMutation({
    mutationFn: async (invoiceId: string) => {
      const blob = await downloadInvoicePdf(invoiceId);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `invoice-${invoiceId}.pdf`;
      anchor.click();
      URL.revokeObjectURL(url);
    },
  });
}
