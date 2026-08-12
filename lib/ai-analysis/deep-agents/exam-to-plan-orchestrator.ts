/**
 * Deep Agents prototype: exam text → weaknesses → Cambridge teaching plan.
 *
 * Not wired into production BFF routes. Use the CLI script or comparison helper
 * to measure tokens vs the existing two-shot OpenAI chain.
 *
 * @see docs/07-deep-agents-decision-guide.md
 * @see docs/08-deep-agents-context-engineering.md
 */

import path from 'node:path';
import { createDeepAgent } from 'deepagents';
import { providerStrategy, tool } from 'langchain';
import { z } from 'zod';
import { analyzeExamText } from '../analyzer';
import {
  buildMockCambridgeTeachingPlan,
  CAMBRIDGE_PLAN_MODEL,
} from '../cambridge-plan-prompts';
import {
  cambridgeTeachingPlanSchema,
  type CambridgeCurriculum,
  type CambridgeTeachingPlan,
} from '../cambridge-plan-schema';
import { resolveOpenAiModel } from '../model-config';
import { logAiUsage } from '../usage-logger';

export interface ExamToPlanInput {
  examText: string;
  studentName?: string;
  curriculum?: CambridgeCurriculum;
  subject?: string;
}

export interface ExamToPlanDeepAgentResult {
  plan: CambridgeTeachingPlan;
  weaknesses: string[];
  model: string;
  latencyMs: number;
}

/**
 * Resolve a LangChain model id string for Deep Agents (provider:model).
 *
 * @param featureDefault - Fallback model when OPENAI_MODEL is unset.
 */
export function resolveDeepAgentModel(
  featureDefault: string = CAMBRIDGE_PLAN_MODEL,
): string {
  const resolved = resolveOpenAiModel(featureDefault);
  return resolved.includes(':') ? resolved : `openai:${resolved}`;
}

/**
 * Absolute path to the prototype skills directory (cambridge-curriculum).
 */
export function getDeepAgentSkillsDir(): string {
  // cwd-relative so the path works under Jest, Next, and `npx tsx` without __dirname ESM issues.
  return path.join(process.cwd(), 'lib/ai-analysis/deep-agents/skills');
}

/**
 * Build the exam→plan deep agent (filesystem + skills + structured plan output).
 *
 * The `extract_exam_weaknesses` tool reuses the existing single-shot exam
 * analyzer so Zod validation stays consistent with production.
 *
 * @param options - Optional model override and injected weakness extractor.
 */
export async function createExamToPlanDeepAgent(options?: {
  model?: string;
  /** Injected for tests; defaults to analyzeExamText. */
  extractWeaknesses?: (
    examText: string,
    studentName?: string,
  ) => Promise<string[]>;
}) {
  const model = options?.model ?? resolveDeepAgentModel();
  const extractWeaknesses =
    options?.extractWeaknesses ??
    (async (examText: string, studentName?: string) => {
      const report = await analyzeExamText(examText, { studentName });
      return report.weakAreas.length > 0
        ? report.weakAreas
        : report.knowledgePoints.slice(0, 5);
    });

  const extractExamWeaknesses = tool(
    async ({ examText, studentName }: { examText: string; studentName?: string }) => {
      const weaknesses = await extractWeaknesses(examText, studentName);
      return JSON.stringify({ weaknesses });
    },
    {
      name: 'extract_exam_weaknesses',
      description:
        'Extract weak areas from exam OCR/PDF text. Call this before drafting lessons.',
      schema: z.object({
        examText: z.string().describe('Full or truncated exam text'),
        studentName: z.string().optional(),
      }),
    },
  );

  return createDeepAgent({
    model,
    tools: [extractExamWeaknesses],
    skills: [getDeepAgentSkillsDir()],
    responseFormat: providerStrategy(cambridgeTeachingPlanSchema),
    systemPrompt: `You coordinate exam remediation for a tutoring center.
1. Call extract_exam_weaknesses on the exam text.
2. Activate the cambridge-curriculum skill when planning lessons.
3. Return a structured Cambridge teaching plan (exactly 10 concise lessons).
Keep objectives/activities short to limit completion tokens.`,
  });
}

/**
 * Run the deep-agent exam→plan path and log latency under feature deep_agent_exam_to_plan.
 *
 * When OPENAI_API_KEY is unset and allowMock is true, returns a deterministic mock plan
 * (same as the production Cambridge mock) without invoking Deep Agents.
 *
 * @param input - Exam text and curriculum context.
 * @param options - Mock policy and optional agent factory override (tests).
 */
export async function runExamToPlanWithDeepAgent(
  input: ExamToPlanInput,
  options?: {
    allowMockWithoutApiKey?: boolean;
    createAgent?: typeof createExamToPlanDeepAgent;
  },
): Promise<ExamToPlanDeepAgentResult> {
  const examText = input.examText.trim();
  if (!examText) {
    throw new Error('Exam text is required');
  }

  const allowMock = options?.allowMockWithoutApiKey !== false;
  const hasApiKey = Boolean(process.env.OPENAI_API_KEY);
  const curriculum = input.curriculum ?? 'IGCSE';
  const subject = input.subject?.trim() || 'Mathematics';
  const model = resolveDeepAgentModel();

  if (!hasApiKey && allowMock) {
    const startedAtMs = Date.now();
    const plan = buildMockCambridgeTeachingPlan({
      weaknesses: ['General review'],
      curriculum,
      subject,
      studentName: input.studentName,
    });
    const latencyMs = Date.now() - startedAtMs;
    logAiUsage('deep_agent_exam_to_plan', model, startedAtMs, null);
    return {
      plan,
      weaknesses: plan.weaknesses,
      model,
      latencyMs,
    };
  }

  if (!hasApiKey) {
    throw new Error('OPENAI_API_KEY is not configured');
  }

  const createAgent = options?.createAgent ?? createExamToPlanDeepAgent;
  const startedAtMs = Date.now();
  const agent = await createAgent({ model });

  const result = await agent.invoke({
    messages: [
      {
        role: 'user',
        content: [
          `Student: ${input.studentName?.trim() || 'Unknown'}`,
          `Curriculum: ${curriculum}`,
          `Subject: ${subject}`,
          '',
          'Exam text:',
          examText,
          '',
          'Extract weaknesses, then produce the Cambridge teaching plan JSON.',
        ].join('\n'),
      },
    ],
  });

  const latencyMs = Date.now() - startedAtMs;
  logAiUsage('deep_agent_exam_to_plan', model, startedAtMs, null);

  const structured = (result as { structuredResponse?: unknown }).structuredResponse;
  if (!structured) {
    throw new Error('Deep agent did not return structuredResponse');
  }

  const plan = cambridgeTeachingPlanSchema.parse(structured);
  return {
    plan,
    weaknesses: plan.weaknesses,
    model,
    latencyMs,
  };
}
