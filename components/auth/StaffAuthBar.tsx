'use client';

/**
 * Compact staff session status + sign-out for Soft River chrome.
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
      <div className="mb-0 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onSignInClick}
          className="rounded-full bg-sp-orange px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-sp-orange/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sp-orange"
        >
          Staff sign in
        </button>
      </div>
    );
  }

  return (
    <div className="mb-0 flex flex-wrap items-center justify-end gap-3 text-sm">
      <span className="text-sp-muted">
        Signed in as <strong className="text-sp-ink">{user.full_name}</strong> (
        {user.role})
      </span>
      <button
        type="button"
        disabled={isMutating}
        onClick={onSignOut}
        className="rounded-full border border-sp-hairline px-3 py-1.5 text-sp-ink transition-colors hover:border-sp-orange hover:bg-sp-orange-soft disabled:opacity-50"
      >
        Sign out
      </button>
    </div>
  );
}
