'use client';

import React, { useEffect, useState, useSyncExternalStore } from 'react';
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

// No external event ever changes these snapshots after mount (the app
// doesn't listen for `popstate`/`storage`), so subscribing is a no-op —
// `useSyncExternalStore` still gives us a hydration-safe re-check after
// the SSR-matching first paint, which a plain effect calling setState
// cannot do without a same-render mismatch.
function subscribeToNothing(): () => void {
  return () => {};
}

function getServerActiveModule(): string {
  return 'Dashboard';
}

function getClientActiveModule(): string {
  return new URLSearchParams(window.location.search).get('module') ?? 'Dashboard';
}

function getServerStaffUser(): StaffUser | null {
  return null;
}

// getStaffUser() parses JSON on every call; cache by token so repeated
// calls in the same commit return the same reference (useSyncExternalStore
// warns/loops if getSnapshot() isn't referentially stable across calls).
let cachedStaffToken: string | null = null;
let cachedStaffUser: StaffUser | null = null;

function getClientStaffUser(): StaffUser | null {
  const token = getStaffAccessToken();
  if (token !== cachedStaffToken) {
    cachedStaffToken = token;
    cachedStaffUser = token ? getStaffUser() : null;
  }
  return cachedStaffUser;
}

export default function SpinozahEducationDashboard() {
  const urlModule = useSyncExternalStore(
    subscribeToNothing,
    getClientActiveModule,
    getServerActiveModule,
  );
  const [moduleOverride, setModuleOverride] = useState<string | null>(null);
  const activeModule = moduleOverride ?? urlModule;
  const setActiveModule = setModuleOverride;

  const hydratedStaffUser = useSyncExternalStore(
    subscribeToNothing,
    getClientStaffUser,
    getServerStaffUser,
  );
  const [staffOverride, setStaffOverride] = useState<StaffUser | null | undefined>(
    undefined,
  );
  const staffUser = staffOverride === undefined ? hydratedStaffUser : staffOverride;
  const setStaffUser = setStaffOverride;

  const [showStaffLogin, setShowStaffLogin] = useState(false);
  const logoutMutation = useStaffLogout();
  const goToDashboard = () => setActiveModule('Dashboard');

  useEffect(() => {
    wireStaffAccessTokenProvider();
  }, []);

  const modules = [
    { title: 'Admin Dashboard', icon: '📊', desc: 'Student/teacher KPIs, revenue, unpaid alerts' },
    { title: 'User Management', icon: '👤', desc: 'Admin create/list/update/deactivate users' },
    { title: 'Teacher Management', icon: '🧑‍🏫', desc: 'Create and edit teacher profiles' },
    { title: 'Teacher Timetable', icon: '🗓️', desc: '老师查看实时排课与课程更新' },
    { title: 'Schedule Management', icon: '📅', desc: 'Create lesson schedules for teacher and student' },
    { title: 'Student Management', icon: '👩‍🎓', desc: '学生录入、编辑、课时管理' },
    { title: 'Enrolment Management', icon: '📦', desc: 'Create and adjust student lesson packages' },
    { title: 'Attendance & Leave', icon: '✅', desc: '系统到课后自动提醒老师确认消课，请假2次限制' },
    { title: 'Question Analysis', icon: '📝', desc: '上传试卷分析错题和薄弱知识点' },
    { title: 'Parent Portal', icon: '📖', desc: 'Magic Link邮箱登录，查看课时与报告' },
    { title: 'Parent Student Links', icon: '🔗', desc: 'Staff link parent users to students for portal access' },
    { title: 'Finance & Invoice', icon: '💳', desc: '自动生成账单、续费提醒' },
    { title: 'AI Reports', icon: '📄', desc: 'AI分析作文、错题与评估报告' },
    { title: 'Lesson Planning', icon: '🗂️', desc: '根据学生情况生成教学计划' },
    { title: 'University Pathway', icon: '🎓', desc: '根据成绩推荐大学和专业' },
  ];
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
