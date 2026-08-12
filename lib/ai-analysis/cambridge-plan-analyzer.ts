import OpenAI from 'openai';
import {
  buildCambridgePlanUserPrompt,
  buildMockCambridgeTeachingPlan,
  CAMBRIDGE_PLAN_MODEL,
  CAMBRIDGE_PLAN_SYSTEM_PROMPT,
  type CambridgePlanPromptInput,
} from './cambridge-plan-prompts';
import {
  type CambridgeCurriculum,
  type CambridgeTeachingPlan,
  parseCambridgeTeachingPlan,
} from './cambridge-plan-schema';
import {
  CAMBRIDGE_PLAN_MAX_COMPLETION_TOKENS,
  resolveOpenAiModel,
} from './model-config';
import { logAiUsage } from './usage-logger';

export interface GenerateCambridgePlanOptions {
  /** Optional injected OpenAI client (for tests). */
  openai?: OpenAI;
  studentName?: string;
  curriculum?: CambridgeCurriculum;
  subject?: string;
  /**
   * When true (default), return a deterministic mock if OPENAI_API_KEY is unset
   * and no client was injected. Set false to require a live key.
   */
  allowMockWithoutApiKey?: boolean;
}

/**
 * Generate a Cambridge teaching plan from student weaknesses (OpenAI or mock).
 *
 * @param weaknesses - Weak topics / skills to remediate (non-empty).
 * @param options - Curriculum, subject, and optional client override.
 * @returns Validated Cambridge teaching plan.
 */
export async function generateCambridgeTeachingPlan(
  weaknesses: string[],
  options: GenerateCambridgePlanOptions = {},
): Promise<CambridgeTeachingPlan> {
  const cleaned = weaknesses
    .map((item) => item.trim())
    .filter((item) => item.length > 0);

  if (cleaned.length === 0) {
    throw new Error('At least one student weakness is required');
  }

  const input: CambridgePlanPromptInput = {
    weaknesses: cleaned,
    curriculum: options.curriculum ?? 'IGCSE',
    subject: options.subject?.trim() || 'Mathematics',
    studentName: options.studentName,
  };

  const allowMock = options.allowMockWithoutApiKey !== false;
  const hasInjectedClient = Boolean(options.openai);
  const hasApiKey = Boolean(process.env.OPENAI_API_KEY);

  if (!hasInjectedClient && !hasApiKey) {
    if (allowMock) {
      return buildMockCambridgeTeachingPlan(input);
    }
    throw new Error('OPENAI_API_KEY is not configured');
  }

  const client =
    options.openai ??
    new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

  const model = resolveOpenAiModel(CAMBRIDGE_PLAN_MODEL);
  const startedAtMs = Date.now();

  const completion = await client.chat.completions.create({
    model,
    max_tokens: CAMBRIDGE_PLAN_MAX_COMPLETION_TOKENS,
    response_format: { type: 'json_object' },
    messages: [
      { role: 'system', content: CAMBRIDGE_PLAN_SYSTEM_PROMPT },
      { role: 'user', content: buildCambridgePlanUserPrompt(input) },
    ],
  });

  logAiUsage('cambridge_plan', model, startedAtMs, completion.usage);

  const content = completion.choices[0]?.message?.content;
  if (!content) {
    throw new Error('OpenAI returned an empty Cambridge plan response');
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error('OpenAI returned invalid JSON for Cambridge plan');
  }

  return parseCambridgeTeachingPlan(parsed);
}
