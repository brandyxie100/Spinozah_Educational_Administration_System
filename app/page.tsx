'use client';

import React, { useState } from 'react';
import { AdminDashboardContainer } from '@/components/admin/AdminDashboardContainer';
import { StaffAuthBar } from '@/components/auth/StaffAuthBar';
import { StaffLoginContainer } from '@/components/auth/StaffLoginContainer';
import { StaffModuleShell } from '@/components/auth/StaffModuleShell';
import { BackButton } from '@/components/dashboard/BackButton';
import { EssayAnalysisPanel } from '@/components/essay-analysis/EssayAnalysisPanel';
import { AttendanceLeaveContainer } from '@/components/attendance/AttendanceLeaveContainer';
import { InvoiceListContainer } from '@/components/finance/InvoiceListContainer';
import { LessonPlanPanel } from '@/components/lesson-planning/LessonPlanPanel';
import { ParentPortalContainer } from '@/components/parent-portal/ParentPortalContainer';
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

  const modules = [
    { title: 'Admin Dashboard', icon: '📊', desc: 'Student/teacher KPIs, revenue, unpaid alerts' },
    { title: 'User Management', icon: '👤', desc: 'Admin create/list/update/deactivate users' },
    { title: 'Teacher Management', icon: '🧑‍🏫', desc: 'Create and edit teacher profiles' },
    { title: 'Teacher Timetable', icon: '🗓️', desc: '老师查看实时排课与课程更新' },
    { title: 'Schedule Management', icon: '📅', desc: 'Create lesson schedules for teacher and student' },
    { title: 'Student Management', icon: '👩‍🎓', desc: '学生录入、编辑、课时管理' },
    { title: 'Attendance & Leave', icon: '✅', desc: '系统到课后自动提醒老师确认消课，请假2次限制' },
    { title: 'Question Analysis', icon: '📝', desc: '上传试卷分析错题和薄弱知识点' },
    { title: 'Parent Portal', icon: '📖', desc: 'Magic Link邮箱登录，查看课时与报告' },
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

  if (activeModule === 'Attendance & Leave') {
    return (
      <StaffModuleShell title="Attendance & Leave" onBack={goToDashboard}>
        <AttendanceLeaveContainer />
      </StaffModuleShell>
    );
  }

  if (activeModule === 'Question Analysis') {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <BackButton onBack={goToDashboard} />
        <h1 className="mb-6 text-3xl font-bold">Question Analysis</h1>
        <QuestionAnalysisPanel />
      </div>
    );
  }

  if (activeModule === 'Parent Portal') {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <BackButton onBack={goToDashboard} />
        <h1 className="mb-6 text-3xl font-bold">Parent Portal</h1>
        <ParentPortalContainer />
      </div>
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
      <div className="min-h-screen bg-slate-50 p-8">
        <BackButton onBack={goToDashboard} />
        <h1 className="mb-6 text-3xl font-bold">AI Reports</h1>
        <EssayAnalysisPanel />
      </div>
    );
  }

  if (activeModule === 'Lesson Planning') {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <BackButton onBack={goToDashboard} />
        <h1 className="mb-6 text-3xl font-bold">Lesson Planning</h1>
        <LessonPlanPanel />
      </div>
    );
  }

  if (activeModule === 'University Pathway') {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <BackButton onBack={goToDashboard} />
        <h1 className="mb-6 text-3xl font-bold">University Pathway</h1>
        <UniversityPathwayPanel />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-7xl">
        <StaffAuthBar
          user={staffUser}
          isMutating={logoutMutation.isPending}
          onSignInClick={() => setShowStaffLogin(true)}
          onSignOut={() => {
            logoutMutation.mutate(undefined, {
              onSettled: () => {
                setStaffUser(null);
                setShowStaffLogin(false);
              },
            });
          }}
        />
        <h1 className="mb-3 text-4xl font-bold">Spinozah AI Education</h1>
        <p className="mb-8">Current Page: {activeModule}</p>

        {showStaffLogin && !staffUser && (
          <div className="mb-8">
            <StaffLoginContainer
              onSignedIn={() => {
                setStaffUser(getStaffUser());
                setShowStaffLogin(false);
              }}
            />
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {modules.map((module) => (
            <div key={module.title} className="rounded-2xl bg-white p-6 shadow-md">
              <div className="text-3xl">{module.icon}</div>
              <h2 className="mt-3 text-xl font-bold">{module.title}</h2>
              <p className="mt-2 text-gray-600">{module.desc}</p>
              <button
                type="button"
                onClick={() => setActiveModule(module.title)}
                className="mt-4 w-full rounded-lg bg-black px-4 py-2 text-white"
              >
                Open
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
