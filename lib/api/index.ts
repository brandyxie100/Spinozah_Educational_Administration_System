/**
 * Public exports for the frontend API client layer.
 */

export {
  ApiError,
  apiRequest,
  getApiBaseUrl,
  resetAccessTokenProviderForTests,
  resolveApiUrl,
  setAccessTokenProvider,
} from '@/lib/api/client';
