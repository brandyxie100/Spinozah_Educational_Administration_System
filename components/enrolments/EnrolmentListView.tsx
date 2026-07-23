'use client';

/**
 * Presentational staff UI for student enrolment packages.
 */

import { useState, type FormEvent } from 'react';
import type { Enrolment } from '@/lib/api/enrolments';
import type { Student } from '@/lib/api/students';

export type EnrolmentListViewProps = {
  students: Student[];
  enrolments: Enrolment[];
  selectedStudentId: string;
  isLoading: boolean;
  error: string | null;
  isSaving: boolean;
  onSelectStudent: (studentId: string) => void;
  onCreate: (input: { studentId: string; totalLessons: number }) => void;
  onUpdateRemaining: (input: {
    enrolmentId: string;
    remainingLessons: number;
  }) => void;
};

/** Pure UI to create and adjust enrolments for a selected student. */
export function EnrolmentListView({
  students,
  enrolments,
  selectedStudentId,
  isLoading,
  error,
  isSaving,
  onSelectStudent,
  onCreate,
  onUpdateRemaining,
}: EnrolmentListViewProps) {
  const [totalLessons, setTotalLessons] = useState('10');
  const [editRemaining, setEditRemaining] = useState<Record<string, string>>(
    {},
  );

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedStudentId) {
      return;
    }
    const parsed = Number.parseInt(totalLessons, 10);
    if (Number.isNaN(parsed) || parsed < 0) {
      return;
    }
    onCreate({ studentId: selectedStudentId, totalLessons: parsed });
  }

  const studentName = (studentId: string) =>
    students.find((student) => student.id === studentId)?.full_name ??
    studentId.slice(0, 8);

  return (
    <div className="space-y-8">
      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
          {error}
        </p>
      )}

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Student</h2>
        <label className="block text-sm font-medium text-slate-700">
          Select student
          <select
            value={selectedStudentId}
            onChange={(event) => onSelectStudent(event.target.value)}
            className="mt-1 block w-full rounded-lg border p-2"
            disabled={isSaving}
          >
            <option value="">All students (list only)</option>
            {students.map((student) => (
              <option key={student.id} value={student.id}>
                {student.full_name}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Create enrolment</h2>
        <form onSubmit={handleCreate} className="flex flex-wrap gap-3">
          <label className="block text-sm font-medium text-slate-700">
            Total lessons
            <input
              type="number"
              min={0}
              value={totalLessons}
              onChange={(event) => setTotalLessons(event.target.value)}
              className="mt-1 block w-40 rounded-lg border p-2"
              disabled={isSaving || !selectedStudentId}
              required
            />
          </label>
          <button
            type="submit"
            disabled={isSaving || !selectedStudentId}
            className="self-end rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            Create package
          </button>
        </form>
        {!selectedStudentId && (
          <p className="mt-2 text-sm text-slate-500">
            Select a student above to create a lesson package.
          </p>
        )}
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">
          Enrolments{selectedStudentId ? '' : ' (all)'}
        </h2>
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : enrolments.length === 0 ? (
          <p className="text-sm text-slate-500">No enrolments yet.</p>
        ) : (
          <ul className="space-y-3">
            {enrolments.map((enrolment) => {
              const remainingValue =
                editRemaining[enrolment.id] ??
                String(enrolment.remaining_lessons);
              return (
                <li
                  key={enrolment.id}
                  className="rounded-lg border p-4 text-sm"
                >
                  <p>
                    <strong>{studentName(enrolment.student_id)}</strong> ·{' '}
                    {enrolment.status}
                  </p>
                  <p className="text-slate-600">
                    Remaining {enrolment.remaining_lessons} / total{' '}
                    {enrolment.total_lessons} (completed{' '}
                    {enrolment.completed_lessons})
                    {enrolment.extension_days > 0
                      ? ` · +${enrolment.extension_days}d extension`
                      : ''}
                  </p>
                  <form
                    className="mt-3 flex flex-wrap items-end gap-2"
                    onSubmit={(event) => {
                      event.preventDefault();
                      const parsed = Number.parseInt(remainingValue, 10);
                      if (Number.isNaN(parsed) || parsed < 0) {
                        return;
                      }
                      onUpdateRemaining({
                        enrolmentId: enrolment.id,
                        remainingLessons: parsed,
                      });
                    }}
                  >
                    <label className="block text-sm font-medium text-slate-700">
                      Set remaining
                      <input
                        type="number"
                        min={0}
                        value={remainingValue}
                        onChange={(event) =>
                          setEditRemaining((prev) => ({
                            ...prev,
                            [enrolment.id]: event.target.value,
                          }))
                        }
                        className="mt-1 block w-32 rounded-lg border p-2"
                        disabled={isSaving}
                        aria-label={`Remaining lessons for ${enrolment.id}`}
                      />
                    </label>
                    <button
                      type="submit"
                      disabled={isSaving}
                      className="rounded-lg bg-slate-800 px-3 py-2 text-white disabled:opacity-50"
                    >
                      Save
                    </button>
                  </form>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
