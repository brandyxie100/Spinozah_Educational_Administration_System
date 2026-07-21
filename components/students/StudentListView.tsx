'use client';

/**
 * Presentational student list + create/edit forms (no data fetching).
 */

import { useState, type FormEvent } from 'react';
import type { Student } from '@/lib/api/students';

export type StudentListViewProps = {
  students: Student[];
  total: number;
  isLoading: boolean;
  error: string | null;
  isSaving: boolean;
  onCreate: (input: { full_name: string; email: string }) => void;
  onUpdate: (input: {
    studentId: string;
    full_name: string;
    email: string;
    is_active: boolean;
  }) => void;
};

/**
 * Pure UI for listing students and creating/editing profiles.
 */
export function StudentListView({
  students,
  total,
  isLoading,
  error,
  isSaving,
  onCreate,
  onUpdate,
}: StudentListViewProps) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFullName, setEditFullName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editIsActive, setEditIsActive] = useState(true);

  // Derive from list so a deleted/refreshed row exits edit mode without an effect.
  const editingStudent =
    editingId === null
      ? null
      : (students.find((student) => student.id === editingId) ?? null);

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

  function startEdit(student: Student) {
    setEditingId(student.id);
    setEditFullName(student.full_name);
    setEditEmail(student.email ?? '');
    setEditIsActive(student.is_active);
  }

  function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingStudent) {
      return;
    }
    const name = editFullName.trim();
    if (!name) {
      return;
    }
    onUpdate({
      studentId: editingStudent.id,
      full_name: name,
      email: editEmail.trim(),
      is_active: editIsActive,
    });
    setEditingId(null);
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-6">
      {error ? (
        <p className="text-red-600 text-sm" role="alert">
          {error}
        </p>
      ) : null}

      <section aria-labelledby="create-student-heading">
        <h2 id="create-student-heading" className="text-lg font-semibold mb-3">
          Add student
        </h2>
        <form onSubmit={handleCreate} className="flex flex-col gap-3 md:flex-row md:items-end">
          <label className="flex flex-col gap-1 flex-1 text-sm">
            Full name
            <input
              name="full_name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="border rounded-lg px-3 py-2"
              required
              disabled={isSaving}
            />
          </label>
          <label className="flex flex-col gap-1 flex-1 text-sm">
            Email (optional)
            <input
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="border rounded-lg px-3 py-2"
              disabled={isSaving}
            />
          </label>
          <button
            type="submit"
            disabled={isSaving}
            className="bg-black text-white rounded-lg px-4 py-2 disabled:opacity-50"
          >
            {isSaving ? 'Saving…' : 'Create'}
          </button>
        </form>
      </section>

      <section aria-labelledby="student-list-heading">
        <h2 id="student-list-heading" className="text-lg font-semibold mb-3">
          Students ({total})
        </h2>
        {isLoading ? (
          <p>Loading students…</p>
        ) : students.length === 0 ? (
          <p>No students yet. Create one above.</p>
        ) : (
          <ul className="divide-y border rounded-xl">
            {students.map((student) => (
              <li key={student.id} className="p-4">
                {editingStudent?.id === student.id ? (
                  <form onSubmit={handleUpdate} className="space-y-3">
                    <label className="flex flex-col gap-1 text-sm">
                      Full name
                      <input
                        name="edit_full_name"
                        value={editFullName}
                        onChange={(event) => setEditFullName(event.target.value)}
                        className="border rounded-lg px-3 py-2"
                        required
                        disabled={isSaving}
                      />
                    </label>
                    <label className="flex flex-col gap-1 text-sm">
                      Email
                      <input
                        name="edit_email"
                        type="email"
                        value={editEmail}
                        onChange={(event) => setEditEmail(event.target.value)}
                        className="border rounded-lg px-3 py-2"
                        disabled={isSaving}
                      />
                    </label>
                    <label className="inline-flex items-center gap-2 text-sm">
                      <input
                        name="edit_is_active"
                        type="checkbox"
                        checked={editIsActive}
                        onChange={(event) => setEditIsActive(event.target.checked)}
                        disabled={isSaving}
                      />
                      Active
                    </label>
                    <div className="flex gap-2">
                      <button
                        type="submit"
                        disabled={isSaving}
                        className="bg-black text-white rounded-lg px-4 py-2 disabled:opacity-50"
                      >
                        Save
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditingId(null)}
                        className="border rounded-lg px-4 py-2"
                        disabled={isSaving}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="font-medium">{student.full_name}</p>
                      <p className="text-sm text-gray-600">
                        {student.email ?? 'No email'} ·{' '}
                        {student.is_active ? 'Active' : 'Inactive'}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => startEdit(student)}
                      className="border rounded-lg px-4 py-2 self-start"
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
