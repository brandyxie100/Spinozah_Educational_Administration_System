/**
 * Shared access-token resolution for staff and parent sessions.
 *
 * Tokens live in separate sessionStorage keys. A preference flag chooses which
 * token the API client sends so parent portal and staff modules do not clash.
 */

import { setAccessTokenProvider } from '@/lib/api/client';

export const STAFF_ACCESS_TOKEN_KEY = 'spinozah_staff_access_token';
export const STAFF_USER_KEY = 'spinozah_staff_user';
export const PARENT_ACCESS_TOKEN_KEY = 'spinozah_parent_access_token';

export type AccessTokenPreference = 'staff' | 'parent';

export type StaffUser = {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: string;
};

let preference: AccessTokenPreference = 'staff';

/** Read staff access JWT (null on server / missing). */
export function getStaffAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.sessionStorage.getItem(STAFF_ACCESS_TOKEN_KEY);
}

/** Read stored staff user profile for UI. */
export function getStaffUser(): StaffUser | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const raw = window.sessionStorage.getItem(STAFF_USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as StaffUser;
  } catch {
    return null;
  }
}

/** Read parent access JWT (null on server / missing). */
export function getParentAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.sessionStorage.getItem(PARENT_ACCESS_TOKEN_KEY);
}

/**
 * Active Bearer token for the current preference.
 * Falls back to the other session if the preferred token is absent.
 */
export function getActiveAccessToken(): string | null {
  const staff = getStaffAccessToken();
  const parent = getParentAccessToken();
  if (preference === 'parent') {
    return parent ?? staff;
  }
  return staff ?? parent;
}

/** Register the shared provider with the HTTP client. */
export function wireSharedAccessTokenProvider(): void {
  setAccessTokenProvider(() => getActiveAccessToken());
}

/** Prefer parent or staff token for subsequent API calls. */
export function setAccessTokenPreference(next: AccessTokenPreference): void {
  preference = next;
  wireSharedAccessTokenProvider();
}

/** Persist or clear the staff access JWT and profile. */
export function setStaffAccessToken(
  token: string | null,
  user?: StaffUser | null,
): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (token) {
    window.sessionStorage.setItem(STAFF_ACCESS_TOKEN_KEY, token);
    if (user) {
      window.sessionStorage.setItem(STAFF_USER_KEY, JSON.stringify(user));
    }
  } else {
    window.sessionStorage.removeItem(STAFF_ACCESS_TOKEN_KEY);
    window.sessionStorage.removeItem(STAFF_USER_KEY);
  }
  preference = 'staff';
  wireSharedAccessTokenProvider();
}

/** Persist or clear the parent access JWT. */
export function setParentAccessToken(token: string | null): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (token) {
    window.sessionStorage.setItem(PARENT_ACCESS_TOKEN_KEY, token);
  } else {
    window.sessionStorage.removeItem(PARENT_ACCESS_TOKEN_KEY);
  }
  wireSharedAccessTokenProvider();
}
