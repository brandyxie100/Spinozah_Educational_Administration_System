import {
  EXAM_ANALYSIS_MODEL,
  EXTRACTED_TEXT_PREVIEW_MAX_LENGTH,
} from './constants';
import { truncateForPrompt } from './model-config';

/**
 * Slim system prompt: Zod validates the shape after parse; keep prose instructional.
 */
export const EXAM_ANALYSIS_SYSTEM_PROMPT = `You are an expert education analyst for tutoring centers.
Analyze exam or test paper text and return ONLY valid JSON with:
studentName, subject, totalScore (string), strengths[], weakAreas[], knowledgePoints[],
questionBreakdown[{questionNumber, topic, isCorrect, notes?}], recommendations[].
Infer subject and score when possible. Be specific about weak areas and teaching recommendations.`;

/**
 * Build the user prompt for exam analysis.
 *
 * @param extractedText - Full OCR/PDF text from the uploaded paper.
 * @param studentName - Optional student name hint from filename or form.
 * @returns User message for the chat completion (input may be truncated).
 */
export function buildExamAnalysisUserPrompt(
  extractedText: string,
  studentName?: string,
): string {
  const nameHint = studentName
    ? `The student name hint is "${studentName}". Use it when appropriate.\n\n`
    : '';

  const body = truncateForPrompt(extractedText);
  return `${nameHint}Analyze this exam content and produce the JSON report:\n\n${body}`;
}

/**
 * Truncate extracted text for preview fields (UI only — not the model prompt).
 *
 * @param text - Full extracted document text.
 * @returns Preview string capped at EXTRACTED_TEXT_PREVIEW_MAX_LENGTH.
 */
export function buildExtractedTextPreview(text: string): string {
  if (text.length <= EXTRACTED_TEXT_PREVIEW_MAX_LENGTH) {
    return text;
  }

  return `${text.slice(0, EXTRACTED_TEXT_PREVIEW_MAX_LENGTH)}…`;
}

export { EXAM_ANALYSIS_MODEL, EXTRACTED_TEXT_PREVIEW_MAX_LENGTH };
