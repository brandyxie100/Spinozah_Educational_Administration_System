# Deep Agents Decision Guide (Spinozah)

This guide captures when to use OpenAI single-shot calls, LangChain `createAgent`, or Deep Agents `createDeepAgent` in this repo.

## Stack layers

| Layer | Product | Role |
|-------|---------|------|
| **Framework** | LangChain | Models, tools, agent loop, structured output |
| **Runtime** | LangGraph | Durable execution, streaming, HITL, persistence |
| **Harness** | Deep Agents SDK | Filesystem, subagents, planning, context offloading, skills |

Deep Agents builds on LangGraph and adds batteries-included context management. It is not a drop-in replacement for a single Chat Completions call.

## Decision rule (use this every time)

1. **One input → one structured JSON, no tools** → keep the OpenAI SDK (current `lib/ai-analysis/*` pattern) or a LangChain chat model with structured output. **Do not use Deep Agents.**
2. **Few tool calls, short session** → LangChain `createAgent`.
3. **Long task, large tool I/O, parallel specialists, memory/skills** → Deep Agents `createDeepAgent`.

### Spinozah mapping today

| Feature | Pattern | Verdict |
|---------|---------|---------|
| Exam analysis | Single-shot JSON | Stay on OpenAI SDK |
| Essay analysis | Single-shot JSON | Stay on OpenAI SDK |
| Cambridge plan | Single-shot JSON | Stay on OpenAI SDK |
| University pathway | Single-shot JSON (small input) | Stay on OpenAI SDK |
| Future exam → curriculum → plan orchestration | Multi-step + large text + specialists | Deep Agents candidate |

## Why Deep Agents does not cut tokens for single-shot flows

Wrapping exam/essay/plan/pathway in `createDeepAgent` adds:

- Extra system guidance for filesystem / task tools
- Often multiple model turns (plan → act → summarize)
- Subagent overhead when misused for trivial work

Deep Agents token wins come from **long runs**: offloading large tool results, summarizing history, loading skills on demand, and isolating heavy work in subagents that return compact results.

## Prefer JS Deep Agents here

Generation lives in the Next.js BFF (`app/api/ai/*`, `lib/ai-analysis/`). Prefer `deepagents` + `langchain` (JavaScript) over a Python-only harness unless AI moves to FastAPI workers.

## References

- [Runtimes, frameworks, and harnesses](https://docs.langchain.com/oss/javascript/concepts/products)
- [Deep Agents overview](https://docs.langchain.com/oss/javascript/deepagents/overview)
- [LangChain agents](https://docs.langchain.com/oss/javascript/langchain/agents)
- [Structured output](https://docs.langchain.com/oss/javascript/langchain/structured-output)
- [Context engineering notes (Spinozah)](./08-deep-agents-context-engineering.md)
- [Exam→plan lab script](../scripts/deep-agents/README.md)
