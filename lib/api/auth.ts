/**
 * Typed FastAPI client helpers for staff auth (AIJOB-61).
 */

import { apiRequest, getApiBaseUrl } from '@/lib/api/client';
import type { StaffUser } from '@/lib/access-token';

export type StaffTokenResponse = {
  access_token: string;
  token_type: string;
  user: StaffUser;
};

export type StaffLoginInput = {
  tenantSlug: string;
  email: string;
  password: string;
};

function authBaseUrl(): string {
  return `${getApiBaseUrl()}/api/v1/auth`;
}

/** Authenticate staff and return access JWT + user. */
export async function loginStaff(
  input: StaffLoginInput,
): Promise<StaffTokenResponse> {
  return apiRequest<StaffTokenResponse>(`${authBaseUrl()}/login`, {
    method: 'POST',
    body: JSON.stringify({
      tenant_slug: input.tenantSlug,
      email: input.email,
      password: input.password,
    }),
  });
}

/** Clear refresh cookie on the API (access token is cleared client-side). */
export async function logoutStaff(): Promise<void> {
  await apiRequest<null>(`${authBaseUrl()}/logout`, {
    method: 'POST',
  });
}
