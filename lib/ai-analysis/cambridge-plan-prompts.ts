import type { CambridgeCurriculum, CambridgeTeachingPlan } from './cambridge-plan-schema';

/** OpenAI model used for Cambridge lesson planning when OPENAI_MODEL is unset. */
export const CAMBRIDGE_PLAN_MODEL = 'gpt-4o-mini';

/**
 * Slim system prompt: Zod validates the shape; keep lesson count capped for tokens.
 */
export const CAMBRIDGE_PLAN_SYSTEM_PROMPT = `You are an expert Cambridge curriculum tutor planner for tutoring centers.
Generate a teaching plan that remediates weak topics. Return ONLY valid JSON with:
studentName, curriculum (Cambridge Primary|Lower Secondary|Checkpoint|IGCSE|AS Level|A Level),
subject, weaknesses[], focusTopics[], summary, lessons[{lessonNumber, title,
objectives[] (max 3), activities[] (max 3), homework (1 short sentence), addressesWeaknesses[]}].
Use exactly 10 lessons. Each lesson maps to at least one weakness. Keep text concise.`;

export interface CambridgePlanPromptInput {
  weaknesses: string[];
  curriculum: CambridgeCurriculum;
  subject: string;
  studentName?: string;
}

/**
 * Build the user prompt for Cambridge plan generation.
 *
 * @param input - Weaknesses and curriculum context.
 * @returns User message for the chat completion.
 */
export function buildCambridgePlanUserPrompt(input: CambridgePlanPromptInput): string {
  const nameHint = input.studentName?.trim()
    ? `Student name: "${input.studentName.trim()}".\n`
    : '';
  const weaknessList = input.weaknesses.map((item) => `- ${item}`).join('\n');

  return `${nameHint}Curriculum: ${input.curriculum}
Subject: ${input.subject}

Student weaknesses (map lessons to these):
${weaknessList}

Generate a 10-lesson Cambridge teaching plan as JSON.`;
}

/**
 * Deterministic mock plan used when OPENAI_API_KEY is unset (local/dev/tests).
 *
 * @param input - Weaknesses and curriculum context.
 * @returns Validated-shaped Cambridge teaching plan.
 */
export function buildMockCambridgeTeachingPlan(
  input: CambridgePlanPromptInput,
): CambridgeTeachingPlan {
  const weaknesses =
    input.weaknesses.length > 0 ? input.weaknesses : ['General review'];
  const studentName = input.studentName?.trim() || 'Unknown student';
  const subject = input.subject.trim() || 'Mathematics';

  const lessons = Array.from({ length: 10 }, (_, index) => {
    const lessonNumber = index + 1;
    const weakness = weaknesses[index % weaknesses.length] ?? weaknesses[0];
    return {
      lessonNumber,
      title: `Lesson ${lessonNumber}: ${weakness} foundations`,
      objectives: [
        `Diagnose gaps in ${weakness}`,
        `Practise core ${subject} skills for ${weakness}`,
      ],
      activities: [
        `Warm-up diagnostic on ${weakness}`,
        `Guided examples and peer explanation`,
        `Independent practice set`,
      ],
      homework: `Complete a short worksheet on ${weakness} (15–20 minutes).`,
      addressesWeaknesses: [weakness],
    };
  });

  return {
    studentName,
    curriculum: input.curriculum,
    subject,
    weaknesses,
    focusTopics: weaknesses.slice(0, 5),
    summary:
      'Mock Cambridge plan (no OPENAI_API_KEY). Ten lessons remediating listed weaknesses for local development.',
    lessons,
  };
}
