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
import type { Teacher, TeacherScheduleSlot } from '@/lib/api/teachers';

export type AttendanceLeaveViewProps = {
  attendance: AttendanceRecord[];
  leaveRequests: LeaveRequest[];
  students: Student[];
  teachers: Teacher[];
  scheduleSlots: TeacherScheduleSlot[];
  checkInTeacherId: string;
  checkInDate: string;
  leaveUsage: LeaveUsage | null;
  usageStudentId: string;
  isLoading: boolean;
  isLoadingSlots: boolean;
  error: string | null;
  isMutating: boolean;
  onUsageStudentChange: (studentId: string) => void;
  onCheckInTeacherChange: (teacherId: string) => void;
  onCheckInDateChange: (date: string) => void;
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

function formatSlotLabel(slot: TeacherScheduleSlot): string {
  const start = new Date(slot.starts_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
  const end = new Date(slot.ends_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
  const student = slot.student_name ?? 'Student';
  const room = slot.classroom ? ` · ${slot.classroom}` : '';
  return `${start}–${end} · ${student}${room}`;
}

/** Pure UI for check-in confirmation and leave approval. */
export function AttendanceLeaveView({
  attendance,
  leaveRequests,
  students,
  teachers,
  scheduleSlots,
  checkInTeacherId,
  checkInDate,
  leaveUsage,
  usageStudentId,
  isLoading,
  isLoadingSlots,
  error,
  isMutating,
  onUsageStudentChange,
  onCheckInTeacherChange,
  onCheckInDateChange,
  onCheckIn,
  onConfirm,
  onCreateLeave,
  onApproveLeave,
  onRejectLeave,
}: AttendanceLeaveViewProps) {
  const [selectedScheduleId, setSelectedScheduleId] = useState('');
  const [leaveStudentId, setLeaveStudentId] = useState('');
  const [leaveDate, setLeaveDate] = useState('');
  const [leaveKind, setLeaveKind] = useState<'sick' | 'personal'>('sick');
  const [leaveReason, setLeaveReason] = useState('');

  function handleCheckIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedScheduleId) {
      return;
    }
    onCheckIn(selectedScheduleId);
    setSelectedScheduleId('');
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
        <form
          onSubmit={handleCheckIn}
          className="mb-6 grid gap-3 sm:grid-cols-2"
        >
          <label className="block text-sm font-medium text-slate-700">
            Teacher
            <select
              value={checkInTeacherId}
              onChange={(event) => {
                onCheckInTeacherChange(event.target.value);
                setSelectedScheduleId('');
              }}
              className="mt-1 block w-full rounded-lg border p-2"
              disabled={isMutating}
            >
              <option value="">Select a teacher…</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.full_name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Lesson date
            <input
              type="date"
              value={checkInDate}
              onChange={(event) => {
                onCheckInDateChange(event.target.value);
                setSelectedScheduleId('');
              }}
              className="mt-1 block w-full rounded-lg border p-2"
              disabled={isMutating}
            />
          </label>
          <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
            Schedule
            <select
              value={selectedScheduleId}
              onChange={(event) => setSelectedScheduleId(event.target.value)}
              className="mt-1 block w-full rounded-lg border p-2"
              disabled={
                isMutating || !checkInTeacherId || isLoadingSlots
              }
              required
            >
              <option value="">
                {!checkInTeacherId
                  ? 'Select a teacher first…'
                  : isLoadingSlots
                    ? 'Loading lessons…'
                    : scheduleSlots.length === 0
                      ? 'No lessons on this date'
                      : 'Select a lesson…'}
              </option>
              {scheduleSlots.map((slot) => (
                <option
                  key={`${slot.schedule_id}-${slot.starts_at}`}
                  value={slot.schedule_id}
                >
                  {formatSlotLabel(slot)}
                </option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            disabled={isMutating || !selectedScheduleId}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50 sm:col-span-2"
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
