'use client';

/**
 * Presentational admin user list + create/edit/deactivate (no data fetching).
 */

import { useState, type FormEvent } from 'react';
import type { User, UserRole } from '@/lib/api/users';

export const USER_ROLES: UserRole[] = [
  'admin',
  'frontdesk',
  'teacher',
  'parent',
];

export type UserListViewProps = {
  users: User[];
  total: number;
  isLoading: boolean;
  error: string | null;
  isSaving: boolean;
  onCreate: (input: {
    email: string;
    full_name: string;
    password: string;
    role: UserRole;
  }) => void;
  onUpdate: (input: {
    userId: string;
    full_name: string;
    role: UserRole;
    password: string;
  }) => void;
  onDeactivate: (userId: string) => void;
};

/** Pure UI for listing and managing tenant users. */
export function UserListView({
  users,
  total,
  isLoading,
  error,
  isSaving,
  onCreate,
  onUpdate,
  onDeactivate,
}: UserListViewProps) {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('frontdesk');

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFullName, setEditFullName] = useState('');
  const [editRole, setEditRole] = useState<UserRole>('frontdesk');
  const [editPassword, setEditPassword] = useState('');

  const editingUser =
    editingId === null
      ? null
      : (users.find((user) => user.id === editingId) ?? null);

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const name = fullName.trim();
    if (!name || !email.trim() || password.length < 8) {
      return;
    }
    onCreate({
      email: email.trim(),
      full_name: name,
      password,
      role,
    });
    setEmail('');
    setFullName('');
    setPassword('');
    setRole('frontdesk');
  }

  function startEdit(user: User) {
    setEditingId(user.id);
    setEditFullName(user.full_name);
    setEditRole(user.role as UserRole);
    setEditPassword('');
  }

  function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingUser) {
      return;
    }
    const name = editFullName.trim();
    if (!name) {
      return;
    }
    onUpdate({
      userId: editingUser.id,
      full_name: name,
      role: editRole,
      password: editPassword,
    });
    setEditingId(null);
    setEditPassword('');
  }

  return (
    <div className="space-y-6 rounded-xl bg-white p-6 shadow">
      {error ? (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}

      <section aria-labelledby="create-user-heading">
        <h2 id="create-user-heading" className="mb-3 text-lg font-semibold">
          Add user
        </h2>
        <form
          onSubmit={handleCreate}
          className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
        >
          <label className="block text-sm font-medium text-slate-700">
            Full name
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              required
              disabled={isSaving}
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              required
              disabled={isSaving}
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Password (min 8)
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              minLength={8}
              required
              disabled={isSaving}
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Role
            <select
              value={role}
              onChange={(event) => setRole(event.target.value as UserRole)}
              className="mt-1 block w-full rounded-lg border p-2"
              disabled={isSaving}
            >
              {USER_ROLES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            disabled={isSaving}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2 lg:col-span-3"
          >
            Create user
          </button>
        </form>
      </section>

      <section aria-labelledby="users-list-heading">
        <h2 id="users-list-heading" className="mb-3 text-lg font-semibold">
          Users ({total})
        </h2>
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : users.length === 0 ? (
          <p className="text-sm text-slate-500">No users yet.</p>
        ) : (
          <ul className="space-y-3">
            {users.map((user) => (
              <li key={user.id} className="rounded-lg border p-4">
                {editingUser?.id === user.id ? (
                  <form onSubmit={handleUpdate} className="grid gap-3 sm:grid-cols-2">
                    <label className="block text-sm font-medium text-slate-700">
                      Full name
                      <input
                        value={editFullName}
                        onChange={(event) => setEditFullName(event.target.value)}
                        className="mt-1 block w-full rounded-lg border p-2"
                        required
                        disabled={isSaving}
                      />
                    </label>
                    <label className="block text-sm font-medium text-slate-700">
                      Role
                      <select
                        value={editRole}
                        onChange={(event) =>
                          setEditRole(event.target.value as UserRole)
                        }
                        className="mt-1 block w-full rounded-lg border p-2"
                        disabled={isSaving}
                      >
                        {USER_ROLES.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
                      New password (optional)
                      <input
                        type="password"
                        value={editPassword}
                        onChange={(event) => setEditPassword(event.target.value)}
                        className="mt-1 block w-full rounded-lg border p-2"
                        minLength={8}
                        disabled={isSaving}
                      />
                    </label>
                    <div className="flex gap-2 sm:col-span-2">
                      <button
                        type="submit"
                        disabled={isSaving}
                        className="rounded-lg bg-black px-3 py-1.5 text-sm text-white disabled:opacity-50"
                      >
                        Save
                      </button>
                      <button
                        type="button"
                        disabled={isSaving}
                        onClick={() => setEditingId(null)}
                        className="rounded-lg border px-3 py-1.5 text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="text-sm">
                      <p>
                        <strong>{user.full_name}</strong> · {user.role}
                        {!user.is_active ? (
                          <span className="ml-2 text-amber-700">(inactive)</span>
                        ) : null}
                      </p>
                      <p className="text-slate-600">{user.email}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        disabled={isSaving}
                        onClick={() => startEdit(user)}
                        className="rounded-lg border px-3 py-1.5 text-sm"
                      >
                        Edit
                      </button>
                      {user.is_active ? (
                        <button
                          type="button"
                          disabled={isSaving}
                          onClick={() => onDeactivate(user.id)}
                          className="rounded-lg bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                        >
                          Deactivate
                        </button>
                      ) : null}
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
