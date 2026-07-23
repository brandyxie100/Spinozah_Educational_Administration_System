/**
 * Presenter tests for AttendanceLeaveView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { AttendanceLeaveView } from '@/components/attendance/AttendanceLeaveView';
import type { AttendanceRecord, LeaveRequest } from '@/lib/api/attendance';
import type { Student } from '@/lib/api/students';
import type { Teacher, TeacherScheduleSlot } from '@/lib/api/teachers';

const students: Student[] = [
  {
    id: 'stu-1',
    tenant_id: 't1',
    full_name: 'Charlotte',
    email: null,
    is_active: true,
  },
];

const teachers: Teacher[] = [
  {
    id: 'tch-1',
    tenant_id: 't1',
    full_name: 'Ada Teacher',
    email: 'ada@example.com',
    user_id: null,
    is_active: true,
  },
];

const scheduleSlots: TeacherScheduleSlot[] = [
  {
    schedule_id: 'sch-pick-1',
    student_id: 'stu-1',
    student_name: 'Charlotte',
    classroom: 'A1',
    starts_at: '2026-07-21T10:00:00.000Z',
    ends_at: '2026-07-21T11:00:00.000Z',
    status: 'scheduled',
    display_status: 'upcoming',
  },
];

const attendance: AttendanceRecord[] = [
  {
    id: 'att-1',
    tenant_id: 't1',
    schedule_id: 'sch-1',
    student_id: 'stu-1',
    enrolment_id: 'enr-1',
    status: 'pending_confirmation',
    remaining_lessons: 8,
  },
];

const leaveRequests: LeaveRequest[] = [
  {
    id: 'lv-1',
    tenant_id: 't1',
    student_id: 'stu-1',
    enrolment_id: 'enr-1',
    leave_date: '2026-11-12',
    kind: 'sick',
    reason: 'Fever',
    status: 'pending',
    is_free: null,
    extension_days_applied: 0,
  },
];

const baseProps = {
  attendance,
  leaveRequests,
  students,
  teachers,
  scheduleSlots,
  checkInTeacherId: 'tch-1',
  checkInDate: '2026-07-21',
  leaveUsage: {
    student_id: 'stu-1',
    enrolment_id: 'enr-1',
    approved_count: 1,
    free_used: 1,
    free_remaining: 1,
    free_limit: 2,
  },
  usageStudentId: 'stu-1',
  isLoading: false,
  isLoadingSlots: false,
  error: null,
  isMutating: false,
  onUsageStudentChange: jest.fn(),
  onCheckInTeacherChange: jest.fn(),
  onCheckInDateChange: jest.fn(),
  onCheckIn: jest.fn(),
  onConfirm: jest.fn(),
  onCreateLeave: jest.fn(),
  onApproveLeave: jest.fn(),
  onRejectLeave: jest.fn(),
};

describe('AttendanceLeaveView', () => {
  it('renders pending check-in and leave actions', () => {
    const onConfirm = jest.fn();
    const onApproveLeave = jest.fn();

    render(
      <AttendanceLeaveView
        {...baseProps}
        onConfirm={onConfirm}
        onApproveLeave={onApproveLeave}
      />,
    );

    expect(screen.getByText(/Free leaves used:/)).toBeInTheDocument();
    expect(screen.getByText('1/2')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Present' }));
    expect(onConfirm).toHaveBeenCalledWith('att-1', 'present');
    fireEvent.click(screen.getByRole('button', { name: 'Approve' }));
    expect(onApproveLeave).toHaveBeenCalledWith('lv-1');
  });

  it('checks in from timetable schedule picker without UUID text', () => {
    const onCheckIn = jest.fn();
    render(<AttendanceLeaveView {...baseProps} onCheckIn={onCheckIn} />);

    expect(screen.queryByPlaceholderText(/Schedule UUID/i)).toBeNull();

    fireEvent.change(screen.getByLabelText(/^Schedule$/), {
      target: { value: 'sch-pick-1' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create check-in' }));

    expect(onCheckIn).toHaveBeenCalledWith('sch-pick-1');
  });

  it('notifies when teacher or lesson date changes', () => {
    const onCheckInTeacherChange = jest.fn();
    const onCheckInDateChange = jest.fn();
    render(
      <AttendanceLeaveView
        {...baseProps}
        checkInTeacherId=""
        scheduleSlots={[]}
        onCheckInTeacherChange={onCheckInTeacherChange}
        onCheckInDateChange={onCheckInDateChange}
      />,
    );

    fireEvent.change(screen.getByLabelText(/^Teacher$/), {
      target: { value: 'tch-1' },
    });
    expect(onCheckInTeacherChange).toHaveBeenCalledWith('tch-1');

    fireEvent.change(screen.getByLabelText(/^Lesson date$/), {
      target: { value: '2026-07-22' },
    });
    expect(onCheckInDateChange).toHaveBeenCalledWith('2026-07-22');
  });
});
