import OpenAI from 'openai';
import {
  buildEssayAnalysisUserPrompt,
  buildEssayTextPreview,
  buildMockEssayAnalysisReport,
  ESSAY_ANALYSIS_MODEL,
  ESSAY_ANALYSIS_SYSTEM_PROMPT,
} from './essay-prompts';
import {
  type EssayAnalysisReport,
  parseEssayAnalysisAiPayload,
} from './essay-schema';
import { DEFAULT_MAX_COMPLETION_TOKENS, resolveOpenAiModel } from './model-config';
import { logAiUsage } from './usage-logger';

export interface AnalyzeEssayTextOptions {
  /** Optional injected OpenAI client (for tests). */
  openai?: OpenAI;
  /** Student name hint from upload filename or UI. */
  studentName?: string;
  /**
   * When true (default), return a deterministic mock if OPENAI_API_KEY is unset
   * and no client was injected. Set false to require a live key.
   */
  allowMockWithoutApiKey?: boolean;
}

/**
 * Call OpenAI (or mock) to produce structured essay scores and rewrite suggestions.
 *
 * @param essayText - Plain essay text (pasted or extracted from a file).
 * @param options - Optional client override and student name hint.
 * @returns Validated essay analysis report with text preview attached.
 */
export async function analyzeEssayText(
  essayText: string,
  options: AnalyzeEssayTextOptions = {},
): Promise<EssayAnalysisReport> {
  const trimmedText = essayText.trim();
  if (!trimmedText) {
    throw new Error('No essay text provided');
  }

  const allowMock = options.allowMockWithoutApiKey !== false;
  const hasInjectedClient = Boolean(options.openai);
  const hasApiKey = Boolean(process.env.OPENAI_API_KEY);

  if (!hasInjectedClient && !hasApiKey) {
    if (allowMock) {
      return buildMockEssayAnalysisReport(trimmedText, options.studentName);
    }
    throw new Error('OPENAI_API_KEY is not configured');
  }

  const client =
    options.openai ??
    new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

  const model = resolveOpenAiModel(ESSAY_ANALYSIS_MODEL);
  const startedAtMs = Date.now();

  const completion = await client.chat.completions.create({
    model,
    max_tokens: DEFAULT_MAX_COMPLETION_TOKENS,
    response_format: { type: 'json_object' },
    messages: [
      { role: 'system', content: ESSAY_ANALYSIS_SYSTEM_PROMPT },
      {
        role: 'user',
        content: buildEssayAnalysisUserPrompt(trimmedText, options.studentName),
      },
    ],
  });

  logAiUsage('essay', model, startedAtMs, completion.usage);

  const content = completion.choices[0]?.message?.content;
  if (!content) {
    throw new Error('OpenAI returned an empty essay analysis response');
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error('OpenAI returned invalid JSON for essay analysis');
  }

  const aiPayload = parseEssayAnalysisAiPayload(parsed);
  return {
    ...aiPayload,
    extractedTextPreview: buildEssayTextPreview(trimmedText),
  };
}
