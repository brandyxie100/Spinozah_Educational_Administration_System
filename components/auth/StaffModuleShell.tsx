'use client';

/**
 * Soft River shell for FastAPI-backed staff modules: auth bar + optional login gate.
 */

import { useState, type ReactNode } from 'react';
import { StaffAuthBar } from '@/components/auth/StaffAuthBar';
import { StaffLoginContainer } from '@/components/auth/StaffLoginContainer';
import { BackButton } from '@/components/dashboard/BackButton';
import { useStaffLogout } from '@/hooks/useStaffAuth';
import {
  getStaffAccessToken,
  getStaffUser,
  wireStaffAccessTokenProvider,
  type StaffUser,
} from '@/lib/staff-session';

export type StaffModuleShellProps = {
  title: string;
  onBack: () => void;
  children: ReactNode;
  /** When false, skip staff JWT gate (AI / parent portal modules). Default true. */
  requireAuth?: boolean;
};

function readStaffSession(): {
  token: string | null;
  user: StaffUser | null;
} {
  wireStaffAccessTokenProvider();
  return {
    token: getStaffAccessToken(),
    user: getStaffUser(),
  };
}

/** Prefer staff JWT and require sign-in before rendering children (unless requireAuth=false). */
export function StaffModuleShell({
  title,
  onBack,
  children,
  requireAuth = true,
}: StaffModuleShellProps) {
  const initial = readStaffSession();
  const [token, setToken] = useState<string | null>(initial.token);
  const [user, setUser] = useState<StaffUser | null>(initial.user);
  const [showLogin, setShowLogin] = useState(requireAuth && !initial.token);
  const logoutMutation = useStaffLogout();

  function refreshSession() {
    wireStaffAccessTokenProvider();
    setToken(getStaffAccessToken());
    setUser(getStaffUser());
    setShowLogin(requireAuth && !getStaffAccessToken());
  }

  const gated = requireAuth && (!token || showLogin);

  return (
    <div className="min-h-screen bg-sp-canvas p-6 text-sp-ink sm:p-8">
      <div className="mx-auto max-w-5xl">
        <BackButton onBack={onBack} />
        <StaffAuthBar
          user={user}
          isMutating={logoutMutation.isPending}
          onSignInClick={() => setShowLogin(true)}
          onSignOut={() => {
            logoutMutation.mutate(undefined, {
              onSettled: () => {
                setToken(null);
                setUser(null);
                if (requireAuth) {
                  setShowLogin(true);
                }
              },
            });
          }}
        />
        <h1 className="mb-6 font-[family-name:var(--font-fraunces)] text-3xl font-semibold text-sp-ink">
          {title}
        </h1>
        {gated ? (
          <StaffLoginContainer
            onSignedIn={() => {
              refreshSession();
            }}
          />
        ) : (
          <div className="rounded-2xl border border-sp-hairline bg-sp-surface p-4 shadow-sm sm:p-6">
            {children}
          </div>
        )}
      </div>
    </div>
  );
}
