import { z } from 'zod';

/** Single question outcome within an exam report. */
export const questionBreakdownItemSchema = z.object({
  questionNumber: z.string(),
  topic: z.string(),
  isCorrect: z.boolean(),
  notes: z.string().optional(),
});

/** Structured weakness report returned by the exam analysis pipeline. */
export const examAnalysisReportSchema = z.object({
  studentName: z.string(),
  subject: z.string(),
  totalScore: z.string(),
  strengths: z.array(z.string()),
  weakAreas: z.array(z.string()),
  knowledgePoints: z.array(z.string()),
  questionBreakdown: z.array(questionBreakdownItemSchema),
  recommendations: z.array(z.string()),
  extractedTextPreview: z.string(),
});

export type QuestionBreakdownItem = z.infer<typeof questionBreakdownItemSchema>;
export type ExamAnalysisReport = z.infer<typeof examAnalysisReportSchema>;

/** AI model output before we attach extractedTextPreview. */
export const examAnalysisAiPayloadSchema = examAnalysisReportSchema.omit({
  extractedTextPreview: true,
});

export type ExamAnalysisAiPayload = z.infer<typeof examAnalysisAiPayloadSchema>;

/**
 * Parse and validate OpenAI exam analysis JSON (without text preview).
 *
 * @param data - Raw JSON from OpenAI.
 * @returns Validated AI payload fields.
 */
export function parseExamAnalysisAiPayload(data: unknown): ExamAnalysisAiPayload {
  return examAnalysisAiPayloadSchema.parse(data);
}

/**
 * Parse and validate a full exam analysis report payload.
 *
 * @param data - Raw JSON from OpenAI or API response.
 * @returns Validated exam analysis report.
 */
export function parseExamAnalysisReport(data: unknown): ExamAnalysisReport {
  return examAnalysisReportSchema.parse(data);
}
