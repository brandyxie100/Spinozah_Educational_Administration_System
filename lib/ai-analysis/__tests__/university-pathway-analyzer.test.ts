/**
 * @jest-environment node
 */
import type OpenAI from 'openai';
import { generateUniversityPathway } from '../university-pathway-analyzer';

const validOpenAiPayload = {
  studentName: 'Charlotte',
  qualification: 'A-Level',
  grades: [
    { subject: 'Mathematics', grade: 'A' },
    { subject: 'Physics', grade: 'B' },
  ],
  summary: 'Strong STEM pathway options.',
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
      rationale: 'Maths strength',
    },
  ],
  roadmapSteps: ['Confirm predicted grades'],
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

describe('generateUniversityPathway', () => {
  it('test_generateUniversityPathway_validResponse_returnsParsedRecommendation', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));

    const recommendation = await generateUniversityPathway(
      [
        { subject: 'Mathematics', grade: 'A' },
        { subject: 'Physics', grade: 'B' },
      ],
      {
        openai: client,
        studentName: 'Charlotte',
        qualification: 'A-Level',
      },
    );

    expect(recommendation.studentName).toBe('Charlotte');
    expect(recommendation.majors[0]?.name).toBe('Computer Science');
    expect(recommendation.universities[0]?.region).toBe('New Zealand');
  });

  it('test_generateUniversityPathway_emptyGrades_throws', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));

    await expect(
      generateUniversityPathway([{ subject: '  ', grade: '' }], {
        openai: client,
      }),
    ).rejects.toThrow('At least one subject grade is required');
  });

  it('test_generateUniversityPathway_invalidJson_throws', async () => {
    const client = createMockOpenAI('not-json');

    await expect(
      generateUniversityPathway([{ subject: 'Mathematics', grade: 'A' }], {
        openai: client,
      }),
    ).rejects.toThrow();
  });

  it('test_generateUniversityPathway_missingApiKey_returnsMock', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    const recommendation = await generateUniversityPathway(
      [{ subject: 'Chemistry', grade: 'A*' }],
      {
        qualification: 'IGCSE',
        studentName: 'Alex',
      },
    );

    expect(recommendation.universities).toHaveLength(5);
    expect(recommendation.summary).toContain('Mock');
    expect(recommendation.qualification).toBe('IGCSE');

    process.env.OPENAI_API_KEY = originalKey;
  });

  it('test_generateUniversityPathway_nceaMock_preservesQualification', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    const recommendation = await generateUniversityPathway(
      [{ subject: 'Calculus', grade: 'Excellence' }],
      { qualification: 'NCEA', studentName: 'Moana' },
    );

    expect(recommendation.qualification).toBe('NCEA');
    expect(recommendation.studentName).toBe('Moana');

    process.env.OPENAI_API_KEY = originalKey;
  });

  it('test_generateUniversityPathway_missingApiKeyNoMock_throws', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    await expect(
      generateUniversityPathway([{ subject: 'Mathematics', grade: 'A' }], {
        allowMockWithoutApiKey: false,
      }),
    ).rejects.toThrow('OPENAI_API_KEY');

    process.env.OPENAI_API_KEY = originalKey;
  });
});
