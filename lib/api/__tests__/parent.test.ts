/**
 * @jest-environment node
 */
import { listLinkedStudents, requestMagicLink, createParentStudentLink } from '../parent';

describe('parent api client', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('test_requestMagicLink_postsTenantAndEmail', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 202,
      headers: { get: () => 'application/json' },
      json: async () => ({
        detail: 'If a parent account exists, a magic link has been sent',
        magic_url: null,
      }),
    }) as unknown as typeof fetch;

    const result = await requestMagicLink({
      tenantSlug: 'demo',
      email: 'parent@example.com',
    });
    expect(result.magic_url).toBeNull();
    const [url, init] = (global.fetch as jest.Mock).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect(url).toContain('/api/v1/parent/magic-link/request');
    expect(init.method).toBe('POST');
    expect(JSON.parse(String(init.body))).toEqual({
      tenant_slug: 'demo',
      email: 'parent@example.com',
    });
  });

  it('test_listLinkedStudents_hitsStudentsEndpoint', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => [
        {
          id: 'stu-1',
          full_name: 'Charlotte',
          email: null,
          is_active: true,
        },
      ],
    }) as unknown as typeof fetch;

    const rows = await listLinkedStudents();
    expect(rows).toHaveLength(1);
    const calledUrl = String((global.fetch as jest.Mock).mock.calls[0]?.[0]);
    expect(calledUrl).toContain('/api/v1/parent/students');
  });

  it('test_createParentStudentLink_postsIds', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 'link-1',
        tenant_id: 'ten-1',
        parent_user_id: 'u-parent',
        student_id: 'stu-1',
      }),
    }) as unknown as typeof fetch;

    await createParentStudentLink({
      parent_user_id: 'u-parent',
      student_id: 'stu-1',
    });

    const [url, init] = (global.fetch as jest.Mock).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect(url).toBe('http://localhost:8000/api/v1/parent/student-links');
    expect(init.method).toBe('POST');
    expect(JSON.parse(String(init.body))).toEqual({
      parent_user_id: 'u-parent',
      student_id: 'stu-1',
    });
  });
});
