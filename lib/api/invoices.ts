/**
 * Typed FastAPI client helpers for semester invoices (AIJOB-57).
 */

import { apiRequest, apiRequestBlob, getApiBaseUrl } from '@/lib/api/client';

export type PaymentStatus = 'unpaid' | 'partial' | 'paid' | 'void';

export type InvoiceLineItem = {
  description: string;
  amount: string;
};

export type Invoice = {
  id: string;
  tenant_id: string;
  student_id: string;
  enrolment_id: string | null;
  semester_label: string;
  subtotal: string;
  credit: string;
  final_amount: string;
  status: PaymentStatus | string;
  line_items: InvoiceLineItem[];
};

export type InvoiceCreateInput = {
  student_id: string;
  semester_label: string;
  subtotal: string;
  credit?: string;
  enrolment_id?: string | null;
  line_items?: { description: string; amount: string }[];
};

function invoicesBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/invoices`;
}

/** List invoices (optional student filter). */
export async function listInvoices(options?: {
  studentId?: string;
}): Promise<Invoice[]> {
  const params = new URLSearchParams();
  if (options?.studentId) {
    params.set('student_id', options.studentId);
  }
  const query = params.toString();
  const url = query ? `${invoicesBaseUrl()}?${query}` : invoicesBaseUrl();
  return apiRequest<Invoice[]>(url);
}

/** Create a semester invoice. */
export async function createInvoice(
  input: InvoiceCreateInput,
): Promise<Invoice> {
  return apiRequest<Invoice>(invoicesBaseUrl(), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

/** Update payment status. */
export async function updateInvoicePaymentStatus(
  invoiceId: string,
  status: PaymentStatus,
): Promise<Invoice> {
  return apiRequest<Invoice>(
    `${invoicesBaseUrl()}/${invoiceId}/payment-status`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    },
  );
}

/** Download invoice PDF as a Blob. */
export async function downloadInvoicePdf(invoiceId: string): Promise<Blob> {
  return apiRequestBlob(`${getApiBaseUrl()}/api/v1/invoices/${invoiceId}/pdf`);
}
