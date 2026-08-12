/**
 * Compare the production two-shot exam→plan chain against the Deep Agents prototype.
 */

import { analyzeExamText } from '../analyzer';
import { generateCambridgeTeachingPlan } from '../cambridge-plan-analyzer';
import type { CambridgeTeachingPlan } from '../cambridge-plan-schema';
import { logAiUsage } from '../usage-logger';
import {
  runExamToPlanWithDeepAgent,
  type ExamToPlanInput,
} from './exam-to-plan-orchestrator';

export interface PathComparisonResult {
  path: 'baseline' | 'deep_agent';
  latencyMs: number;
  lessonCount: number;
  weaknessCount: number;
  planSummary: string;
  plan: CambridgeTeachingPlan;
}

export interface ExamToPlanComparison {
  baseline: PathComparisonResult;
  deepAgent: PathComparisonResult;
  winnerByLatency: 'baseline' | 'deep_agent' | 'tie';
  notes: string[];
}

/**
 * Run baseline (analyzeExamText + generateCambridgeTeachingPlan) then deep agent.
 *
 * Usage for each OpenAI call is logged by the underlying analyzers / orchestrator.
 * This helper adds a summary line for easy CLI comparison.
 *
 * @param input - Shared exam text and curriculum context.
 */
export async function compareExamToPlanApproaches(
  input: ExamToPlanInput,
): Promise<ExamToPlanComparison> {
  const baselineStarted = Date.now();
  const examReport = await analyzeExamText(input.examText, {
    studentName: input.studentName,
  });
  const weaknesses =
    examReport.weakAreas.length > 0
      ? examReport.weakAreas
      : examReport.knowledgePoints.slice(0, 5);
  const baselinePlan = await generateCambridgeTeachingPlan(weaknesses, {
    studentName: input.studentName ?? examReport.studentName,
    curriculum: input.curriculum,
    subject: input.subject ?? examReport.subject,
  });
  const baselineLatency = Date.now() - baselineStarted;

  const deep = await runExamToPlanWithDeepAgent(input, {
    allowMockWithoutApiKey: false,
  });

  const baseline: PathComparisonResult = {
    path: 'baseline',
    latencyMs: baselineLatency,
    lessonCount: baselinePlan.lessons.length,
    weaknessCount: baselinePlan.weaknesses.length,
    planSummary: baselinePlan.summary,
    plan: baselinePlan,
  };

  const deepAgent: PathComparisonResult = {
    path: 'deep_agent',
    latencyMs: deep.latencyMs,
    lessonCount: deep.plan.lessons.length,
    weaknessCount: deep.weaknesses.length,
    planSummary: deep.plan.summary,
    plan: deep.plan,
  };

  const delta = Math.abs(baseline.latencyMs - deepAgent.latencyMs);
  const winnerByLatency =
    delta < 50
      ? 'tie'
      : baseline.latencyMs < deepAgent.latencyMs
        ? 'baseline'
        : 'deep_agent';

  const notes = [
    'Baseline uses two single-shot OpenAI calls (exam + plan).',
    'Deep Agents adds harness overhead (tools/skills/turns); expect higher tokens unless exam text is huge and offloaded.',
    'Inspect [ai-usage] log lines and LangSmith traces for token totals.',
  ];

  console.info(
    '[ai-compare]',
    JSON.stringify({
      feature: 'exam_to_plan_compare',
      baselineLatencyMs: baseline.latencyMs,
      deepAgentLatencyMs: deepAgent.latencyMs,
      winnerByLatency,
    }),
  );

  // Aggregate marker (no token fields — those are per-call in analyzer logs).
  logAiUsage('deep_agent_exam_to_plan', deep.model, Date.now() - deep.latencyMs, null);

  return { baseline, deepAgent, winnerByLatency, notes };
}
