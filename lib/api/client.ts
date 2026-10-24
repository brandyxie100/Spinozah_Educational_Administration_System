/**
 * Typed HTTP client for FastAPI and same-origin Next.js BFF routes.
 *
 * Page components must not call `fetch` directly — use this module (or hooks
 * built on top of it) so auth headers and base URL stay centralized.
 */

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

type AccessTokenProvider = () => string | null | Promise<string | null>;

let accessTokenProvider: AccessTokenProvider = () => null;

/**
 * Register how the client obtains a JWT access token (wired in AIJOB-35).
 */
export function setAccessTokenProvider(provider: AccessTokenProvider): void {
  accessTokenProvider = provider;
}

/** Reset token provider between Jest cases. */
export function resetAccessTokenProviderForTests(): void {
  accessTokenProvider = () => null;
}

/**
 * Return the configured FastAPI base URL (no trailing slash).
 *
 * @throws Error when `NEXT_PUBLIC_API_URL` is unset or empty.
 */
export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!raw) {
    throw new Error(
      'NEXT_PUBLIC_API_URL is not configured. Set it in .env.local (see .env.example).',
    );
  }
  return raw.replace(/\/$/, '');
}

/**
 * Resolve a request path to an absolute or same-origin URL.
 *
 * - Paths under `/api/` stay same-origin (Next.js route handlers / BFF).
 * - All other paths are prefixed with `NEXT_PUBLIC_API_URL` (FastAPI).
 */
export function resolveApiUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const normalized = path.startsWith('/') ? path : `/${path}`;
  if (normalized.startsWith('/api/')) {
    return normalized;
  }
  return `${getApiBaseUrl()}${normalized}`;
}

/** Render one FastAPI/Pydantic validation error entry, e.g. "email: value is not a valid email address". */
function formatValidationError(entry: unknown): string | null {
  if (!entry || typeof entry !== 'object') {
    return null;
  }
  const { loc, msg } = entry as { loc?: unknown; msg?: unknown };
  if (typeof msg !== 'string') {
    return null;
  }
  const field = Array.isArray(loc) ? loc.filter((part) => part !== 'body').pop() : null;
  return field != null ? `${field}: ${msg}` : msg;
}

function messageFromBody(body: unknown, status: number): string {
  if (body && typeof body === 'object') {
    const record = body as Record<string, unknown>;
    if (typeof record.detail === 'string') {
      return record.detail;
    }
    if (Array.isArray(record.detail)) {
      const messages = record.detail
        .map(formatValidationError)
        .filter((message): message is string => message != null);
      if (messages.length > 0) {
        return messages.join('; ');
      }
    }
    if (typeof record.error === 'string') {
      return record.error;
    }
  }
  return `Request failed with status ${status}`;
}

/**
 * Perform a typed JSON request with optional Bearer auth injection.
 */
export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  const token = await accessTokenProvider();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // FormData must set its own Content-Type (with boundary); skip JSON default.
  const isFormData =
    typeof FormData !== 'undefined' && init.body instanceof FormData;
  if (!isFormData && !headers.has('Content-Type') && init.body != null) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(resolveApiUrl(path), {
    ...init,
    headers,
  });

  let body: unknown = null;
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    body = await response.json();
  } else {
    const text = await response.text();
    body = text.length > 0 ? text : null;
  }

  if (!response.ok) {
    throw new ApiError(messageFromBody(body, response.status), response.status, body);
  }

  return body as T;
}

/**
 * Perform an authenticated request and return a Blob (e.g. PDF download).
 */
export async function apiRequestBlob(
  path: string,
  init: RequestInit = {},
): Promise<Blob> {
  const headers = new Headers(init.headers);
  const token = await accessTokenProvider();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(resolveApiUrl(path), {
    ...init,
    headers,
  });

  if (!response.ok) {
    let body: unknown = null;
    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('application/json')) {
      body = await response.json();
    } else {
      const text = await response.text();
      body = text.length > 0 ? text : null;
    }
    throw new ApiError(messageFromBody(body, response.status), response.status, body);
  }

  return response.blob();
}
