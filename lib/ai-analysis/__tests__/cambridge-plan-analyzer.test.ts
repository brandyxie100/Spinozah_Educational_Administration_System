/**
 * @jest-environment node
 */
import type OpenAI from 'openai';
import { generateCambridgeTeachingPlan } from '../cambridge-plan-analyzer';

const validOpenAiPayload = {
  studentName: 'Charlotte',
  curriculum: 'IGCSE',
  subject: 'Mathematics',
  weaknesses: ['Fractions', 'Algebra'],
  focusTopics: ['Fractions', 'Algebra'],
  summary: 'Ten lessons remediating fractions and algebra.',
  lessons: [
    {
      lessonNumber: 1,
      title: 'Fractions foundations',
      objectives: ['Identify equivalent fractions'],
      activities: ['Guided practice'],
      homework: 'Worksheet A',
      addressesWeaknesses: ['Fractions'],
    },
  ],
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

describe('generateCambridgeTeachingPlan', () => {
  it('test_generateCambridgeTeachingPlan_validResponse_returnsParsedPlan', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));

    const plan = await generateCambridgeTeachingPlan(['Fractions', 'Algebra'], {
      openai: client,
      studentName: 'Charlotte',
      curriculum: 'IGCSE',
      subject: 'Mathematics',
    });

    expect(plan.studentName).toBe('Charlotte');
    expect(plan.weaknesses).toContain('Fractions');
    expect(plan.lessons[0]?.title).toContain('Fractions');
  });

  it('test_generateCambridgeTeachingPlan_emptyWeaknesses_throws', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));

    await expect(
      generateCambridgeTeachingPlan(['  ', ''], { openai: client }),
    ).rejects.toThrow('At least one student weakness is required');
  });

  it('test_generateCambridgeTeachingPlan_invalidJson_throws', async () => {
    const client = createMockOpenAI('not-json');

    await expect(
      generateCambridgeTeachingPlan(['Algebra'], { openai: client }),
    ).rejects.toThrow();
  });

  it('test_generateCambridgeTeachingPlan_missingApiKey_returnsMock', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    const plan = await generateCambridgeTeachingPlan(['Probability'], {
      curriculum: 'A Level',
      subject: 'Mathematics',
      studentName: 'Alex',
    });

    expect(plan.lessons).toHaveLength(10);
    expect(plan.summary).toContain('Mock');
    expect(plan.curriculum).toBe('A Level');

    process.env.OPENAI_API_KEY = originalKey;
  });

  it('test_generateCambridgeTeachingPlan_missingApiKeyNoMock_throws', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    await expect(
      generateCambridgeTeachingPlan(['Algebra'], {
        allowMockWithoutApiKey: false,
      }),
    ).rejects.toThrow('OPENAI_API_KEY');

    process.env.OPENAI_API_KEY = originalKey;
  });
});
