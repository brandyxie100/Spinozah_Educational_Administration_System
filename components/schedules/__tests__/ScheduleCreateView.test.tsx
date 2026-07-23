/**
 * Presenter tests for ScheduleCreateView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { ScheduleCreateView } from '@/components/schedules/ScheduleCreateView';
import type { Schedule } from '@/lib/api/schedules';
import type { Student } from '@/lib/api/students';
import type { Teacher } from '@/lib/api/teachers';

const teachers: Teacher[] = [
  {
    id: 't1',
    tenant_id: 'ten1',
    full_name: 'Ada Teacher',
    email: 'ada@example.com',
    user_id: null,
    is_active: true,
  },
];

const students: Student[] = [
  {
    id: 's1',
    tenant_id: 'ten1',
    full_name: 'Sam Student',
    email: null,
    is_active: true,
  },
];

const created: Schedule[] = [
  {
    id: 'sch1',
    tenant_id: 'ten1',
    teacher_id: 't1',
    student_id: 's1',
    classroom: 'A1',
    starts_at: '2026-07-21T10:00:00.000Z',
    ends_at: '2026-07-21T11:00:00.000Z',
    status: 'scheduled',
    is_recurring: false,
    recurrence_weekday: null,
    recurrence_until: null,
  },
];

describe('ScheduleCreateView', () => {
  it('renders created schedules and submits create form', () => {
    const onCreate = jest.fn();
    render(
      <ScheduleCreateView
        teachers={teachers}
        students={students}
        createdSchedules={created}
        isLoadingOptions={false}
        isSaving={false}
        error={null}
        onCreate={onCreate}
      />,
    );

    expect(screen.getByText('Created this session')).toBeInTheDocument();
    expect(screen.getByText('sch1')).toBeInTheDocument();
    expect(screen.getAllByText('Ada Teacher').length).toBeGreaterThan(0);

    fireEvent.change(screen.getByLabelText(/^Teacher$/), {
      target: { value: 't1' },
    });
    fireEvent.change(screen.getByLabelText(/^Student$/), {
      target: { value: 's1' },
    });
    fireEvent.change(screen.getByLabelText(/^Starts at$/), {
      target: { value: '2026-07-22T09:00' },
    });
    fireEvent.change(screen.getByLabelText(/^Ends at$/), {
      target: { value: '2026-07-22T10:00' },
    });
    fireEvent.change(screen.getByLabelText(/Classroom/), {
      target: { value: 'B2' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create schedule' }));

    expect(onCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        teacherId: 't1',
        studentId: 's1',
        classroom: 'B2',
        isRecurring: false,
        recurrenceUntil: '',
      }),
    );
    expect(onCreate.mock.calls[0][0].startsAt).toMatch(
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/,
    );
    expect(onCreate.mock.calls[0][0].endsAt).toMatch(
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/,
    );
  });

  it('shows empty session message when none created', () => {
    render(
      <ScheduleCreateView
        teachers={teachers}
        students={students}
        createdSchedules={[]}
        isLoadingOptions={false}
        isSaving={false}
        error={null}
        onCreate={jest.fn()}
      />,
    );

    expect(
      screen.getByText(/No schedules created yet/),
    ).toBeInTheDocument();
  });
});
