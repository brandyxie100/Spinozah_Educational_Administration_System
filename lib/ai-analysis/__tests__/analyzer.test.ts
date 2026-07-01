/**
 * @jest-environment node
 */
import type OpenAI from 'openai';
import { analyzeExamText } from '../analyzer';

const validOpenAiPayload = {
  studentName: 'Charlotte',
  subject: 'Reading Comprehension',
  totalScore: '68/100',
  strengths: ['Vocabulary'],
  weakAreas: ['Inference'],
  knowledgePoints: ['Context clues'],
  questionBreakdown: [
    { questionNumber: '1', topic: 'Reading', isCorrect: false },
  ],
  recommendations: ['Practice inference daily'],
};

function createMockOpenAI(content: string): OpenAI {
  return {
    chat: {
      completions: {
        create: jest.fn().mockResolvedValue({
          choices: [{ message: { content } }],
        }),
      },
    },
  } as unknown as OpenAI;
}

describe('analyzeExamText', () => {
  it('test_analyzeExamText_validResponse_returnsParsedReport', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));

    const report = await analyzeExamText('Exam text content', {
      openai: client,
      studentName: 'Charlotte',
    });

    expect(report.studentName).toBe('Charlotte');
    expect(report.weakAreas).toContain('Inference');
    expect(report.extractedTextPreview).toContain('Exam text');
  });

  it('test_analyzeExamText_emptyText_throws', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));

    await expect(
      analyzeExamText('   ', { openai: client }),
    ).rejects.toThrow('No extractable text found');
  });

  it('test_analyzeExamText_invalidJson_throws', async () => {
    const client = createMockOpenAI('not-json');

    await expect(
      analyzeExamText('Some exam text', { openai: client }),
    ).rejects.toThrow();
  });

  it('test_analyzeExamText_missingApiKey_throws', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    await expect(analyzeExamText('Some exam text')).rejects.toThrow(
      'OPENAI_API_KEY',
    );

    process.env.OPENAI_API_KEY = originalKey;
  });
});
