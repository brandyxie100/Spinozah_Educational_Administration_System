/**
 * @jest-environment node
 */
import { loginStaff } from '../auth';

describe('auth api client', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('test_loginStaff_postsCredentialsAndReturnsToken', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        access_token: 'access.jwt',
        token_type: 'bearer',
        user: {
          id: 'u1',
          tenant_id: 't1',
          email: 'admin@example.com',
          full_name: 'Admin',
          role: 'admin',
        },
      }),
    }) as unknown as typeof fetch;

    const result = await loginStaff({
      tenantSlug: 'demo',
      email: 'admin@example.com',
      password: 'secret',
    });
    expect(result.access_token).toBe('access.jwt');
    const [url, init] = (global.fetch as jest.Mock).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect(url).toContain('/api/v1/auth/login');
    expect(init.method).toBe('POST');
    expect(JSON.parse(String(init.body))).toEqual({
      tenant_slug: 'demo',
      email: 'admin@example.com',
      password: 'secret',
    });
  });
});
