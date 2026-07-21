/**
 * Presenter tests for TeacherTimetableView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { TeacherTimetableView } from '@/components/timetable/TeacherTimetableView';
import type { Teacher, TeacherScheduleSlot } from '@/lib/api/teachers';

const teachers: Teacher[] = [
  {
    id: 't1',
    tenant_id: 'ten1',
    full_name: 'Max Teacher',
    email: null,
    user_id: null,
    is_active: true,
  },
];

const slots: TeacherScheduleSlot[] = [
  {
    schedule_id: 's1',
    student_id: 'st1',
    student_name: 'Charlotte',
    classroom: 'Room A',
    starts_at: '2026-10-14T16:00:00.000Z',
    ends_at: '2026-10-14T17:00:00.000Z',
    status: 'not_started',
    display_status: 'in_progress',
  },
  {
    schedule_id: 's2',
    student_id: 'st2',
    student_name: 'Chace',
    classroom: null,
    starts_at: '2026-10-14T17:00:00.000Z',
    ends_at: '2026-10-14T18:00:00.000Z',
    status: 'cancelled',
    display_status: 'absent',
  },
  {
    schedule_id: 's3',
    student_id: 'st3',
    student_name: 'Olivia',
    classroom: null,
    starts_at: '2026-10-14T18:00:00.000Z',
    ends_at: '2026-10-14T19:00:00.000Z',
    status: 'not_started',
    display_status: 'starting_soon',
  },
];

describe('TeacherTimetableView', () => {
  it('should render display statuses and switch to weekly mode', () => {
    const onChangeViewMode = jest.fn();

    render(
      <TeacherTimetableView
        teachers={teachers}
        selectedTeacherId="t1"
        onSelectTeacher={jest.fn()}
        viewMode="daily"
        onChangeViewMode={onChangeViewMode}
        rangeLabel="Wednesday"
        onShiftRange={jest.fn()}
        slots={slots}
        isLoading={false}
        error={null}
      />,
    );

    expect(screen.getByText(/Charlotte/)).toBeInTheDocument();
    expect(screen.getByText('In progress')).toBeInTheDocument();
    expect(screen.getByText('Absent')).toBeInTheDocument();
    expect(screen.getByText('Starting soon')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Weekly' }));
    expect(onChangeViewMode).toHaveBeenCalledWith('weekly');
  });
});
