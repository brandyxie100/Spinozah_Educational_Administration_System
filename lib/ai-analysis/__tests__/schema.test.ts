/**
 * @jest-environment node
 */
import {
  examAnalysisReportSchema,
  parseExamAnalysisReport,
} from '../schema';

const validReport = {
  studentName: 'Charlotte',
  subject: 'Reading Comprehension',
  totalScore: '68/100',
  strengths: ['Vocabulary recognition'],
  weakAreas: ['Inference questions'],
  knowledgePoints: ['Context clues', 'Paragraph structure'],
  questionBreakdown: [
    {
      questionNumber: '1',
      topic: 'Literal comprehension',
      isCorrect: true,
    },
    {
      questionNumber: '2',
      topic: 'Inference',
      isCorrect: false,
      notes: 'Missed implied meaning',
    },
  ],
  recommendations: ['Daily inference practice'],
  extractedTextPreview: 'Sample exam text preview',
};

describe('examAnalysisReportSchema', () => {
  it('test_parseExamAnalysisReport_validPayload_returnsReport', () => {
    const report = parseExamAnalysisReport(validReport);

    expect(report.studentName).toBe('Charlotte');
    expect(report.weakAreas).toContain('Inference questions');
    expect(report.questionBreakdown).toHaveLength(2);
  });

  it('test_parseExamAnalysisReport_missingRequiredField_throws', () => {
    const invalid = { ...validReport, subject: undefined };

    expect(() => parseExamAnalysisReport(invalid)).toThrow();
  });

  it('test_examAnalysisReportSchema_emptyArrays_accepts', () => {
    const parsed = examAnalysisReportSchema.parse({
      ...validReport,
      strengths: [],
      weakAreas: [],
      knowledgePoints: [],
      questionBreakdown: [],
      recommendations: [],
    });

    expect(parsed.strengths).toEqual([]);
  });
});
