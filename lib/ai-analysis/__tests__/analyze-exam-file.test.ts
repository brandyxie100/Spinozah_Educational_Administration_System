/**
 * @jest-environment node
 */
import { analyzeExamFile } from '../analyze-exam-file';
import { SUPPORTED_MIME_TYPES } from '../constants';

jest.mock('../extract-pdf', () => ({
  extractTextFromPdf: jest.fn().mockResolvedValue('PDF exam content'),
}));

jest.mock('../extract-image', () => ({
  extractTextFromImage: jest.fn().mockResolvedValue('Image exam content'),
}));

jest.mock('../analyzer', () => ({
  analyzeExamText: jest.fn().mockResolvedValue({
    studentName: 'Charlotte',
    subject: 'Math',
    totalScore: '80/100',
    strengths: ['Algebra'],
    weakAreas: ['Geometry'],
    knowledgePoints: ['Fractions'],
    questionBreakdown: [],
    recommendations: ['Review geometry'],
    extractedTextPreview: 'PDF exam content',
  }),
}));

describe('analyzeExamFile', () => {
  it('test_analyzeExamFile_pdfFile_returnsReport', async () => {
    const file = new File(['pdf-bytes'], 'charlotte exam.pdf', {
      type: SUPPORTED_MIME_TYPES.PDF,
    });

    const report = await analyzeExamFile(file);

    expect(report.subject).toBe('Math');
    expect(report.studentName).toBe('Charlotte');
  });

  it('test_analyzeExamFile_unsupportedType_throws', async () => {
    const file = new File(['data'], 'notes.txt', { type: 'text/plain' });

    await expect(analyzeExamFile(file)).rejects.toThrow('Unsupported file type');
  });

  it('test_analyzeExamFile_emptyFile_throws', async () => {
    const file = new File([], 'empty.pdf', { type: SUPPORTED_MIME_TYPES.PDF });

    await expect(analyzeExamFile(file)).rejects.toThrow('File is empty');
  });
});
