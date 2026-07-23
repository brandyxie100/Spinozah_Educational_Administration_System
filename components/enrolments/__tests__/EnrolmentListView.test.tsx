/**
 * Presenter tests for EnrolmentListView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { EnrolmentListView } from '@/components/enrolments/EnrolmentListView';
import type { Enrolment } from '@/lib/api/enrolments';
import type { Student } from '@/lib/api/students';

const students: Student[] = [
  {
    id: 'stu-1',
    tenant_id: 't1',
    full_name: 'Sam Student',
    email: null,
    is_active: true,
  },
];

const enrolments: Enrolment[] = [
  {
    id: 'enr-1',
    tenant_id: 't1',
    student_id: 'stu-1',
    total_lessons: 20,
    completed_lessons: 5,
    remaining_lessons: 15,
    extension_days: 0,
    status: 'active',
  },
];

describe('EnrolmentListView', () => {
  it('creates a package and updates remaining lessons', () => {
    const onCreate = jest.fn();
    const onUpdateRemaining = jest.fn();
    render(
      <EnrolmentListView
        students={students}
        enrolments={enrolments}
        selectedStudentId="stu-1"
        isLoading={false}
        error={null}
        isSaving={false}
        onSelectStudent={jest.fn()}
        onCreate={onCreate}
        onUpdateRemaining={onUpdateRemaining}
      />,
    );

    fireEvent.change(screen.getByLabelText(/^Total lessons$/), {
      target: { value: '12' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create package' }));
    expect(onCreate).toHaveBeenCalledWith({
      studentId: 'stu-1',
      totalLessons: 12,
    });

    fireEvent.change(
      screen.getByLabelText(/Remaining lessons for enr-1/),
      { target: { value: '10' } },
    );
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));
    expect(onUpdateRemaining).toHaveBeenCalledWith({
      enrolmentId: 'enr-1',
      remainingLessons: 10,
    });
  });
});
