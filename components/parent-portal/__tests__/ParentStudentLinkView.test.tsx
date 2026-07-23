/**
 * Presenter tests for ParentStudentLinkView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { ParentStudentLinkView } from '@/components/parent-portal/ParentStudentLinkView';
import type { ParentStudentLink } from '@/lib/api/parent';
import type { Student } from '@/lib/api/students';
import type { User } from '@/lib/api/users';

const parents: User[] = [
  {
    id: 'u-parent',
    tenant_id: 't1',
    email: 'parent@example.com',
    full_name: 'Pat Parent',
    role: 'parent',
    is_active: true,
  },
];

const students: Student[] = [
  {
    id: 'stu-1',
    tenant_id: 't1',
    full_name: 'Sam Student',
    email: null,
    is_active: true,
  },
];

const created: ParentStudentLink[] = [
  {
    id: 'link-1',
    tenant_id: 't1',
    parent_user_id: 'u-parent',
    student_id: 'stu-1',
  },
];

describe('ParentStudentLinkView', () => {
  it('submits parent and student selection', () => {
    const onCreate = jest.fn();
    render(
      <ParentStudentLinkView
        parents={parents}
        students={students}
        createdLinks={[]}
        isLoadingOptions={false}
        isSaving={false}
        error={null}
        onCreate={onCreate}
      />,
    );

    fireEvent.change(screen.getByLabelText(/^Parent user$/), {
      target: { value: 'u-parent' },
    });
    fireEvent.change(screen.getByLabelText(/^Student$/), {
      target: { value: 'stu-1' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create link' }));

    expect(onCreate).toHaveBeenCalledWith({
      parentUserId: 'u-parent',
      studentId: 'stu-1',
    });
  });

  it('shows API error and created links', () => {
    render(
      <ParentStudentLinkView
        parents={parents}
        students={students}
        createdLinks={created}
        isLoadingOptions={false}
        isSaving={false}
        error="Selected user is not a parent."
        onCreate={jest.fn()}
      />,
    );

    expect(screen.getByRole('alert')).toHaveTextContent(/not a parent/i);
    expect(screen.getByText('link-1')).toBeInTheDocument();
    expect(screen.getByText('Created this session')).toBeInTheDocument();
  });
});
