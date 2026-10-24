/**
 * Tests for the typed frontend API client (AIJOB-34).
 */

import {
  apiRequest,
  getApiBaseUrl,
  resetAccessTokenProviderForTests,
  setAccessTokenProvider,
} from '@/lib/api/client';

describe('getApiBaseUrl', () => {
  const original = process.env.NEXT_PUBLIC_API_URL;

  afterEach(() => {
    process.env.NEXT_PUBLIC_API_URL = original;
  });

  it('returns NEXT_PUBLIC_API_URL without trailing slash', () => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/';
    expect(getApiBaseUrl()).toBe('http://localhost:8000');
  });

  it('throws when NEXT_PUBLIC_API_URL is missing for backend paths', () => {
    delete process.env.NEXT_PUBLIC_API_URL;
    expect(() => getApiBaseUrl()).toThrow(/NEXT_PUBLIC_API_URL/);
  });
});

describe('apiRequest', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
    resetAccessTokenProviderForTests();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    resetAccessTokenProviderForTests();
  });

  it('prefixes backend paths with NEXT_PUBLIC_API_URL', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ status: 'ok' }),
    }) as unknown as typeof fetch;

    await apiRequest<{ status: string }>('/health');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/health',
      expect.objectContaining({
        headers: expect.any(Headers),
      }),
    );
  });

  it('keeps Next.js BFF /api routes same-origin', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ ok: true }),
    }) as unknown as typeof fetch;

    await apiRequest<{ ok: boolean }>('/api/ai/exams/analyze', { method: 'POST' });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/ai/exams/analyze',
      expect.any(Object),
    );
  });

  it('injects Authorization bearer header when token provider returns a token', async () => {
    setAccessTokenProvider(() => 'test-access-token');
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({}),
    }) as unknown as typeof fetch;

    await apiRequest('/health');

    const [, init] = (global.fetch as jest.Mock).mock.calls[0] as [
      string,
      RequestInit,
    ];
    const headers = init.headers as Headers;
    expect(headers.get('Authorization')).toBe('Bearer test-access-token');
  });

  it('throws ApiError when response is not ok', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 503,
      headers: { get: () => 'application/json' },
      json: async () => ({ detail: 'unavailable' }),
    }) as unknown as typeof fetch;

    await expect(apiRequest('/health')).rejects.toMatchObject({
      name: 'ApiError',
      status: 503,
      message: 'unavailable',
    });
  });

  it('formats FastAPI 422 validation error arrays into a readable message', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 422,
      headers: { get: () => 'application/json' },
      json: async () => ({
        detail: [
          {
            loc: ['body', 'email'],
            msg: 'value is not a valid email address',
            type: 'value_error',
          },
        ],
      }),
    }) as unknown as typeof fetch;

    await expect(apiRequest('/api/v1/auth/login')).rejects.toMatchObject({
      name: 'ApiError',
      status: 422,
      message: 'email: value is not a valid email address',
    });
  });
});
