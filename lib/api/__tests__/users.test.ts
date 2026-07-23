/**
 * @jest-environment node
 */
import { listUsers } from '../users';

describe('users api client', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('test_listUsers_buildsPaginationQuery', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        items: [],
        page: 2,
        page_size: 10,
        total: 0,
      }),
    }) as unknown as typeof fetch;

    await listUsers({ page: 2, pageSize: 10 });
    const calledUrl = String((global.fetch as jest.Mock).mock.calls[0]?.[0]);
    expect(calledUrl).toContain('/api/v1/users');
    expect(calledUrl).toContain('page=2');
    expect(calledUrl).toContain('page_size=10');
  });
});
