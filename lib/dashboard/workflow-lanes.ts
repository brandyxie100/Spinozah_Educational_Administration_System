/**
 * Soft River home: modules grouped by staff workflow (not a flat card grid).
 */

export type WorkflowModule = {
  title: string;
  label: string;
  desc: string;
};

export type WorkflowLane = {
  id: string;
  title: string;
  blurb: string;
  modules: WorkflowModule[];
};

/** All dashboard modules in workflow order. Titles must match page.tsx routing. */
export const WORKFLOW_LANES: WorkflowLane[] = [
  {
    id: 'overview',
    title: 'Overview',
    blurb: 'Centre health at a glance',
    modules: [
      {
        title: 'Admin Dashboard',
        label: 'Admin Dashboard',
        desc: 'KPIs, revenue, unpaid alerts',
      },
    ],
  },
  {
    id: 'people',
    title: 'People',
    blurb: 'Who works and learns here',
    modules: [
      {
        title: 'User Management',
        label: 'Users',
        desc: 'Staff logins and roles',
      },
      {
        title: 'Teacher Management',
        label: 'Teachers',
        desc: 'Teacher profiles',
      },
      {
        title: 'Student Management',
        label: 'Students',
        desc: 'Student records',
      },
      {
        title: 'Parent Student Links',
        label: 'Parent links',
        desc: 'Link parents to children',
      },
    ],
  },
  {
    id: 'schedule',
    title: 'Schedule',
    blurb: 'Book and see lessons',
    modules: [
      {
        title: 'Schedule Management',
        label: 'Book lessons',
        desc: 'Create lesson schedules',
      },
      {
        title: 'Teacher Timetable',
        label: 'Timetable',
        desc: 'Live teacher calendar',
      },
      {
        title: 'Enrolment Management',
        label: 'Enrolments',
        desc: 'Lesson packages',
      },
    ],
  },
  {
    id: 'attendance',
    title: 'Attendance',
    blurb: 'Confirm classes and leave',
    modules: [
      {
        title: 'Attendance & Leave',
        label: 'Attendance & Leave',
        desc: 'Check-in and leave requests',
      },
    ],
  },
  {
    id: 'money',
    title: 'Money',
    blurb: 'Billing and renewals',
    modules: [
      {
        title: 'Finance & Invoice',
        label: 'Finance & Invoice',
        desc: 'Invoices and reminders',
      },
    ],
  },
  {
    id: 'ai',
    title: 'AI insights',
    blurb: 'Learning analysis and plans',
    modules: [
      {
        title: 'Question Analysis',
        label: 'Exam analysis',
        desc: 'Weaknesses from papers',
      },
      {
        title: 'AI Reports',
        label: 'Essay reports',
        desc: 'Essay scores and rewrites',
      },
      {
        title: 'Lesson Planning',
        label: 'Lesson plans',
        desc: 'Cambridge teaching plans',
      },
      {
        title: 'University Pathway',
        label: 'University pathway',
        desc: 'Majors and unis',
      },
      {
        title: 'Parent Portal',
        label: 'Parent portal',
        desc: 'Magic-link parent view',
      },
    ],
  },
];
