'use client';

/**
 * Presentational teacher timetable with daily/weekly views.
 */

import type { Teacher, TeacherScheduleSlot } from '@/lib/api/teachers';

export type TimetableViewMode = 'daily' | 'weekly';

export type TeacherTimetableViewProps = {
  teachers: Teacher[];
  selectedTeacherId: string | null;
  onSelectTeacher: (teacherId: string) => void;
  viewMode: TimetableViewMode;
  onChangeViewMode: (mode: TimetableViewMode) => void;
  rangeLabel: string;
  onShiftRange: (direction: -1 | 1) => void;
  slots: TeacherScheduleSlot[];
  isLoading: boolean;
  error: string | null;
};

function formatTime(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function formatDay(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString([], {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

function statusLabel(status: string): string {
  switch (status) {
    case 'in_progress':
      return 'In progress';
    case 'absent':
      return 'Absent';
    case 'starting_soon':
      return 'Starting soon';
    case 'completed':
      return 'Completed';
    default:
      return 'Upcoming';
  }
}

function statusClass(status: string): string {
  switch (status) {
    case 'in_progress':
      return 'text-emerald-700';
    case 'absent':
      return 'text-red-600';
    case 'starting_soon':
      return 'text-amber-700';
    default:
      return 'text-gray-600';
  }
}

/**
 * Pure UI for teacher selection and timetable slots.
 */
export function TeacherTimetableView({
  teachers,
  selectedTeacherId,
  onSelectTeacher,
  viewMode,
  onChangeViewMode,
  rangeLabel,
  onShiftRange,
  slots,
  isLoading,
  error,
}: TeacherTimetableViewProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-6">
      {error ? (
        <p className="text-red-600 text-sm" role="alert">
          {error}
        </p>
      ) : null}

      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <label className="flex flex-col gap-1 text-sm md:min-w-64">
          Teacher
          <select
            value={selectedTeacherId ?? ''}
            onChange={(event) => onSelectTeacher(event.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="" disabled>
              Select a teacher
            </option>
            {teachers.map((teacher) => (
              <option key={teacher.id} value={teacher.id}>
                {teacher.full_name}
              </option>
            ))}
          </select>
        </label>

        <div className="flex flex-wrap gap-2 items-center">
          <button
            type="button"
            className={`rounded-lg px-4 py-2 border ${
              viewMode === 'daily' ? 'bg-black text-white' : ''
            }`}
            onClick={() => onChangeViewMode('daily')}
          >
            Daily
          </button>
          <button
            type="button"
            className={`rounded-lg px-4 py-2 border ${
              viewMode === 'weekly' ? 'bg-black text-white' : ''
            }`}
            onClick={() => onChangeViewMode('weekly')}
          >
            Weekly
          </button>
          <button
            type="button"
            className="border rounded-lg px-3 py-2"
            onClick={() => onShiftRange(-1)}
            aria-label="Previous range"
          >
            ←
          </button>
          <span className="text-sm font-medium min-w-40 text-center">{rangeLabel}</span>
          <button
            type="button"
            className="border rounded-lg px-3 py-2"
            onClick={() => onShiftRange(1)}
            aria-label="Next range"
          >
            →
          </button>
        </div>
      </div>

      {!selectedTeacherId ? (
        <p>Select a teacher to view their timetable.</p>
      ) : isLoading ? (
        <p>Loading timetable…</p>
      ) : slots.length === 0 ? (
        <p>No lessons in this {viewMode === 'daily' ? 'day' : 'week'}.</p>
      ) : (
        <ul className="divide-y border rounded-xl">
          {slots.map((slot) => (
            <li
              key={`${slot.schedule_id}-${slot.starts_at}`}
              className="p-4 flex flex-col gap-1 md:flex-row md:items-center md:justify-between"
            >
              <div>
                <p className="font-medium">
                  {formatTime(slot.starts_at)} – {formatTime(slot.ends_at)}
                  {viewMode === 'weekly' ? ` · ${formatDay(slot.starts_at)}` : ''}
                </p>
                <p className="text-sm text-gray-600">
                  {slot.student_name ?? 'Student'}
                  {slot.classroom ? ` · ${slot.classroom}` : ''}
                </p>
              </div>
              <p
                className={`text-sm font-semibold ${statusClass(slot.display_status)}`}
                data-testid={`status-${slot.display_status}`}
              >
                {statusLabel(slot.display_status)}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
