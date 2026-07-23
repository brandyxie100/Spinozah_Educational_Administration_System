/**
 * Presenter tests for TeacherListView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { TeacherListView } from '@/components/teachers/TeacherListView';
import type { Teacher } from '@/lib/api/teachers';

const sampleTeachers: Teacher[] = [
  {
    id: 't1',
    tenant_id: 'ten1',
    full_name: 'Ada Teacher',
    email: 'ada@example.com',
    user_id: null,
    is_active: true,
  },
];

describe('TeacherListView', () => {
  it('renders teachers and submits create form', () => {
    const onCreate = jest.fn();
    render(
      <TeacherListView
        teachers={sampleTeachers}
        total={1}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={onCreate}
        onUpdate={jest.fn()}
      />,
    );

    expect(screen.getByText('Ada Teacher')).toBeInTheDocument();
    expect(screen.getByText(/Teachers \(1\)/)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/^Full name$/), {
      target: { value: 'Bob Coach' },
    });
    fireEvent.change(screen.getByLabelText(/Email \(optional\)/), {
      target: { value: 'bob@example.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create' }));

    expect(onCreate).toHaveBeenCalledWith({
      full_name: 'Bob Coach',
      email: 'bob@example.com',
    });
  });

  it('enters edit mode and calls onUpdate', () => {
    const onUpdate = jest.fn();
    render(
      <TeacherListView
        teachers={sampleTeachers}
        total={1}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={jest.fn()}
        onUpdate={onUpdate}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
    fireEvent.change(screen.getByDisplayValue('Ada Teacher'), {
      target: { value: 'Ada Updated' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));

    expect(onUpdate).toHaveBeenCalledWith({
      teacherId: 't1',
      full_name: 'Ada Updated',
      email: 'ada@example.com',
      is_active: true,
    });
  });
});
