'use client';

/**
 * Presentational staff UI to link parent users to students.
 */

import { useState, type FormEvent } from 'react';
import type { ParentStudentLink } from '@/lib/api/parent';
import type { Student } from '@/lib/api/students';
import type { User } from '@/lib/api/users';

export type ParentStudentLinkViewProps = {
  parents: User[];
  students: Student[];
  createdLinks: ParentStudentLink[];
  isLoadingOptions: boolean;
  isSaving: boolean;
  error: string | null;
  onCreate: (input: { parentUserId: string; studentId: string }) => void;
};

/** Pure UI for creating parent↔student links and confirming creates. */
export function ParentStudentLinkView({
  parents,
  students,
  createdLinks,
  isLoadingOptions,
  isSaving,
  error,
  onCreate,
}: ParentStudentLinkViewProps) {
  const [parentUserId, setParentUserId] = useState('');
  const [studentId, setStudentId] = useState('');

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!parentUserId || !studentId) {
      return;
    }
    onCreate({ parentUserId, studentId });
  }

  const parentLabel = (id: string) => {
    const parent = parents.find((user) => user.id === id);
    return parent
      ? `${parent.full_name} (${parent.email})`
      : id.slice(0, 8);
  };
  const studentLabel = (id: string) =>
    students.find((student) => student.id === id)?.full_name ?? id.slice(0, 8);

  return (
    <div className="space-y-8">
      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
          {error}
        </p>
      )}

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-2 text-xl font-bold">Link parent to student</h2>
        <p className="mb-4 text-sm text-slate-600">
          Required before a parent can see that student in the Parent Portal.
          Only users with the parent role appear below.
        </p>
        {isLoadingOptions ? (
          <p className="text-sm text-slate-500">Loading parents and students…</p>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="grid gap-3 sm:grid-cols-2"
          >
            <label className="block text-sm font-medium text-slate-700">
              Parent user
              <select
                value={parentUserId}
                onChange={(event) => setParentUserId(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
                disabled={isSaving}
              >
                <option value="">
                  {parents.length === 0
                    ? 'No parent users found'
                    : 'Select a parent…'}
                </option>
                {parents.map((parent) => (
                  <option key={parent.id} value={parent.id}>
                    {parent.full_name} ({parent.email})
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Student
              <select
                value={studentId}
                onChange={(event) => setStudentId(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
                disabled={isSaving}
              >
                <option value="">Select a student…</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.full_name}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="submit"
              disabled={isSaving || !parentUserId || !studentId}
              className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2"
            >
              Create link
            </button>
          </form>
        )}
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Created this session</h2>
        {createdLinks.length === 0 ? (
          <p className="text-sm text-slate-500">
            No links created yet. Successful creates appear here.
          </p>
        ) : (
          <ul className="space-y-3">
            {createdLinks.map((link) => (
              <li key={link.id} className="rounded-lg border p-4 text-sm">
                <p>
                  <strong>{parentLabel(link.parent_user_id)}</strong>
                  {' → '}
                  {studentLabel(link.student_id)}
                </p>
                <p className="font-mono text-xs text-slate-500">{link.id}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
