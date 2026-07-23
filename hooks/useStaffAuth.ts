'use client';

/**
 * Staff auth hooks: login / logout with session persistence (AIJOB-61).
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { loginStaff, logoutStaff, type StaffLoginInput } from '@/lib/api/auth';
import {
  setStaffAccessToken,
  wireStaffAccessTokenProvider,
} from '@/lib/staff-session';

/** Login and store the staff access JWT. */
export function useStaffLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: StaffLoginInput) => loginStaff(input),
    onSuccess: async (data) => {
      setStaffAccessToken(data.access_token, data.user);
      wireStaffAccessTokenProvider();
      await queryClient.invalidateQueries();
    },
  });
}

/** Logout: clear staff session (best-effort API cookie clear). */
export function useStaffLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      try {
        await logoutStaff();
      } catch {
        // Access token is client-owned; proceed even if cookie clear fails.
      }
      setStaffAccessToken(null);
      wireStaffAccessTokenProvider();
    },
    onSuccess: async () => {
      await queryClient.clear();
    },
  });
}
