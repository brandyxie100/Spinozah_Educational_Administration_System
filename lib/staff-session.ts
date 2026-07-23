/**
 * Staff session helpers (separate storage from parent magic-link JWT).
 */

import {
  getStaffAccessToken,
  getStaffUser,
  setAccessTokenPreference,
  setStaffAccessToken,
  STAFF_ACCESS_TOKEN_KEY,
  wireSharedAccessTokenProvider,
  type StaffUser,
} from '@/lib/access-token';

export {
  getStaffAccessToken,
  getStaffUser,
  setStaffAccessToken,
  STAFF_ACCESS_TOKEN_KEY,
  wireSharedAccessTokenProvider,
  type StaffUser,
};

/** Prefer staff token for dashboard / ops modules. */
export function wireStaffAccessTokenProvider(): void {
  setAccessTokenPreference('staff');
  wireSharedAccessTokenProvider();
}
