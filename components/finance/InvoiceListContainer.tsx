'use client';

/**
 * Container: wires invoice hooks and students list into InvoiceListView.
 */

import { InvoiceListView } from '@/components/finance/InvoiceListView';
import {
  useCreateInvoice,
  useDownloadInvoicePdf,
  useInvoicesList,
  useUpdateInvoicePaymentStatus,
} from '@/hooks/useInvoices';
import { useStudentsList } from '@/hooks/useStudents';
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
  return 'Something went wrong loading invoices';
}

/** Finance & Invoice module container (data + mutations). */
export function InvoiceListContainer() {
  const studentsQuery = useStudentsList({ page: 1, pageSize: 100 });
  const invoicesQuery = useInvoicesList();
  const createMutation = useCreateInvoice();
  const statusMutation = useUpdateInvoicePaymentStatus();
  const pdfMutation = useDownloadInvoicePdf();

  const mutationError =
    createMutation.error ?? statusMutation.error ?? pdfMutation.error;
  const queryError = studentsQuery.error ?? invoicesQuery.error;
  const displayError = errorMessage(mutationError ?? queryError);

  const isMutating =
    createMutation.isPending ||
    statusMutation.isPending ||
    pdfMutation.isPending;

  return (
    <InvoiceListView
      invoices={invoicesQuery.data ?? []}
      students={studentsQuery.data?.items ?? []}
      isLoading={studentsQuery.isLoading || invoicesQuery.isLoading}
      error={displayError}
      isMutating={isMutating}
      onCreate={({ studentId, semesterLabel, subtotal, credit }) => {
        createMutation.mutate({
          student_id: studentId,
          semester_label: semesterLabel,
          subtotal,
          credit,
        });
      }}
      onStatusChange={(invoiceId, status) => {
        statusMutation.mutate({ invoiceId, status });
      }}
      onDownloadPdf={(invoiceId) => {
        pdfMutation.mutate(invoiceId);
      }}
    />
  );
}
