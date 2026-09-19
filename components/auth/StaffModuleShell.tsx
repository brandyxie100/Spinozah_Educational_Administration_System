'use client';

/**
 * Shell for FastAPI-backed staff modules: auth bar + login gate.
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

/** Prefer staff JWT and require sign-in before rendering children. */
export function StaffModuleShell({
  title,
  onBack,
  children,
}: StaffModuleShellProps) {
  const initial = readStaffSession();
  const [token, setToken] = useState<string | null>(initial.token);
  const [user, setUser] = useState<StaffUser | null>(initial.user);
  const [showLogin, setShowLogin] = useState(!initial.token);
  const logoutMutation = useStaffLogout();

  function refreshSession() {
    wireStaffAccessTokenProvider();
    setToken(getStaffAccessToken());
    setUser(getStaffUser());
    setShowLogin(!getStaffAccessToken());
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8 text-slate-900">
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
              setShowLogin(true);
            },
          });
        }}
      />
      <h1 className="mb-6 text-3xl font-bold text-slate-900">{title}</h1>
      {!token || showLogin ? (
        <StaffLoginContainer
          onSignedIn={() => {
            refreshSession();
          }}
        />
      ) : (
        children
      )}
    </div>
  );
}
