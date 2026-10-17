'use client';

/**
 * Presentational staff login form (no data fetching).
 */

import { useState, type FormEvent } from 'react';

export type StaffLoginViewProps = {
  isMutating: boolean;
  error: string | null;
  onLogin: (input: {
    tenantSlug: string;
    email: string;
    password: string;
  }) => void;
};

/** Pure UI for tenant-scoped staff login. */
export function StaffLoginView({
  isMutating,
  error,
  onLogin,
}: StaffLoginViewProps) {
  const [tenantSlug, setTenantSlug] = useState('demo');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!tenantSlug.trim() || !email.trim() || !password) {
      return;
    }
    onLogin({
      tenantSlug: tenantSlug.trim(),
      email: email.trim(),
      password,
    });
  }

  return (
    <section className="mx-auto max-w-md rounded-2xl border border-sp-hairline bg-sp-surface p-6 text-sp-ink shadow-sm">
      <h2 className="mb-2 font-[family-name:var(--font-fraunces)] text-xl font-semibold">
        Staff sign in
      </h2>
      <p className="mb-4 text-sm text-sp-muted">
        Sign in to call FastAPI ops modules (students, attendance, finance,
        admin).
      </p>
      {error && (
        <p
          className="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700"
          role="alert"
        >
          {error}
        </p>
      )}
      <form onSubmit={handleSubmit} className="grid gap-3">
        <label className="block text-sm font-medium text-sp-ink">
          Tenant slug
          <input
            type="text"
            value={tenantSlug}
            onChange={(event) => setTenantSlug(event.target.value)}
            className="mt-1 block w-full rounded-lg border border-sp-hairline bg-sp-canvas p-2 text-sp-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sp-orange"
            required
          />
        </label>
        <label className="block text-sm font-medium text-sp-ink">
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 block w-full rounded-lg border border-sp-hairline bg-sp-canvas p-2 text-sp-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sp-orange"
            required
          />
        </label>
        <label className="block text-sm font-medium text-sp-ink">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 block w-full rounded-lg border border-sp-hairline bg-sp-canvas p-2 text-sp-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sp-orange"
            required
          />
        </label>
        <button
          type="submit"
          disabled={isMutating}
          className="rounded-full bg-sp-orange px-4 py-2.5 font-medium text-white transition-colors hover:bg-sp-orange/90 disabled:opacity-50"
        >
          Sign in
        </button>
      </form>
    </section>
  );
}
