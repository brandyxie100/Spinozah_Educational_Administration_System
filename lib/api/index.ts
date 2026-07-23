/**
 * Public exports for the frontend API client layer.
 */

export {
  ApiError,
  apiRequest,
  apiRequestBlob,
  getApiBaseUrl,
  resetAccessTokenProviderForTests,
  resolveApiUrl,
  setAccessTokenProvider,
} from '@/lib/api/client';

export {
  loginStaff,
  logoutStaff,
  type StaffLoginInput,
  type StaffTokenResponse,
} from '@/lib/api/auth';

export {
  createUser,
  deactivateUser,
  listUsers,
  updateUser,
  type User,
  type UserCreateInput,
  type UserListResponse,
  type UserRole,
  type UserUpdateInput,
} from '@/lib/api/users';

export {
  createStudent,
  listStudents,
  updateStudent,
  type Student,
  type StudentCreateInput,
  type StudentListResponse,
  type StudentUpdateInput,
} from '@/lib/api/students';

export {
  getAdminKpis,
  type AdminKpis,
  type RevenuePeriod,
  type TodaySchedule,
} from '@/lib/api/admin';

export {
  createTeacher,
  getTeacherSchedule,
  listTeachers,
  updateTeacher,
  type Teacher,
  type TeacherCreateInput,
  type TeacherListResponse,
  type TeacherScheduleResponse,
  type TeacherScheduleSlot,
  type TeacherUpdateInput,
  type TimetableDisplayStatus,
} from '@/lib/api/teachers';

export {
  approveLeaveRequest,
  checkInAttendance,
  confirmAttendance,
  createLeaveRequest,
  getLeaveUsage,
  listAttendance,
  listLeaveRequests,
  rejectLeaveRequest,
  type AttendanceCheckInInput,
  type AttendanceRecord,
  type LeaveRequest,
  type LeaveRequestCreateInput,
  type LeaveUsage,
} from '@/lib/api/attendance';

export {
  createInvoice,
  downloadInvoicePdf,
  listInvoices,
  updateInvoicePaymentStatus,
  type Invoice,
  type InvoiceCreateInput,
  type InvoiceLineItem,
  type PaymentStatus,
} from '@/lib/api/invoices';

export {
  consumeMagicLink,
  downloadStudentInvoicePdf,
  getStudentDashboardReport,
  getStudentEnrolment,
  listLinkedStudents,
  listStudentAttendance,
  listStudentInvoices,
  requestMagicLink,
  type LinkedStudent,
  type MagicLinkRequestResponse,
  type ParentAttendance,
  type ParentDashboardReport,
  type ParentEnrolment,
  type ParentInvoice,
  type ParentTokenResponse,
  type ParentUser,
} from '@/lib/api/parent';
