import OpenAI from 'openai';
import { EXAM_ANALYSIS_MODEL } from './constants';
import { DEFAULT_MAX_COMPLETION_TOKENS, resolveOpenAiModel } from './model-config';
import {
  buildExamAnalysisUserPrompt,
  buildExtractedTextPreview,
  EXAM_ANALYSIS_SYSTEM_PROMPT,
} from './prompts';
import {
  type ExamAnalysisReport,
  parseExamAnalysisAiPayload,
} from './schema';
import { logAiUsage } from './usage-logger';

export interface AnalyzeExamTextOptions {
  /** Optional injected OpenAI client (for tests). */
  openai?: OpenAI;
  /** Student name hint from upload filename or UI. */
  studentName?: string;
}

/**
 * Call OpenAI to produce a structured exam weakness report from extracted text.
 *
 * @param extractedText - Plain text from PDF or OCR.
 * @param options - Optional client override and student name hint.
 * @returns Validated exam analysis report with text preview attached.
 */
export async function analyzeExamText(
  extractedText: string,
  options: AnalyzeExamTextOptions = {},
): Promise<ExamAnalysisReport> {
  const trimmedText = extractedText.trim();
  if (!trimmedText) {
    throw new Error('No extractable text found in uploaded file');
  }

  const client =
    options.openai ??
    new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

  if (!options.openai && !process.env.OPENAI_API_KEY) {
    throw new Error('OPENAI_API_KEY is not configured');
  }

  const model = resolveOpenAiModel(EXAM_ANALYSIS_MODEL);
  const startedAtMs = Date.now();

  const completion = await client.chat.completions.create({
    model,
    max_tokens: DEFAULT_MAX_COMPLETION_TOKENS,
    response_format: { type: 'json_object' },
    messages: [
      { role: 'system', content: EXAM_ANALYSIS_SYSTEM_PROMPT },
      {
        role: 'user',
        content: buildExamAnalysisUserPrompt(trimmedText, options.studentName),
      },
    ],
  });

  logAiUsage('exam', model, startedAtMs, completion.usage);

  const content = completion.choices[0]?.message?.content;
  if (!content) {
    throw new Error('OpenAI returned an empty analysis response');
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error('OpenAI returned invalid JSON for exam analysis');
  }

  const aiPayload = parseExamAnalysisAiPayload(parsed);
  const preview = buildExtractedTextPreview(trimmedText);

  return {
    ...aiPayload,
    extractedTextPreview: preview,
  };
}
