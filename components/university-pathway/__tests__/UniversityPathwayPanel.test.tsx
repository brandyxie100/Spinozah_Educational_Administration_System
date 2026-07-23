/**
 * Panel tests for UniversityPathwayPanel curriculum selection (AIJOB-69).
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { UniversityPathwayPanel } from '@/components/university-pathway/UniversityPathwayPanel';

jest.mock('@/hooks/useUniversityPathway', () => ({
  useUniversityPathway: () => ({
    recommendation: null,
    isGenerating: false,
    isDownloadingPdf: false,
    error: null,
    generatePathway: jest.fn(),
    downloadPdf: jest.fn(),
    reset: jest.fn(),
  }),
}));

describe('UniversityPathwayPanel', () => {
  it('offers NCEA and IB curriculum options alongside IGCSE and A-Level', () => {
    render(<UniversityPathwayPanel />);

    const select = screen.getByLabelText(/^Qualification$/);
    expect(select).toBeInTheDocument();

    for (const option of ['IGCSE', 'A-Level', 'NCEA', 'IB']) {
      expect(
        screen.getByRole('option', { name: option }),
      ).toBeInTheDocument();
    }

    fireEvent.change(select, { target: { value: 'NCEA' } });
    expect(select).toHaveValue('NCEA');

    fireEvent.change(select, { target: { value: 'IB' } });
    expect(select).toHaveValue('IB');
  });
});
