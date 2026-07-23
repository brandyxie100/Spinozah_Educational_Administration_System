/**
 * Presenter tests for UserListView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { UserListView } from '@/components/users/UserListView';
import type { User } from '@/lib/api/users';

const sampleUsers: User[] = [
  {
    id: 'u1',
    tenant_id: 't1',
    email: 'admin@example.com',
    full_name: 'Ada Admin',
    role: 'admin',
    is_active: true,
  },
];

describe('UserListView', () => {
  it('renders users and submits create form', () => {
    const onCreate = jest.fn();
    render(
      <UserListView
        users={sampleUsers}
        total={1}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={onCreate}
        onUpdate={jest.fn()}
        onDeactivate={jest.fn()}
      />,
    );

    expect(screen.getByText('Ada Admin')).toBeInTheDocument();
    expect(screen.getByText(/Users \(1\)/)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/^Full name$/), {
      target: { value: 'Bob Frontdesk' },
    });
    fireEvent.change(screen.getByLabelText(/^Email$/), {
      target: { value: 'bob@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password \(min 8\)/), {
      target: { value: 'password1' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create user' }));

    expect(onCreate).toHaveBeenCalledWith({
      email: 'bob@example.com',
      full_name: 'Bob Frontdesk',
      password: 'password1',
      role: 'frontdesk',
    });
  });

  it('calls onDeactivate for an active user', () => {
    const onDeactivate = jest.fn();
    render(
      <UserListView
        users={sampleUsers}
        total={1}
        isLoading={false}
        error={null}
        isSaving={false}
        onCreate={jest.fn()}
        onUpdate={jest.fn()}
        onDeactivate={onDeactivate}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Deactivate' }));
    expect(onDeactivate).toHaveBeenCalledWith('u1');
  });
});
