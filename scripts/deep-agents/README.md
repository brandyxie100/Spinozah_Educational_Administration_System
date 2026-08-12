# Deep Agents exam→plan prototype

Lab script for the Spinozah Deep Agents roadmap. **Not production.**

## What it does

- Builds a `createDeepAgent` coordinator with:
  - `extract_exam_weaknesses` tool (wraps production `analyzeExamText`)
  - `cambridge-curriculum` skill ([SKILL.md](../../lib/ai-analysis/deep-agents/skills/cambridge-curriculum/SKILL.md))
  - Zod `responseFormat` matching Cambridge teaching plans
- Optionally compares latency/shape against the baseline two-shot chain (`analyzeExamText` → `generateCambridgeTeachingPlan`)

## Commands

```bash
# Mock path (no API key) — verifies wiring
npx tsx scripts/deep-agents/run-exam-to-plan-prototype.ts --mock

# Live deep-agent run
npx tsx scripts/deep-agents/run-exam-to-plan-prototype.ts

# Live baseline vs deep agent comparison (logs [ai-usage] + [ai-compare])
npx tsx scripts/deep-agents/run-exam-to-plan-prototype.ts --compare
```

Optional LangSmith:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=lsv2_...
export LANGCHAIN_PROJECT=spinozah-ai-education
```

## Reading results

Expect the deep-agent path to use **more** tokens on short sample exams (harness + multi-turn). Wins appear when exam text is large and skills/subagent isolation avoid re-sending the full document every turn—see [docs/08-deep-agents-context-engineering.md](../../docs/08-deep-agents-context-engineering.md).
