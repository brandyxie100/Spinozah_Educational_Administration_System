/**
 * CLI: Deep Agents exam→plan prototype vs baseline two-shot chain.
 *
 * Usage:
 *   npx tsx scripts/deep-agents/run-exam-to-plan-prototype.ts
 *   npx tsx scripts/deep-agents/run-exam-to-plan-prototype.ts --compare
 *
 * Requires OPENAI_API_KEY for live runs. Without a key, --mock runs the mock path only.
 */

import {
  compareExamToPlanApproaches,
} from '../../lib/ai-analysis/deep-agents/compare';
import {
  runExamToPlanWithDeepAgent,
} from '../../lib/ai-analysis/deep-agents/exam-to-plan-orchestrator';

const SAMPLE_EXAM = `
Mathematics IGCSE Paper — Student: Sample Student
Q1 (Algebra): Solve 2x + 5 = 17. Student wrote x = 5. Incorrect; should be x = 6.
Q2 (Fractions): Simplify 3/4 + 1/6. Student wrote 4/10. Incorrect common denominator.
Q3 (Geometry): Find area of triangle base 6 height 4. Student wrote 24. Missed 1/2.
Total: 1/3.
`.trim();

async function main(): Promise<void> {
  const args = new Set(process.argv.slice(2));
  const compare = args.has('--compare');
  const forceMock = args.has('--mock');

  if (forceMock) {
    delete process.env.OPENAI_API_KEY;
  }

  const input = {
    examText: SAMPLE_EXAM,
    studentName: 'Sample Student',
    curriculum: 'IGCSE' as const,
    subject: 'Mathematics',
  };

  if (compare) {
    if (!process.env.OPENAI_API_KEY) {
      console.error(
        'OPENAI_API_KEY is required for --compare (live baseline + deep agent).',
      );
      process.exit(1);
    }
    const result = await compareExamToPlanApproaches(input);
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const result = await runExamToPlanWithDeepAgent(input, {
    allowMockWithoutApiKey: true,
  });
  console.log(
    JSON.stringify(
      {
        model: result.model,
        latencyMs: result.latencyMs,
        weaknesses: result.weaknesses,
        lessonCount: result.plan.lessons.length,
        summary: result.plan.summary,
      },
      null,
      2,
    ),
  );
}

main().catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
