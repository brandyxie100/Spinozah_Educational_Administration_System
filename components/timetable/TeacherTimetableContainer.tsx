'use client';

/**
 * Container: wires teacher list + schedule Query hooks into the timetable view.
 */

import { useMemo, useState } from 'react';
import {
  TeacherTimetableView,
  type TimetableViewMode,
} from '@/components/timetable/TeacherTimetableView';
import { useTeacherSchedule, useTeachersList } from '@/hooks/useTeacherSchedule';
import { ApiError } from '@/lib/api';

function toIsoDate(value: Date): string {
  return value.toISOString().slice(0, 10);
}

function startOfWeek(day: Date): Date {
  const result = new Date(day);
  const weekday = (result.getUTCDay() + 6) % 7; // Monday=0
  result.setUTCDate(result.getUTCDate() - weekday);
  result.setUTCHours(0, 0, 0, 0);
  return result;
}

function addDays(day: Date, amount: number): Date {
  const result = new Date(day);
  result.setUTCDate(result.getUTCDate() + amount);
  return result;
}

function errorMessage(error: unknown): string | null {
  if (!error) {
    return null;
  }
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Something went wrong loading the timetable';
}

/** Teacher Timetable module container. */
export function TeacherTimetableContainer() {
  const teachersQuery = useTeachersList({ page: 1, pageSize: 50 });
  const [selectedTeacherId, setSelectedTeacherId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<TimetableViewMode>('daily');
  const [anchorDate, setAnchorDate] = useState(() => {
    const today = new Date();
    today.setUTCHours(0, 0, 0, 0);
    return today;
  });

  const teachers = teachersQuery.data?.items ?? [];
  const effectiveTeacherId =
    selectedTeacherId ?? (teachers.length > 0 ? teachers[0].id : null);

  const { rangeStart, rangeEnd, rangeLabel } = useMemo(() => {
    if (viewMode === 'daily') {
      const label = anchorDate.toLocaleDateString([], {
        weekday: 'long',
        month: 'short',
        day: 'numeric',
      });
      return {
        rangeStart: toIsoDate(anchorDate),
        rangeEnd: toIsoDate(anchorDate),
        rangeLabel: label,
      };
    }
    const weekStart = startOfWeek(anchorDate);
    const weekEnd = addDays(weekStart, 6);
    return {
      rangeStart: toIsoDate(weekStart),
      rangeEnd: toIsoDate(weekEnd),
      rangeLabel: `${toIsoDate(weekStart)} → ${toIsoDate(weekEnd)}`,
    };
  }, [anchorDate, viewMode]);

  const scheduleQuery = useTeacherSchedule({
    teacherId: effectiveTeacherId,
    rangeStart,
    rangeEnd,
  });

  return (
    <TeacherTimetableView
      teachers={teachers}
      selectedTeacherId={effectiveTeacherId}
      onSelectTeacher={setSelectedTeacherId}
      viewMode={viewMode}
      onChangeViewMode={setViewMode}
      rangeLabel={rangeLabel}
      onShiftRange={(direction) => {
        setAnchorDate((current) =>
          addDays(current, direction * (viewMode === 'daily' ? 1 : 7)),
        );
      }}
      slots={scheduleQuery.data?.items ?? []}
      isLoading={teachersQuery.isLoading || scheduleQuery.isLoading}
      error={errorMessage(teachersQuery.error ?? scheduleQuery.error)}
    />
  );
}
