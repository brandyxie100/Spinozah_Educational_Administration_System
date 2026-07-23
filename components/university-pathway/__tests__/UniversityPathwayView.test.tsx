/**
 * Presenter tests for UniversityPathwayView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { UniversityPathwayView } from '@/components/university-pathway/UniversityPathwayView';
import type { PathwayRecommendation } from '@/lib/ai-analysis';

const sample: PathwayRecommendation = {
  studentName: 'Charlotte',
  qualification: 'A-Level',
  grades: [{ subject: 'Mathematics', grade: 'A' }],
  summary: 'Strong STEM profile for competitive universities.',
  universities: [
    {
      rank: 1,
      name: 'University of Auckland',
      region: 'New Zealand',
      admissionProbability: 78,
      rationale: 'Strong regional fit',
    },
  ],
  majors: [
    {
      rank: 1,
      name: 'Computer Science',
      relatedSubjects: ['Mathematics'],
      admissionProbability: 74,
      rationale: 'Aligns with maths strength',
    },
  ],
  roadmapSteps: ['Confirm predicted grades with teachers.'],
};

describe('UniversityPathwayView', () => {
  it('renders ranked majors and universities for parents', () => {
    render(<UniversityPathwayView recommendation={sample} />);
    expect(screen.getByText('University Pathway Report')).toBeInTheDocument();
    expect(
      screen.getByText('Strong STEM profile for competitive universities.'),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /#1 Computer Science/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /#1 University of Auckland/ }),
    ).toBeInTheDocument();
    expect(screen.getByText('Aligns with maths strength')).toBeInTheDocument();
  });

  it('invokes PDF download action when provided', () => {
    const onDownloadPdf = jest.fn();
    render(
      <UniversityPathwayView
        recommendation={sample}
        onDownloadPdf={onDownloadPdf}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /Download PDF/i }));
    expect(onDownloadPdf).toHaveBeenCalled();
  });
});
