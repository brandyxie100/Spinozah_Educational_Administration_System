/**
 * Parent portal session helpers (separate storage from staff JWT).
 */

import {
  getParentAccessToken,
  PARENT_ACCESS_TOKEN_KEY,
  setAccessTokenPreference,
  setParentAccessToken,
  wireSharedAccessTokenProvider,
} from '@/lib/access-token';

export {
  getParentAccessToken,
  PARENT_ACCESS_TOKEN_KEY,
  setParentAccessToken,
  wireSharedAccessTokenProvider,
};

/** Prefer parent token while the parent portal module is active. */
export function wireParentAccessTokenProvider(): void {
  setAccessTokenPreference('parent');
  wireSharedAccessTokenProvider();
}
