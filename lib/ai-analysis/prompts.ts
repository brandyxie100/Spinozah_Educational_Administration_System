import {
  EXAM_ANALYSIS_MODEL,
  EXTRACTED_TEXT_PREVIEW_MAX_LENGTH,
} from './constants';

/** System prompt instructing the model to return structured JSON only. */
export const EXAM_ANALYSIS_SYSTEM_PROMPT = `You are an expert education analyst for tutoring centers.
Analyze exam or test paper text and return ONLY valid JSON matching this shape:
{
  "studentName": string,
  "subject": string,
  "totalScore": string,
  "strengths": string[],
  "weakAreas": string[],
  "knowledgePoints": string[],
  "questionBreakdown": [
    {
      "questionNumber": string,
      "topic": string,
      "isCorrect": boolean,
      "notes": string (optional)
    }
  ],
  "recommendations": string[]
}
Infer subject and score when possible. Be specific about weak areas and teaching recommendations.`;

/**
 * Build the user prompt for exam analysis.
 *
 * @param extractedText - Full OCR/PDF text from the uploaded paper.
 * @param studentName - Optional student name hint from filename or form.
 * @returns User message for the chat completion.
 */
export function buildExamAnalysisUserPrompt(
  extractedText: string,
  studentName?: string,
): string {
  const nameHint = studentName
    ? `The student name hint is "${studentName}". Use it when appropriate.\n\n`
    : '';

  return `${nameHint}Analyze this exam content and produce the JSON report:\n\n${extractedText}`;
}

/**
 * Truncate extracted text for preview fields and prompt size control.
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
