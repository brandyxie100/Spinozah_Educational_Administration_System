'use client';

/**
 * Presentational schedule create form + created-session list.
 */

import { useState, type FormEvent } from 'react';
import type { Schedule } from '@/lib/api/schedules';
import type { Student } from '@/lib/api/students';
import type { Teacher } from '@/lib/api/teachers';

export type ScheduleCreateViewProps = {
  teachers: Teacher[];
  students: Student[];
  createdSchedules: Schedule[];
  isLoadingOptions: boolean;
  isSaving: boolean;
  error: string | null;
  onCreate: (input: {
    teacherId: string;
    studentId: string;
    startsAt: string;
    endsAt: string;
    classroom: string;
    isRecurring: boolean;
    recurrenceUntil: string;
  }) => void;
};

function toIsoFromLocal(value: string): string {
  // datetime-local → ISO; empty stays empty for validation upstream.
  if (!value) {
    return value;
  }
  const date = new Date(value);
  return date.toISOString();
}

/** Pure UI for creating schedules and showing confirmed creates. */
export function ScheduleCreateView({
  teachers,
  students,
  createdSchedules,
  isLoadingOptions,
  isSaving,
  error,
  onCreate,
}: ScheduleCreateViewProps) {
  const [teacherId, setTeacherId] = useState('');
  const [studentId, setStudentId] = useState('');
  const [startsAt, setStartsAt] = useState('');
  const [endsAt, setEndsAt] = useState('');
  const [classroom, setClassroom] = useState('');
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceUntil, setRecurrenceUntil] = useState('');

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!teacherId || !studentId || !startsAt || !endsAt) {
      return;
    }
    onCreate({
      teacherId,
      studentId,
      startsAt: toIsoFromLocal(startsAt),
      endsAt: toIsoFromLocal(endsAt),
      classroom: classroom.trim(),
      isRecurring,
      recurrenceUntil: recurrenceUntil.trim(),
    });
  }

  const teacherName = (id: string) =>
    teachers.find((teacher) => teacher.id === id)?.full_name ?? id.slice(0, 8);
  const studentName = (id: string) =>
    students.find((student) => student.id === id)?.full_name ?? id.slice(0, 8);

  return (
    <div className="space-y-8">
      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
          {error}
        </p>
      )}

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Create schedule</h2>
        {isLoadingOptions ? (
          <p className="text-sm text-slate-500">Loading teachers and students…</p>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="grid gap-3 sm:grid-cols-2"
          >
            <label className="block text-sm font-medium text-slate-700">
              Teacher
              <select
                value={teacherId}
                onChange={(event) => setTeacherId(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
                disabled={isSaving}
              >
                <option value="">Select…</option>
                {teachers.map((teacher) => (
                  <option key={teacher.id} value={teacher.id}>
                    {teacher.full_name}
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
                <option value="">Select…</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.full_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Starts at
              <input
                type="datetime-local"
                value={startsAt}
                onChange={(event) => setStartsAt(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
                disabled={isSaving}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Ends at
              <input
                type="datetime-local"
                value={endsAt}
                onChange={(event) => setEndsAt(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                required
                disabled={isSaving}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Classroom (optional)
              <input
                type="text"
                value={classroom}
                onChange={(event) => setClassroom(event.target.value)}
                className="mt-1 block w-full rounded-lg border p-2"
                disabled={isSaving}
              />
            </label>
            <label className="flex items-center gap-2 self-end text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={isRecurring}
                onChange={(event) => setIsRecurring(event.target.checked)}
                disabled={isSaving}
              />
              Weekly recurring
            </label>
            {isRecurring ? (
              <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
                Recurrence until
                <input
                  type="date"
                  value={recurrenceUntil}
                  onChange={(event) => setRecurrenceUntil(event.target.value)}
                  className="mt-1 block w-full rounded-lg border p-2"
                  required
                  disabled={isSaving}
                />
              </label>
            ) : null}
            <button
              type="submit"
              disabled={isSaving || !teacherId || !studentId}
              className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2"
            >
              Create schedule
            </button>
          </form>
        )}
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Created this session</h2>
        {createdSchedules.length === 0 ? (
          <p className="text-sm text-slate-500">
            No schedules created yet. Use the form above — each successful create
            appears here with its schedule id (for attendance check-in).
          </p>
        ) : (
          <ul className="space-y-3">
            {createdSchedules.map((schedule) => (
              <li
                key={schedule.id}
                className="rounded-lg border p-4 text-sm"
              >
                <p>
                  <strong>{teacherName(schedule.teacher_id)}</strong> ·{' '}
                  {studentName(schedule.student_id)}
                </p>
                <p className="text-slate-600">
                  {new Date(schedule.starts_at).toLocaleString()} →{' '}
                  {new Date(schedule.ends_at).toLocaleString()}
                  {schedule.classroom ? ` · ${schedule.classroom}` : ''}
                </p>
                <p className="font-mono text-xs text-slate-500">{schedule.id}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
