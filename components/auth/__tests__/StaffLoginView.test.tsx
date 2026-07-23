/**
 * Presenter tests for StaffLoginView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { StaffLoginView } from '@/components/auth/StaffLoginView';

describe('StaffLoginView', () => {
  it('submits tenant, email, and password', () => {
    const onLogin = jest.fn();
    render(
      <StaffLoginView isMutating={false} error={null} onLogin={onLogin} />,
    );

    fireEvent.change(screen.getByLabelText(/Email/), {
      target: { value: 'admin@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password/), {
      target: { value: 'secret' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(onLogin).toHaveBeenCalledWith({
      tenantSlug: 'demo',
      email: 'admin@example.com',
      password: 'secret',
    });
  });
});
