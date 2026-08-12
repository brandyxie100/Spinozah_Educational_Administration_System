import { EXTRACTED_TEXT_PREVIEW_MAX_LENGTH } from './constants';
import { truncateForPrompt } from './model-config';

/** OpenAI model used for essay analysis when OPENAI_MODEL is unset. */
export const ESSAY_ANALYSIS_MODEL = 'gpt-4o-mini';

/**
 * Slim system prompt: Zod validates the shape after parse.
 */
export const ESSAY_ANALYSIS_SYSTEM_PROMPT = `You are an expert English writing tutor for tutoring centers.
Analyze the student essay and return ONLY valid JSON with:
studentName, title, grammarScore/vocabularyScore/structureScore (0-100),
cohesionNotes[], suggestions{grammarImprovements[], advancedVocabulary[],
sentenceRewrites[{original, rewrite}]}, summary.
Be specific and actionable. Prefer 2–5 items in each suggestion array.`;

/**
 * Build the user prompt for essay analysis.
 *
 * @param essayText - Full essay text (pasted or extracted).
 * @param studentName - Optional student name hint.
 * @returns User message for the chat completion (input may be truncated).
 */
export function buildEssayAnalysisUserPrompt(
  essayText: string,
  studentName?: string,
): string {
  const nameHint = studentName
    ? `The student name hint is "${studentName}". Use it when appropriate.\n\n`
    : '';

  const body = truncateForPrompt(essayText);
  return `${nameHint}Analyze this essay and produce the JSON report:\n\n${body}`;
}

/**
 * Truncate essay text for preview fields.
 *
 * @param text - Full essay text.
 * @returns Preview string capped at EXTRACTED_TEXT_PREVIEW_MAX_LENGTH.
 */
export function buildEssayTextPreview(text: string): string {
  if (text.length <= EXTRACTED_TEXT_PREVIEW_MAX_LENGTH) {
    return text;
  }

  return `${text.slice(0, EXTRACTED_TEXT_PREVIEW_MAX_LENGTH)}…`;
}

/**
 * Deterministic mock report used when OPENAI_API_KEY is unset (local/dev/tests).
 *
 * @param essayText - Essay text used for preview and lightweight heuristics.
 * @param studentName - Optional student name.
 * @returns Validated-shaped essay analysis report.
 */
export function buildMockEssayAnalysisReport(
  essayText: string,
  studentName?: string,
): {
  studentName: string;
  title: string;
  grammarScore: number;
  vocabularyScore: number;
  structureScore: number;
  cohesionNotes: string[];
  suggestions: {
    grammarImprovements: string[];
    advancedVocabulary: string[];
    sentenceRewrites: { original: string; rewrite: string }[];
  };
  summary: string;
  extractedTextPreview: string;
} {
  const firstLine = essayText.trim().split('\n')[0] ?? 'Untitled essay';
  const title =
    firstLine.length > 60 ? `${firstLine.slice(0, 57)}…` : firstLine || 'Untitled essay';
  const sampleSentence =
    essayText.trim().split(/[.!?]/)[0]?.trim() || 'This is a sample sentence';

  return {
    studentName: studentName?.trim() || 'Unknown student',
    title,
    grammarScore: 72,
    vocabularyScore: 68,
    structureScore: 74,
    cohesionNotes: [
      'Ideas are mostly connected with basic transitions.',
      'Consider clearer topic sentences for each paragraph.',
    ],
    suggestions: {
      grammarImprovements: [
        'Check subject-verb agreement in longer sentences.',
        'Prefer consistent tense across paragraphs.',
      ],
      advancedVocabulary: [
        'Replace "very good" with more precise adjectives (e.g. "compelling").',
        'Use academic verbs such as "demonstrate" or "illustrate".',
      ],
      sentenceRewrites: [
        {
          original: sampleSentence,
          rewrite: `${sampleSentence} — revised for clarity and flow.`,
        },
      ],
    },
    summary:
      'Mock analysis (no OPENAI_API_KEY). Scores and rewrites are illustrative for local development.',
    extractedTextPreview: buildEssayTextPreview(essayText),
  };
}
