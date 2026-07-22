/**
 * Session helpers for parent portal access JWT (browser-only).
 */

import { setAccessTokenProvider } from '@/lib/api/client';

export const PARENT_ACCESS_TOKEN_KEY = 'spinozah_parent_access_token';

/** Read the stored parent access token (null on server / missing). */
export function getParentAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.sessionStorage.getItem(PARENT_ACCESS_TOKEN_KEY);
}

/** Persist parent access token and wire the shared API client. */
export function setParentAccessToken(token: string | null): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (token) {
    window.sessionStorage.setItem(PARENT_ACCESS_TOKEN_KEY, token);
  } else {
    window.sessionStorage.removeItem(PARENT_ACCESS_TOKEN_KEY);
  }
  setAccessTokenProvider(() => getParentAccessToken());
}

/** Ensure the API client reads the parent session token. */
export function wireParentAccessTokenProvider(): void {
  setAccessTokenProvider(() => getParentAccessToken());
}
