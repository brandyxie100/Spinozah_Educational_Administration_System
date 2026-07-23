'use client';

/**
 * Compact staff session status + sign-out for the dashboard chrome.
 */

import type { StaffUser } from '@/lib/staff-session';

export type StaffAuthBarProps = {
  user: StaffUser | null;
  isMutating: boolean;
  onSignOut: () => void;
  onSignInClick: () => void;
};

/** Shows signed-in staff identity or a sign-in affordance. */
export function StaffAuthBar({
  user,
  isMutating,
  onSignOut,
  onSignInClick,
}: StaffAuthBarProps) {
  if (!user) {
    return (
      <div className="mb-4 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onSignInClick}
          className="rounded-lg border px-3 py-1.5 text-sm"
        >
          Staff sign in
        </button>
      </div>
    );
  }

  return (
    <div className="mb-4 flex flex-wrap items-center justify-end gap-3 text-sm">
      <span className="text-slate-600">
        Signed in as <strong>{user.full_name}</strong> ({user.role})
      </span>
      <button
        type="button"
        disabled={isMutating}
        onClick={onSignOut}
        className="rounded-lg border px-3 py-1.5 disabled:opacity-50"
      >
        Sign out
      </button>
    </div>
  );
}
