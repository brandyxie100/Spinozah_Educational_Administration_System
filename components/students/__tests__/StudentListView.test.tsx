/**
 * Presenter tests for StudentListView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { StudentListView } from '@/components/students/StudentListView';
import type { Student } from '@/lib/api/students';

const sampleStudents: Student[] = [
  {
    id: 's1',
    tenant_id: 't1',
    full_name: 'Charlotte',
    email: 'charlotte@example.com',
    is_active: true,
  },
];

describe('StudentListView', () => {
  it('should render students and call onCreate when the form is submitted', () => {
    const onCreate = jest.fn();
    const onUpdate = jest.fn();

    render(
      <StudentListView
        students={sampleStudents}
        total={1}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={onCreate}
        onUpdate={onUpdate}
      />,
    );

    expect(screen.getByText('Charlotte')).toBeInTheDocument();
    expect(screen.getByText(/Students \(1\)/)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/Full name/i), {
      target: { value: 'Zoe' },
    });
    fireEvent.change(screen.getByLabelText(/Email \(optional\)/i), {
      target: { value: 'zoe@example.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create' }));

    expect(onCreate).toHaveBeenCalledWith({
      full_name: 'Zoe',
      email: 'zoe@example.com',
    });
  });

  it('should show empty state when there are no students', () => {
    render(
      <StudentListView
        students={[]}
        total={0}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={jest.fn()}
        onUpdate={jest.fn()}
      />,
    );

    expect(screen.getByText(/No students yet/i)).toBeInTheDocument();
  });

  it('should enter edit mode and call onUpdate on save', () => {
    const onUpdate = jest.fn();

    render(
      <StudentListView
        students={sampleStudents}
        total={1}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={jest.fn()}
        onUpdate={onUpdate}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
    fireEvent.change(screen.getByDisplayValue('Charlotte'), {
      target: { value: 'Charlotte Updated' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));

    expect(onUpdate).toHaveBeenCalledWith({
      studentId: 's1',
      full_name: 'Charlotte Updated',
      email: 'charlotte@example.com',
      is_active: true,
    });
  });
});
