import OpenAI from 'openai';
import {
  buildMockPathwayRecommendation,
  buildUniversityPathwayUserPrompt,
  UNIVERSITY_PATHWAY_MODEL,
  UNIVERSITY_PATHWAY_SYSTEM_PROMPT,
  type UniversityPathwayPromptInput,
} from './university-pathway-prompts';
import {
  type PathwayQualification,
  type PathwayRecommendation,
  type SubjectGrade,
  parsePathwayRecommendation,
} from './university-pathway-schema';

export interface GenerateUniversityPathwayOptions {
  /** Optional injected OpenAI client (for tests). */
  openai?: OpenAI;
  studentName?: string;
  qualification?: PathwayQualification;
  /**
   * When true (default), return a deterministic mock if OPENAI_API_KEY is unset
   * and no client was injected. Set false to require a live key.
   */
  allowMockWithoutApiKey?: boolean;
}

/**
 * Generate ranked university/major recommendations from exam grades.
 *
 * @param grades - Subject + grade pairs (non-empty).
 * @param options - Qualification, student name, and optional client override.
 * @returns Validated pathway recommendation.
 */
export async function generateUniversityPathway(
  grades: SubjectGrade[],
  options: GenerateUniversityPathwayOptions = {},
): Promise<PathwayRecommendation> {
  const cleaned = grades
    .map((item) => ({
      subject: item.subject.trim(),
      grade: item.grade.trim(),
    }))
    .filter((item) => item.subject.length > 0 && item.grade.length > 0);

  if (cleaned.length === 0) {
    throw new Error('At least one subject grade is required');
  }

  const input: UniversityPathwayPromptInput = {
    grades: cleaned,
    qualification: options.qualification ?? 'A-Level',
    studentName: options.studentName,
  };

  const allowMock = options.allowMockWithoutApiKey !== false;
  const hasInjectedClient = Boolean(options.openai);
  const hasApiKey = Boolean(process.env.OPENAI_API_KEY);

  if (!hasInjectedClient && !hasApiKey) {
    if (allowMock) {
      return buildMockPathwayRecommendation(input);
    }
    throw new Error('OPENAI_API_KEY is not configured');
  }

  const client =
    options.openai ??
    new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

  const completion = await client.chat.completions.create({
    model: UNIVERSITY_PATHWAY_MODEL,
    response_format: { type: 'json_object' },
    messages: [
      { role: 'system', content: UNIVERSITY_PATHWAY_SYSTEM_PROMPT },
      { role: 'user', content: buildUniversityPathwayUserPrompt(input) },
    ],
  });

  const content = completion.choices[0]?.message?.content;
  if (!content) {
    throw new Error('OpenAI returned an empty pathway response');
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error('OpenAI returned invalid JSON for university pathway');
  }

  return parsePathwayRecommendation(parsed);
}
