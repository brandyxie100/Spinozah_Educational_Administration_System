'use client';

/**
 * Container: staff login form wired to auth hooks.
 */

import { StaffLoginView } from '@/components/auth/StaffLoginView';
import { useStaffLogin } from '@/hooks/useStaffAuth';
import { ApiError } from '@/lib/api';

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Sign-in failed';
}

export type StaffLoginContainerProps = {
  onSignedIn?: () => void;
};

/** Staff login module container. */
export function StaffLoginContainer({ onSignedIn }: StaffLoginContainerProps) {
  const loginMutation = useStaffLogin();

  return (
    <StaffLoginView
      isMutating={loginMutation.isPending}
      error={errorMessage(loginMutation.error)}
      onLogin={(input) => {
        loginMutation.mutate(input, {
          onSuccess: () => {
            onSignedIn?.();
          },
        });
      }}
    />
  );
}
