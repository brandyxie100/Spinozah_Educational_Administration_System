'use client';

/**
 * Presentational teacher list + create/edit forms (no data fetching).
 */

import { useState, type FormEvent } from 'react';
import type { Teacher } from '@/lib/api/teachers';

export type TeacherListViewProps = {
  teachers: Teacher[];
  total: number;
  isLoading: boolean;
  error: string | null;
  isSaving: boolean;
  onCreate: (input: { full_name: string; email: string }) => void;
  onUpdate: (input: {
    teacherId: string;
    full_name: string;
    email: string;
    is_active: boolean;
  }) => void;
};

/** Pure UI for listing teachers and creating/editing profiles. */
export function TeacherListView({
  teachers,
  total,
  isLoading,
  error,
  isSaving,
  onCreate,
  onUpdate,
}: TeacherListViewProps) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFullName, setEditFullName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editIsActive, setEditIsActive] = useState(true);

  const editingTeacher =
    editingId === null
      ? null
      : (teachers.find((teacher) => teacher.id === editingId) ?? null);

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const name = fullName.trim();
    if (!name) {
      return;
    }
    onCreate({ full_name: name, email: email.trim() });
    setFullName('');
    setEmail('');
  }

  function startEdit(teacher: Teacher) {
    setEditingId(teacher.id);
    setEditFullName(teacher.full_name);
    setEditEmail(teacher.email ?? '');
    setEditIsActive(teacher.is_active);
  }

  function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingTeacher) {
      return;
    }
    const name = editFullName.trim();
    if (!name) {
      return;
    }
    onUpdate({
      teacherId: editingTeacher.id,
      full_name: name,
      email: editEmail.trim(),
      is_active: editIsActive,
    });
    setEditingId(null);
  }

  return (
    <div className="space-y-6 rounded-xl bg-white p-6 shadow">
      {error ? (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}

      <section aria-labelledby="create-teacher-heading">
        <h2 id="create-teacher-heading" className="mb-3 text-lg font-semibold">
          Add teacher
        </h2>
        <form
          onSubmit={handleCreate}
          className="flex flex-col gap-3 md:flex-row md:items-end"
        >
          <label className="flex flex-1 flex-col gap-1 text-sm">
            Full name
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="rounded-lg border px-3 py-2"
              required
              disabled={isSaving}
            />
          </label>
          <label className="flex flex-1 flex-col gap-1 text-sm">
            Email (optional)
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="rounded-lg border px-3 py-2"
              disabled={isSaving}
            />
          </label>
          <button
            type="submit"
            disabled={isSaving}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            Create
          </button>
        </form>
      </section>

      <section aria-labelledby="teachers-list-heading">
        <h2 id="teachers-list-heading" className="mb-3 text-lg font-semibold">
          Teachers ({total})
        </h2>
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : teachers.length === 0 ? (
          <p className="text-sm text-slate-500">No teachers yet.</p>
        ) : (
          <ul className="space-y-3">
            {teachers.map((teacher) => (
              <li key={teacher.id} className="rounded-lg border p-4">
                {editingTeacher?.id === teacher.id ? (
                  <form
                    onSubmit={handleUpdate}
                    className="flex flex-col gap-3 md:flex-row md:items-end"
                  >
                    <label className="flex flex-1 flex-col gap-1 text-sm">
                      Full name
                      <input
                        value={editFullName}
                        onChange={(event) => setEditFullName(event.target.value)}
                        className="rounded-lg border px-3 py-2"
                        required
                        disabled={isSaving}
                      />
                    </label>
                    <label className="flex flex-1 flex-col gap-1 text-sm">
                      Email (optional)
                      <input
                        type="email"
                        value={editEmail}
                        onChange={(event) => setEditEmail(event.target.value)}
                        className="rounded-lg border px-3 py-2"
                        disabled={isSaving}
                      />
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={editIsActive}
                        onChange={(event) =>
                          setEditIsActive(event.target.checked)
                        }
                        disabled={isSaving}
                      />
                      Active
                    </label>
                    <button
                      type="submit"
                      disabled={isSaving}
                      className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
                    >
                      Save
                    </button>
                    <button
                      type="button"
                      disabled={isSaving}
                      onClick={() => setEditingId(null)}
                      className="rounded-lg border px-4 py-2"
                    >
                      Cancel
                    </button>
                  </form>
                ) : (
                  <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
                    <div>
                      <p>
                        <strong>{teacher.full_name}</strong>
                        {!teacher.is_active ? (
                          <span className="ml-2 text-amber-700">(inactive)</span>
                        ) : null}
                      </p>
                      <p className="text-slate-600">
                        {teacher.email ?? 'No email'}
                      </p>
                    </div>
                    <button
                      type="button"
                      disabled={isSaving}
                      onClick={() => startEdit(teacher)}
                      className="rounded-lg border px-3 py-1.5"
                    >
                      Edit
                    </button>
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
