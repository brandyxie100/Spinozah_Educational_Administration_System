'use client';

/**
 * Presentational Attendance & Leave dashboard (no data fetching).
 */

import { useState, type FormEvent } from 'react';
import type {
  AttendanceRecord,
  LeaveRequest,
  LeaveUsage,
} from '@/lib/api/attendance';
import type { Student } from '@/lib/api/students';

export type AttendanceLeaveViewProps = {
  attendance: AttendanceRecord[];
  leaveRequests: LeaveRequest[];
  students: Student[];
  leaveUsage: LeaveUsage | null;
  usageStudentId: string;
  isLoading: boolean;
  error: string | null;
  isMutating: boolean;
  onUsageStudentChange: (studentId: string) => void;
  onCheckIn: (scheduleId: string) => void;
  onConfirm: (attendanceId: string, outcome: 'present' | 'absent') => void;
  onCreateLeave: (input: {
    studentId: string;
    leaveDate: string;
    kind: 'sick' | 'personal';
    reason: string;
  }) => void;
  onApproveLeave: (leaveId: string) => void;
  onRejectLeave: (leaveId: string) => void;
};

/** Pure UI for check-in confirmation and leave approval. */
export function AttendanceLeaveView({
  attendance,
  leaveRequests,
  students,
  leaveUsage,
  usageStudentId,
  isLoading,
  error,
  isMutating,
  onUsageStudentChange,
  onCheckIn,
  onConfirm,
  onCreateLeave,
  onApproveLeave,
  onRejectLeave,
}: AttendanceLeaveViewProps) {
  const [scheduleId, setScheduleId] = useState('');
  const [leaveStudentId, setLeaveStudentId] = useState('');
  const [leaveDate, setLeaveDate] = useState('');
  const [leaveKind, setLeaveKind] = useState<'sick' | 'personal'>('sick');
  const [leaveReason, setLeaveReason] = useState('');

  function handleCheckIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = scheduleId.trim();
    if (!trimmed) {
      return;
    }
    onCheckIn(trimmed);
    setScheduleId('');
  }

  function handleCreateLeave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!leaveStudentId || !leaveDate) {
      return;
    }
    onCreateLeave({
      studentId: leaveStudentId,
      leaveDate,
      kind: leaveKind,
      reason: leaveReason.trim(),
    });
    setLeaveReason('');
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
        <h2 className="mb-2 text-xl font-bold">Free leave usage</h2>
        <p className="mb-3 text-sm text-slate-600">
          First {leaveUsage?.free_limit ?? 2} approved leaves per term are free;
          extras extend the semester.
        </p>
        <label className="block text-sm font-medium text-slate-700">
          Student
          <select
            value={usageStudentId}
            onChange={(event) => onUsageStudentChange(event.target.value)}
            className="mt-1 block w-full rounded-lg border p-2"
          >
            <option value="">Select a student…</option>
            {students.map((student) => (
              <option key={student.id} value={student.id}>
                {student.full_name}
              </option>
            ))}
          </select>
        </label>
        {leaveUsage && (
          <p className="mt-3 text-lg">
            Free leaves used:{' '}
            <strong>
              {leaveUsage.free_used}/{leaveUsage.free_limit}
            </strong>{' '}
            ({leaveUsage.free_remaining} remaining · {leaveUsage.approved_count}{' '}
            approved total)
          </p>
        )}
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Check-in</h2>
        <form onSubmit={handleCheckIn} className="mb-6 flex flex-wrap gap-3">
          <input
            type="text"
            value={scheduleId}
            onChange={(event) => setScheduleId(event.target.value)}
            placeholder="Schedule UUID"
            className="min-w-[240px] flex-1 rounded-lg border p-2 font-mono text-sm"
          />
          <button
            type="submit"
            disabled={isMutating || !scheduleId.trim()}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            Create check-in
          </button>
        </form>

        <h3 className="mb-2 font-semibold">Pending confirmation</h3>
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : attendance.length === 0 ? (
          <p className="text-sm text-slate-500">No pending check-ins.</p>
        ) : (
          <ul className="space-y-3">
            {attendance.map((row) => (
              <li
                key={row.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3"
              >
                <div className="text-sm">
                  <p>
                    <strong>{studentName(row.student_id)}</strong> · {row.status}
                  </p>
                  <p className="font-mono text-xs text-slate-500">
                    schedule {row.schedule_id}
                  </p>
                  {row.remaining_lessons !== null && (
                    <p className="text-slate-600">
                      Remaining lessons: {row.remaining_lessons}
                    </p>
                  )}
                </div>
                {row.status === 'pending_confirmation' && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => onConfirm(row.id, 'present')}
                      className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                    >
                      Present
                    </button>
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => onConfirm(row.id, 'absent')}
                      className="rounded-lg bg-slate-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                    >
                      Absent
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">Leave requests</h2>
        <form onSubmit={handleCreateLeave} className="mb-6 grid gap-3 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Student
            <select
              value={leaveStudentId}
              onChange={(event) => setLeaveStudentId(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              required
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
            Leave date
            <input
              type="date"
              value={leaveDate}
              onChange={(event) => setLeaveDate(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              required
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Kind
            <select
              value={leaveKind}
              onChange={(event) =>
                setLeaveKind(event.target.value as 'sick' | 'personal')
              }
              className="mt-1 block w-full rounded-lg border p-2"
            >
              <option value="sick">Sick</option>
              <option value="personal">Personal</option>
            </select>
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Reason (optional)
            <input
              type="text"
              value={leaveReason}
              onChange={(event) => setLeaveReason(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
            />
          </label>
          <button
            type="submit"
            disabled={isMutating || !leaveStudentId || !leaveDate}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2"
          >
            Submit leave request
          </button>
        </form>

        {leaveRequests.length === 0 ? (
          <p className="text-sm text-slate-500">No leave requests yet.</p>
        ) : (
          <ul className="space-y-3">
            {leaveRequests.map((leave) => (
              <li
                key={leave.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3"
              >
                <div className="text-sm">
                  <p>
                    <strong>{studentName(leave.student_id)}</strong> ·{' '}
                    {leave.leave_date} · {leave.kind} · {leave.status}
                  </p>
                  {leave.reason && (
                    <p className="text-slate-600">{leave.reason}</p>
                  )}
                  {leave.is_free !== null && leave.status === 'approved' && (
                    <p className="text-slate-600">
                      {leave.is_free
                        ? 'Free leave'
                        : `Extended +${leave.extension_days_applied} days`}
                    </p>
                  )}
                </div>
                {leave.status === 'pending' && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => onApproveLeave(leave.id)}
                      className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => onRejectLeave(leave.id)}
                      className="rounded-lg bg-slate-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                    >
                      Reject
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
