/**
 * Presenter tests for EssayReportView.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { EssayReportView } from '@/components/essay-analysis/EssayReportView';
import type { EssayAnalysisReport } from '@/lib/ai-analysis';

const sample: EssayAnalysisReport = {
  studentName: 'Charlotte',
  title: 'My Summer Holiday',
  grammarScore: 80,
  vocabularyScore: 75,
  structureScore: 78,
  cohesionNotes: ['Clear flow'],
  suggestions: {
    grammarImprovements: ['Check articles'],
    advancedVocabulary: ['Use compelling'],
    sentenceRewrites: [{ original: 'It was nice.', rewrite: 'It was memorable.' }],
  },
  summary: 'Good draft',
  extractedTextPreview: 'It was nice.',
};

describe('EssayReportView', () => {
  it('renders scores and rewrite suggestions', () => {
    render(<EssayReportView report={sample} />);
    expect(screen.getByText('80/100')).toBeInTheDocument();
    expect(screen.getByText('75/100')).toBeInTheDocument();
    expect(screen.getByText('It was memorable.')).toBeInTheDocument();
  });

  it('invokes PDF download callback', () => {
    const onDownloadPdf = jest.fn();
    render(<EssayReportView report={sample} onDownloadPdf={onDownloadPdf} />);
    fireEvent.click(screen.getByRole('button', { name: /Download PDF/i }));
    expect(onDownloadPdf).toHaveBeenCalled();
  });
});
