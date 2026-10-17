'use client';

import React, { useState } from 'react';
import { AdminDashboardContainer } from '@/components/admin/AdminDashboardContainer';
import { StaffModuleShell } from '@/components/auth/StaffModuleShell';
import { WorkflowHome } from '@/components/dashboard/WorkflowHome';
import { EssayAnalysisPanel } from '@/components/essay-analysis/EssayAnalysisPanel';
import { AttendanceLeaveContainer } from '@/components/attendance/AttendanceLeaveContainer';
import { EnrolmentListContainer } from '@/components/enrolments/EnrolmentListContainer';
import { InvoiceListContainer } from '@/components/finance/InvoiceListContainer';
import { LessonPlanPanel } from '@/components/lesson-planning/LessonPlanPanel';
import { ParentPortalContainer } from '@/components/parent-portal/ParentPortalContainer';
import { ParentStudentLinkContainer } from '@/components/parent-portal/ParentStudentLinkContainer';
import { QuestionAnalysisPanel } from '@/components/question-analysis/QuestionAnalysisPanel';
import { ScheduleCreateContainer } from '@/components/schedules/ScheduleCreateContainer';
import { UniversityPathwayPanel } from '@/components/university-pathway/UniversityPathwayPanel';
import { StudentListContainer } from '@/components/students/StudentListContainer';
import { TeacherListContainer } from '@/components/teachers/TeacherListContainer';
import { TeacherTimetableContainer } from '@/components/timetable/TeacherTimetableContainer';
import { UserListContainer } from '@/components/users/UserListContainer';
import { useStaffLogout } from '@/hooks/useStaffAuth';
import {
  getStaffAccessToken,
  getStaffUser,
  wireStaffAccessTokenProvider,
  type StaffUser,
} from '@/lib/staff-session';

function initialModuleFromUrl(): string {
  if (typeof window === 'undefined') {
    return 'Dashboard';
  }
  return (
    new URLSearchParams(window.location.search).get('module') ?? 'Dashboard'
  );
}

function readStaffUser(): StaffUser | null {
  wireStaffAccessTokenProvider();
  return getStaffAccessToken() ? getStaffUser() : null;
}

export default function SpinozahEducationDashboard() {
  const [activeModule, setActiveModule] = useState(initialModuleFromUrl);
  const [staffUser, setStaffUser] = useState<StaffUser | null>(readStaffUser);
  const [showStaffLogin, setShowStaffLogin] = useState(false);
  const logoutMutation = useStaffLogout();
  const goToDashboard = () => setActiveModule('Dashboard');

  if (activeModule === 'Admin Dashboard') {
    return (
      <StaffModuleShell title="Admin Dashboard" onBack={goToDashboard}>
        <AdminDashboardContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'User Management') {
    return (
      <StaffModuleShell title="User Management" onBack={goToDashboard}>
        <UserListContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Teacher Management') {
    return (
      <StaffModuleShell title="Teacher Management" onBack={goToDashboard}>
        <TeacherListContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Teacher Timetable') {
    return (
      <StaffModuleShell title="Teacher Timetable" onBack={goToDashboard}>
        <TeacherTimetableContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Schedule Management') {
    return (
      <StaffModuleShell title="Schedule Management" onBack={goToDashboard}>
        <ScheduleCreateContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Student Management') {
    return (
      <StaffModuleShell title="Student Management" onBack={goToDashboard}>
        <StudentListContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Enrolment Management') {
    return (
      <StaffModuleShell title="Enrolment Management" onBack={goToDashboard}>
        <EnrolmentListContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Attendance & Leave') {
    return (
      <StaffModuleShell title="Attendance & Leave" onBack={goToDashboard}>
        <AttendanceLeaveContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Question Analysis') {
    return (
      <StaffModuleShell title="Question Analysis" onBack={goToDashboard} requireAuth={false}>
        <QuestionAnalysisPanel />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Parent Portal') {
    return (
      <StaffModuleShell title="Parent Portal" onBack={goToDashboard} requireAuth={false}>
        <ParentPortalContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Parent Student Links') {
    return (
      <StaffModuleShell title="Parent Student Links" onBack={goToDashboard}>
        <ParentStudentLinkContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Finance & Invoice') {
    return (
      <StaffModuleShell title="Finance & Invoice" onBack={goToDashboard}>
        <InvoiceListContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'AI Reports') {
    return (
      <StaffModuleShell title="AI Reports" onBack={goToDashboard} requireAuth={false}>
        <EssayAnalysisPanel />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Lesson Planning') {
    return (
      <StaffModuleShell title="Lesson Planning" onBack={goToDashboard} requireAuth={false}>
        <LessonPlanPanel />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'University Pathway') {
    return (
      <StaffModuleShell title="University Pathway" onBack={goToDashboard} requireAuth={false}>
        <UniversityPathwayPanel />
      </StaffModuleShell>
    );
  }

  return (
    <WorkflowHome
      staffUser={staffUser}
      isMutating={logoutMutation.isPending}
      showStaffLogin={showStaffLogin}
      onSignInClick={() => setShowStaffLogin(true)}
      onSignOut={() => {
        logoutMutation.mutate(undefined, {
          onSettled: () => {
            setStaffUser(null);
            setShowStaffLogin(false);
          },
        });
      }}
      onSignedIn={() => {
        setStaffUser(getStaffUser());
        setShowStaffLogin(false);
      }}
      onOpenModule={setActiveModule}
    />
  );
}
