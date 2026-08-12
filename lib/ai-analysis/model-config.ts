/**
 * Shared OpenAI model / token budget resolution for AI analysis features.
 *
 * Prefer OPENAI_MODEL when set; otherwise fall back to the feature default.
 */

/** Default chat model when OPENAI_MODEL is unset. */
export const DEFAULT_OPENAI_MODEL = 'gpt-4o-mini';

/** Soft cap on characters sent to the model for exam/essay body text. */
export const PROMPT_INPUT_MAX_CHARS = 24_000;

/** Default max completion tokens for structured JSON responses. */
export const DEFAULT_MAX_COMPLETION_TOKENS = 4_096;

/** Tighter budget for large Cambridge plans (still enough for ~10 lessons). */
export const CAMBRIDGE_PLAN_MAX_COMPLETION_TOKENS = 3_500;

/** Pathway lists are smaller than full lesson plans. */
export const PATHWAY_MAX_COMPLETION_TOKENS = 2_500;

/**
 * Resolve the model id for an analyzer.
 *
 * @param featureDefault - Hardcoded default for the feature (e.g. gpt-4o-mini).
 * @returns Env override when present and non-empty; otherwise the feature default.
 */
export function resolveOpenAiModel(featureDefault: string = DEFAULT_OPENAI_MODEL): string {
  const fromEnv = process.env.OPENAI_MODEL?.trim();
  if (fromEnv) {
    return fromEnv;
  }
  return featureDefault;
}

/**
 * Truncate long document text before embedding it in a user prompt.
 *
 * Keeps the start of the document (headers, early questions) and appends a
 * marker so the model knows content was clipped.
 *
 * @param text - Full extracted or pasted text.
 * @param maxChars - Character budget (defaults to PROMPT_INPUT_MAX_CHARS).
 * @returns Original text or a truncated prefix with an ellipsis marker.
 */
export function truncateForPrompt(
  text: string,
  maxChars: number = PROMPT_INPUT_MAX_CHARS,
): string {
  if (text.length <= maxChars) {
    return text;
  }
  return `${text.slice(0, maxChars)}\n\n[…truncated for prompt size; ${text.length - maxChars} characters omitted]`;
}
