'use client';

/**
 * Magic-link landing: consume ?token= then deep-link to Parent Portal.
 */

import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ApiError } from '@/lib/api';
import { consumeMagicLink } from '@/lib/api/parent';
import { setParentAccessToken } from '@/lib/parent-session';

function MagicLinkConsumer() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'pending' | 'ok' | 'error'>(
    token ? 'pending' : 'error',
  );
  const [message, setMessage] = useState(
    token
      ? 'Signing you in…'
      : 'Missing magic-link token in the URL.',
  );

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;
    void (async () => {
      try {
        const tokens = await consumeMagicLink(token);
        if (cancelled) {
          return;
        }
        setParentAccessToken(tokens.access_token);
        setStatus('ok');
        setMessage(`Signed in as ${tokens.user.full_name}.`);
      } catch (error) {
        if (cancelled) {
          return;
        }
        setStatus('error');
        setMessage(
          error instanceof ApiError
            ? error.message
            : error instanceof Error
              ? error.message
              : 'Magic-link sign-in failed.',
        );
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="w-full max-w-md rounded-xl bg-white p-8 shadow">
      <h1 className="mb-4 text-2xl font-bold">Parent magic link</h1>
      <p
        className={
          status === 'error'
            ? 'text-sm text-red-700'
            : status === 'ok'
              ? 'text-sm text-emerald-800'
              : 'text-sm text-slate-600'
        }
        role={status === 'error' ? 'alert' : undefined}
      >
        {message}
      </p>
      {status !== 'pending' && (
        <Link
          href="/?module=Parent%20Portal"
          className="mt-6 inline-block rounded-lg bg-black px-4 py-2 text-white"
        >
          Open Parent Portal
        </Link>
      )}
    </div>
  );
}

/** Route entry for ``/parent/magic-link?token=…``. */
export default function ParentMagicLinkPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 p-8">
      <Suspense
        fallback={
          <div className="rounded-xl bg-white p-8 text-sm text-slate-600 shadow">
            Signing you in…
          </div>
        }
      >
        <MagicLinkConsumer />
      </Suspense>
    </main>
  );
}
