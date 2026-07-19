# Non-Goals

This document lists what the flagship build will **not** attempt in the 12-week scope.
Saying no preserves depth for Python, Java, TypeScript, and JavaScript and keeps cost at zero until a short demo window.

## Language and analysis

- Compiler-level static analysis for any language
- Full LSP / language-server parity
- Accurate call graphs for generic languages
- Complete symbol resolution outside the deep set
- Inheritance graphs as a promise for Python/TS (best-effort only; Java is the inheritance flagship)
- Framework-complete support (detect common patterns only: FastAPI, Express, Spring, React, etc.)
- Deep parsers for C, C++, C#, Go, Rust, Ruby, PHP, Kotlin, Swift, Scala in v1
- Binary, media, or proprietary format intelligence
- Guaranteed correctness on obfuscated, generated, or minified code

## Repository import

- Private repository import in the initial public demo path
- Arbitrary git hosts beyond GitHub HTTPS (unless explicitly added later)
- Submodule checkout in v1
- Installing dependencies from the imported repository
- Executing build/test scripts from the imported repository
- Unlimited repository size or file count

## Infrastructure

- Paid Redis
- Paid managed PostgreSQL for the demo
- Virtual machines
- Kubernetes / AKS
- Always-on cloud replicas (min replicas must be 0)
- Multi-region production HA
- Long-lived production deployment after Week 12

## Product features deferred / out of scope

- Multi-tenant SaaS billing and org administration
- Real-time collaborative editing
- IDE plugins (VS Code / JetBrains) in the flagship window
- Automatic PR review bots
- Writing or committing code back to GitHub
- Fine-tuning custom embedding or LLM models
- Guaranteeing incremental indexing on day one of Week 11 if time-boxed (full re-index remains acceptable fallback)

## AI claims we will not make

- “Hallucination-free” answers without citations
- Treating heuristic sections as verified symbols
- Claiming deep intelligence for generic languages in marketing copy
- Unrestricted public AI Q&A without auth or caps

## Cost non-goals

- Building a permanently hosted free public instance
- Spending more than the intended $10 temporary cloud budget
- Keeping Azure or paid AI keys alive after the demo recording

## Related contracts

- Language honesty: [language-support.md](./language-support.md)
- Cost ceiling: [deployment/cost-policy.md](./deployment/cost-policy.md)
- Requirements: [product-requirements.md](./product-requirements.md)
