/**
 * @jest-environment jsdom
 */
import {
  getActiveAccessToken,
  setAccessTokenPreference,
  setParentAccessToken,
  setStaffAccessToken,
  STAFF_ACCESS_TOKEN_KEY,
  PARENT_ACCESS_TOKEN_KEY,
} from '@/lib/access-token';
import { resetAccessTokenProviderForTests } from '@/lib/api/client';

describe('access-token session separation', () => {
  beforeEach(() => {
    window.sessionStorage.clear();
    resetAccessTokenProviderForTests();
    setAccessTokenPreference('staff');
  });

  it('test_staffAndParentTokens_useSeparateKeys', () => {
    setStaffAccessToken('staff-token', {
      id: 'u1',
      tenant_id: 't1',
      email: 'a@example.com',
      full_name: 'Admin',
      role: 'admin',
    });
    setParentAccessToken('parent-token');

    expect(window.sessionStorage.getItem(STAFF_ACCESS_TOKEN_KEY)).toBe(
      'staff-token',
    );
    expect(window.sessionStorage.getItem(PARENT_ACCESS_TOKEN_KEY)).toBe(
      'parent-token',
    );
  });

  it('test_preference_selectsParentWithoutClearingStaff', () => {
    setStaffAccessToken('staff-token');
    setParentAccessToken('parent-token');
    setAccessTokenPreference('parent');
    expect(getActiveAccessToken()).toBe('parent-token');
    setAccessTokenPreference('staff');
    expect(getActiveAccessToken()).toBe('staff-token');
  });
});
