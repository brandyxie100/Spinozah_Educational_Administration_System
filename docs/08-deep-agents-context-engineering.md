# Deep Agents Context Engineering Notes (Spinozah)

Notes from Deep Agents context features, mapped to a *future* Spinozah tutoring pipeline—not the current single-shot analyzers.

## Mechanisms that reduce wasted context

| Mechanism | What it does | Future Spinozah use |
|-----------|--------------|---------------------|
| **Skills progressive disclosure** | Load skill frontmatter at start; full body only when relevant | Cambridge curriculum / marking rubrics as skills instead of stuffing every system prompt |
| **Context offloading** | Large tool I/O (default ~20k tokens) → virtual FS refs + preview | Store full OCR/PDF text as a file; agent reads slices via `read_file` |
| **Summarization** | Compress older history near ~85% of context window | Multi-turn tutor chat / long plan refinement sessions |
| **Subagent isolation** | Heavy work in isolated windows; parent gets compact result | Weakness extraction vs lesson planning vs pathway ranking in parallel |
| **Prompt caching** | Cache static system/memory/skills (mainly Anthropic/Bedrock) | Lower priority while defaulting to OpenAI `gpt-4o-mini` |

## Cost tradeoff

More model calls (coordinator + subagents) raise latency and per-request API cost. Use Deep Agents when quality needs tools/isolation; otherwise Phase 1 truncation/`max_tokens` on single-shot calls is cheaper.

See [multi-agent performance comparison](https://docs.langchain.com/oss/javascript/langchain/multi-agent/index#performance-comparison).

## Candidate orchestrated pipeline

```text
Coordinator (createDeepAgent)
  ├─ WeaknessSubagent  → compact JSON weaknesses
  ├─ Curriculum skill / RAG → compact topic refs
  └─ PlanSubagent → structured 10-lesson plan (responseFormat)
       → persist via FastAPI /api/v1/analyses
```

Prototype: `scripts/deep-agents/exam-to-plan-prototype.ts` (compare tokens vs current exam + plan two-shot chain).

## Lab checklist

1. Install: `npm install deepagents langchain @langchain/core`
2. Run JS [quickstart](https://docs.langchain.com/oss/javascript/deepagents/quickstart)
3. Trace with [LangSmith](https://docs.langchain.com/langsmith/observability-quickstart)
4. Compare total tokens vs `analyzeExamText` single-shot

## References

- [Context engineering](https://docs.langchain.com/oss/javascript/deepagents/context-engineering)
- [Skills](https://docs.langchain.com/oss/javascript/deepagents/skills)
- [Subagents](https://docs.langchain.com/oss/javascript/deepagents/subagents)
