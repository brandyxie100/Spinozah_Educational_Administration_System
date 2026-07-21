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

export {
  createStudent,
  listStudents,
  updateStudent,
  type Student,
  type StudentCreateInput,
  type StudentListResponse,
  type StudentUpdateInput,
} from '@/lib/api/students';
