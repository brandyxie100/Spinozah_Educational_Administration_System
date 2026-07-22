/**
 * Presenter tests for AttendanceLeaveView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { AttendanceLeaveView } from '@/components/attendance/AttendanceLeaveView';
import type { AttendanceRecord, LeaveRequest } from '@/lib/api/attendance';
import type { Student } from '@/lib/api/students';

const students: Student[] = [
  {
    id: 'stu-1',
    tenant_id: 't1',
    full_name: 'Charlotte',
    email: null,
    is_active: true,
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

describe('AttendanceLeaveView', () => {
  it('renders pending check-in and leave actions', () => {
    const onConfirm = jest.fn();
    const onApproveLeave = jest.fn();

    render(
      <AttendanceLeaveView
        attendance={attendance}
        leaveRequests={leaveRequests}
        students={students}
        leaveUsage={{
          student_id: 'stu-1',
          enrolment_id: 'enr-1',
          approved_count: 1,
          free_used: 1,
          free_remaining: 1,
          free_limit: 2,
        }}
        usageStudentId="stu-1"
        isLoading={false}
        error={null}
        isMutating={false}
        onUsageStudentChange={jest.fn()}
        onCheckIn={jest.fn()}
        onConfirm={onConfirm}
        onCreateLeave={jest.fn()}
        onApproveLeave={onApproveLeave}
        onRejectLeave={jest.fn()}
      />,
    );

    expect(screen.getByText(/Free leaves used:/)).toBeInTheDocument();
    expect(screen.getByText('1/2')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Present' }));
    expect(onConfirm).toHaveBeenCalledWith('att-1', 'present');
    fireEvent.click(screen.getByRole('button', { name: 'Approve' }));
    expect(onApproveLeave).toHaveBeenCalledWith('lv-1');
  });
});
