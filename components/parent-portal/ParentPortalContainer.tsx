'use client';

/**
 * Container: wires parent magic-link auth and dashboard reads into the view.
 */

import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ParentPortalView } from '@/components/parent-portal/ParentPortalView';
import {
  useConsumeMagicLink,
  useDownloadParentInvoicePdf,
  useLinkedStudents,
  useParentAttendance,
  useParentEnrolment,
  useParentInvoices,
  useParentReport,
  useRequestMagicLink,
} from '@/hooks/useParentPortal';
import { ApiError } from '@/lib/api';
import type { ParentUser } from '@/lib/api/parent';
import {
  getParentAccessToken,
  setParentAccessToken,
  wireParentAccessTokenProvider,
} from '@/lib/parent-session';

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
  return 'Something went wrong in the parent portal';
}

function readInitialAccessToken(): string | null {
  wireParentAccessTokenProvider();
  return getParentAccessToken();
}

/** Parent Portal module container (auth session + dashboard data). */
export function ParentPortalContainer() {
  const queryClient = useQueryClient();
  const [accessToken, setAccessToken] = useState<string | null>(
    readInitialAccessToken,
  );
  const [parentUser, setParentUser] = useState<ParentUser | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [magicLinkHint, setMagicLinkHint] = useState<string | null>(null);

  const isAuthenticated = Boolean(accessToken);

  const studentsQuery = useLinkedStudents(isAuthenticated);
  const effectiveStudentId =
    selectedStudentId || studentsQuery.data?.[0]?.id || '';

  const enrolmentQuery = useParentEnrolment(
    effectiveStudentId || null,
    isAuthenticated,
  );
  const attendanceQuery = useParentAttendance(
    effectiveStudentId || null,
    isAuthenticated,
  );
  const invoicesQuery = useParentInvoices(
    effectiveStudentId || null,
    isAuthenticated,
  );
  const reportQuery = useParentReport(
    effectiveStudentId || null,
    isAuthenticated,
  );

  const requestMutation = useRequestMagicLink();
  const consumeMutation = useConsumeMagicLink();
  const pdfMutation = useDownloadParentInvoicePdf();

  const mutationError =
    requestMutation.error ?? consumeMutation.error ?? pdfMutation.error;
  const enrolmentError =
    enrolmentQuery.error instanceof ApiError &&
    enrolmentQuery.error.status === 404
      ? null
      : enrolmentQuery.error;
  const queryError =
    studentsQuery.error ??
    enrolmentError ??
    attendanceQuery.error ??
    invoicesQuery.error ??
    reportQuery.error;
  const displayError = errorMessage(mutationError ?? queryError);

  const isMutating =
    requestMutation.isPending ||
    consumeMutation.isPending ||
    pdfMutation.isPending;

  const isLoading =
    studentsQuery.isLoading ||
    enrolmentQuery.isLoading ||
    attendanceQuery.isLoading ||
    invoicesQuery.isLoading ||
    reportQuery.isLoading;

  return (
    <ParentPortalView
      isAuthenticated={isAuthenticated}
      parentName={parentUser?.full_name ?? null}
      students={studentsQuery.data ?? []}
      selectedStudentId={effectiveStudentId}
      enrolment={enrolmentQuery.data ?? null}
      attendance={attendanceQuery.data ?? []}
      invoices={invoicesQuery.data ?? []}
      report={reportQuery.data ?? null}
      isLoading={isLoading}
      isMutating={isMutating}
      error={displayError}
      magicLinkHint={magicLinkHint}
      onRequestMagicLink={({ tenantSlug, email }) => {
        setMagicLinkHint(null);
        requestMutation.mutate(
          { tenantSlug, email },
          {
            onSuccess: (result) => {
              if (result.magic_url) {
                setMagicLinkHint(
                  `Debug magic link available: ${result.magic_url}`,
                );
              } else {
                setMagicLinkHint(
                  result.detail ||
                    'If a parent account exists, a magic link has been sent.',
                );
              }
            },
          },
        );
      }}
      onConsumeToken={(token) => {
        consumeMutation.mutate(token, {
          onSuccess: (data) => {
            setAccessToken(data.access_token);
            setParentUser(data.user);
            setMagicLinkHint(null);
          },
        });
      }}
      onSelectStudent={setSelectedStudentId}
      onDownloadPdf={(invoiceId) => {
        if (!effectiveStudentId) {
          return;
        }
        pdfMutation.mutate({ studentId: effectiveStudentId, invoiceId });
      }}
      onLogout={() => {
        setParentAccessToken(null);
        setAccessToken(null);
        setParentUser(null);
        setSelectedStudentId('');
        setMagicLinkHint(null);
        void queryClient.removeQueries({ queryKey: ['parent'] });
      }}
    />
  );
}
