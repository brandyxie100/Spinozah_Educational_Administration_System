/**
 * Tests for analyses API helpers.
 */

import { createAnalysis, getAnalysis, listAnalyses } from '@/lib/api/analyses';

describe('analyses API helpers', () => {
  const originalFetch = global.fetch;
  const originalUrl = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    global.fetch = originalFetch;
    process.env.NEXT_PUBLIC_API_URL = originalUrl;
  });

  it('creates, lists, and gets analyses', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 'a1',
        tenant_id: 't1',
        kind: 'essay',
        student_id: null,
        student_name: 'Ada',
        title: 'Trip',
        payload: { studentName: 'Ada', title: 'Trip' },
      }),
    }) as unknown as typeof fetch;

    await createAnalysis({
      kind: 'essay',
      payload: { studentName: 'Ada', title: 'Trip' },
    });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/analyses',
      expect.objectContaining({ method: 'POST' }),
    );

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => [],
    }) as unknown as typeof fetch;

    await listAnalyses({ kind: 'exam' });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/analyses?kind=exam',
      expect.any(Object),
    );

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        id: 'a1',
        tenant_id: 't1',
        kind: 'essay',
        student_id: null,
        student_name: 'Ada',
        title: 'Trip',
        payload: {},
      }),
    }) as unknown as typeof fetch;

    await getAnalysis('a1');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/analyses/a1',
      expect.any(Object),
    );
  });
});
