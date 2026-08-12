/**
 * Structured OpenAI usage / latency logging for AI analysis features.
 */

export type AiAnalysisFeature =
  | 'exam'
  | 'essay'
  | 'cambridge_plan'
  | 'university_pathway'
  | 'deep_agent_exam_to_plan';

export interface OpenAiUsageLike {
  prompt_tokens?: number | null;
  completion_tokens?: number | null;
  total_tokens?: number | null;
}

export interface AiUsageLogPayload {
  feature: AiAnalysisFeature;
  model: string;
  latencyMs: number;
  promptTokens: number | null;
  completionTokens: number | null;
  totalTokens: number | null;
}

/**
 * Normalize OpenAI usage fields into a log payload and write one JSON line.
 *
 * Safe to call when usage is missing (mocked clients / older API shapes).
 *
 * @param feature - Analyzer name for filtering logs.
 * @param model - Model id used for the call.
 * @param startedAtMs - `Date.now()` captured before the API call.
 * @param usage - Optional usage object from the completion response.
 */
export function logAiUsage(
  feature: AiAnalysisFeature,
  model: string,
  startedAtMs: number,
  usage?: OpenAiUsageLike | null,
): AiUsageLogPayload {
  const payload: AiUsageLogPayload = {
    feature,
    model,
    latencyMs: Math.max(0, Date.now() - startedAtMs),
    promptTokens: usage?.prompt_tokens ?? null,
    completionTokens: usage?.completion_tokens ?? null,
    totalTokens: usage?.total_tokens ?? null,
  };

  // Single-line JSON so ops can grep / ship to log drains without multiline noise.
  console.info('[ai-usage]', JSON.stringify(payload));
  return payload;
}
