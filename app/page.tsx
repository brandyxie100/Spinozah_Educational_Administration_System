'use client';

import React, { useState } from 'react';
import { AdminDashboardContainer } from '@/components/admin/AdminDashboardContainer';
import { BackButton } from '@/components/dashboard/BackButton';
import { EssayAnalysisPanel } from '@/components/essay-analysis/EssayAnalysisPanel';
import { LessonPlanPanel } from '@/components/lesson-planning/LessonPlanPanel';
import { QuestionAnalysisPanel } from '@/components/question-analysis/QuestionAnalysisPanel';
import { StudentListContainer } from '@/components/students/StudentListContainer';
import { TeacherTimetableContainer } from '@/components/timetable/TeacherTimetableContainer';

export default function SpinozahEducationDashboard() {
  const [activeModule, setActiveModule] = useState('Dashboard');
  const goToDashboard = () => setActiveModule('Dashboard');

  const modules = [
    { title: 'Admin Dashboard', icon: '📊', desc: 'Student/teacher KPIs, revenue, unpaid alerts' },
    { title: 'Teacher Timetable', icon: '🗓️', desc: '老师查看实时排课与课程更新' },
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
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
        <AdminDashboardContainer />
      </div>
    );
  }

  if (activeModule === 'Teacher Timetable') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Teacher Timetable</h1>
        <TeacherTimetableContainer />
      </div>
    );
  }

  if (activeModule === 'Student Management') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Student Management</h1>
        <StudentListContainer />
      </div>
    );
  }

  if (activeModule === 'Attendance & Leave') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Attendance & Leave</h1>
        <div className="bg-white p-6 rounded-xl shadow">
          <p>Charlotte: Present</p>
          <p>Chace: Leave used 1/2</p>
          <p>Olivia: Present</p>
        </div>
      </div>
    );
  }

  if (activeModule === 'Question Analysis') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Question Analysis</h1>
        <QuestionAnalysisPanel />
      </div>
    );
  }

  if (activeModule === 'Parent Portal') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Parent Portal</h1>
        <div className="bg-white p-6 rounded-xl shadow">
          <p>Charlotte: 8 lessons completed, 2 remaining</p>
        </div>
      </div>
    );
  }

  if (activeModule === 'Finance & Invoice') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Finance & Invoice</h1>
        <div className="bg-white p-6 rounded-xl shadow">
          <p>Next invoice auto-generated for Term 3.</p>
        </div>
      </div>
    );
  }

  if (activeModule === 'AI Reports') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">AI Reports</h1>
        <EssayAnalysisPanel />
      </div>
    );
  }

  if (activeModule === 'Lesson Planning') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">Lesson Planning</h1>
        <LessonPlanPanel />
      </div>
    );
  }

  if (activeModule === 'University Pathway') {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <BackButton onBack={goToDashboard} />
        <h1 className="text-3xl font-bold mb-6">University Pathway</h1>
        <div className="bg-white p-6 rounded-xl shadow">
          <p>Recommend majors and universities after IGCSE/A-Level results.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-3">Spinozah AI Education</h1>
        <p className="mb-8">Current Page: {activeModule}</p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-md p-6">
              <div className="text-3xl">{module.icon}</div>
              <h2 className="text-xl font-bold mt-3">{module.title}</h2>
              <p className="text-gray-600 mt-2">{module.desc}</p>
              <button
                onClick={() => setActiveModule(module.title)}
                className="mt-4 w-full bg-black text-white rounded-lg px-4 py-2"
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
