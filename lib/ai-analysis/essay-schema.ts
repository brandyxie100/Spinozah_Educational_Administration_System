import { z } from 'zod';

/** One sentence rewrite suggestion from essay analysis. */
export const sentenceRewriteSchema = z.object({
  original: z.string(),
  rewrite: z.string(),
});

/** Structured rewrite suggestions returned with essay scores. */
export const essaySuggestionsSchema = z.object({
  grammarImprovements: z.array(z.string()),
  advancedVocabulary: z.array(z.string()),
  sentenceRewrites: z.array(sentenceRewriteSchema),
});

/**
 * Structured essay analysis report (Skill G / AIJOB-52).
 *
 * Scores are integers 0–100 for grammar, vocabulary, and structure.
 */
export const essayAnalysisReportSchema = z.object({
  studentName: z.string(),
  title: z.string(),
  grammarScore: z.number().min(0).max(100),
  vocabularyScore: z.number().min(0).max(100),
  structureScore: z.number().min(0).max(100),
  cohesionNotes: z.array(z.string()),
  suggestions: essaySuggestionsSchema,
  summary: z.string(),
  extractedTextPreview: z.string(),
});

export type SentenceRewrite = z.infer<typeof sentenceRewriteSchema>;
export type EssaySuggestions = z.infer<typeof essaySuggestionsSchema>;
export type EssayAnalysisReport = z.infer<typeof essayAnalysisReportSchema>;

/** AI model output before we attach extractedTextPreview. */
export const essayAnalysisAiPayloadSchema = essayAnalysisReportSchema.omit({
  extractedTextPreview: true,
});

export type EssayAnalysisAiPayload = z.infer<typeof essayAnalysisAiPayloadSchema>;

/**
 * Parse and validate OpenAI essay analysis JSON (without text preview).
 *
 * @param data - Raw JSON from OpenAI.
 * @returns Validated AI payload fields.
 */
export function parseEssayAnalysisAiPayload(data: unknown): EssayAnalysisAiPayload {
  return essayAnalysisAiPayloadSchema.parse(data);
}

/**
 * Parse and validate a full essay analysis report payload.
 *
 * @param data - Raw JSON from OpenAI or API response.
 * @returns Validated essay analysis report.
 */
export function parseEssayAnalysisReport(data: unknown): EssayAnalysisReport {
  return essayAnalysisReportSchema.parse(data);
}
