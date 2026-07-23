/**
 * @jest-environment node
 */
import { buildMockPathwayRecommendation } from '../university-pathway-prompts';
import { buildPathwayReportPdfBytes } from '../university-pathway-pdf';
import { parsePathwayRecommendation } from '../university-pathway-schema';

describe('pathway PDF helper', () => {
  it('builds non-empty PDF bytes from a recommendation', () => {
    const recommendation = parsePathwayRecommendation(
      buildMockPathwayRecommendation({
        grades: [
          { subject: 'Mathematics', grade: 'A' },
          { subject: 'Physics', grade: 'B' },
        ],
        qualification: 'A-Level',
        studentName: 'Charlotte',
      }),
    );
    const pdf = buildPathwayReportPdfBytes(recommendation);
    expect(pdf.byteLength).toBeGreaterThan(100);
    expect(Buffer.from(pdf).subarray(0, 4).toString()).toBe('%PDF');
  });
});
