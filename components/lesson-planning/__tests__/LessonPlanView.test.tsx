/**
 * Presenter tests for LessonPlanView.
 */

import { render, screen } from '@testing-library/react';
import { LessonPlanView } from '@/components/lesson-planning/LessonPlanView';
import type { CambridgeTeachingPlan } from '@/lib/ai-analysis';

const sample: CambridgeTeachingPlan = {
  studentName: 'Charlotte',
  curriculum: 'IGCSE',
  subject: 'Mathematics',
  weaknesses: ['Fractions', 'Algebra'],
  focusTopics: ['Fractions'],
  summary: 'Remediate core number sense gaps.',
  lessons: [
    {
      lessonNumber: 1,
      title: 'Fractions foundations',
      objectives: ['Identify equivalent fractions'],
      activities: ['Warm-up diagnostic'],
      homework: 'Worksheet 1',
      addressesWeaknesses: ['Fractions'],
    },
  ],
};

describe('LessonPlanView', () => {
  it('renders curriculum, weaknesses, and lesson details', () => {
    render(<LessonPlanView plan={sample} />);
    expect(screen.getByText('Cambridge Teaching Plan')).toBeInTheDocument();
    expect(screen.getByText('Remediate core number sense gaps.')).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /1\. Fractions foundations/ }),
    ).toBeInTheDocument();
    expect(screen.getByText('Identify equivalent fractions')).toBeInTheDocument();
    expect(screen.getByText('Warm-up diagnostic')).toBeInTheDocument();
  });
});
