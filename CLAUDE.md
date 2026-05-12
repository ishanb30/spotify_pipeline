Project: spotify_pipeline

## Note on This File
This CLAUDE.md currently contains substantial detail about the 6-week pre-build learning period. Once building begins, that content will be largely removed and replaced with project-specific context — architecture decisions, technical standards, constraints, and living memory relevant to the build itself.

## Project Summary
This is the main data engineering project to be built after a 6-week self-study learning period (May–June 2026). It is not a learning exercise — it is a production-quality project built using the stack learned during that period:
- **Snowflake** — cloud data warehouse (storage and compute)
- **dbt Core** — transformations (project located in `transform/` subdirectory)
- **Python** — orchestration (no Airflow/Dagster)
- **Requests** — API ingestion

API: **Spotify Web API** selected. Using Authorization Code Flow (OAuth 2.0) targeting user data — specifically recently played tracks (`user-read-recently-played` scope). Pagination to be covered in Week 2.

## Pre-Build: 6-Week Learning Period
Before building begins, there is a 6-week self-study period (30 hrs/week) targeting ~50-70% competency on each tool. Claude Code in this project will be used for learning check-ins during this period. The BI Dev rotation (starting early-to-mid June 2026) will compound Snowflake knowledge.

### Learning Goals

**Tools:**
- Requests module — API ingestion patterns, auth, pagination, retry logic
- Snowflake — architecture, object hierarchy, ingestion, RBAC, Python connector
- dbt Core — models, ref/source, materializations, tests, documentation, incremental models, snapshots

**DE Theory (front-loaded in weeks 1–3):**
- Idempotency implementation patterns (beyond truncate+load: MERGE, watermarking, delete+insert)
- Watermarking — tracking pipeline state across runs
- Late-arriving data and backfilling
- Schema evolution
- SCD Type 1/2/3 tradeoffs
- Data quality testing philosophy (completeness, freshness, uniqueness, referential integrity)
- DAG concept and lineage
- Full refresh vs incremental (conceptual before dbt)
- Pipeline-level retry logic (which failures are safe to retry vs not)

**Professional completeness goal:** Build a mental checklist of what belongs in a production pipeline before starting to build — logging, run logs, validation, observability, testing, documentation, error handling, idempotency, lineage. Know this upfront, not mid-build.

### Week-by-Week Plan

**Week 1 — Requests foundations + Snowflake setup + ingestion theory**

*Tools:*
- Requests: HTTP fundamentals, first authenticated API call, parsing JSON responses
- Snowflake: Trial account setup, UI, virtual warehouse concept, object hierarchy (account → database → schema → table), basic SQL

*DE Theory:*
- API ingestion patterns: batch vs polling vs event-driven — what each means and when you'd choose one
- Watermarking: what it is, why pipelines need to track state, why truncate+load doesn't need it but incremental ingestion does

*End-of-week milestone:* Authenticated API call working and response parsed cleanly. Snowflake account set up, virtual warehouse concept understood, basic SQL running. Can explain watermarking and why it exists.

---

**Week 2 — Requests depth + Snowflake architecture + idempotency patterns**

*Tools:*
- Requests: Pagination (cursor-based and offset-based), OAuth token handling, retry logic with exponential backoff, structuring ingestion as a clean reusable function not a script
- Snowflake: Stages (internal and external), COPY INTO, file formats, RBAC (roles, users, privileges), micro-partitions concept

*DE Theory:*
- Idempotency implementation patterns: when truncate+load breaks down, MERGE/UPSERT, delete+insert, tradeoffs of each
- Late-arriving data: what it is, why it's a problem, how pipeline design accommodates it
- Schema evolution: writing ingestion code that doesn't break when the source changes

*End-of-week milestone:* Production-style ingestion function — authenticated, paginated, with retry logic and clean error handling. Can explain the COPY INTO flow and what a stage is. Can explain three idempotency patterns and when to use each.

---

**Week 3 — Snowflake deepening + pre-dbt concepts + professional completeness**

*Tools:*
- Snowflake: Python connector, time travel, zero-copy cloning, performance basics (clustering keys, query profile)
- Light orientation to dbt project structure — what files exist and what they do — without writing models yet

*DE Theory:*
- DAG: what it is, how dbt uses it to express model dependencies, why it's better than sequential scripts
- Full refresh vs incremental: conceptual tradeoff — cost, reliability, complexity
- SCD Type 1 vs 2 vs 3: understand the full spectrum, not just Type 2
- Data quality testing philosophy: completeness, freshness, uniqueness, referential integrity — what each catches and which layer it belongs to
- Backfilling: why reprocessing historical data is harder than it looks, what makes a pipeline backfill-friendly
- Pipeline-level retry logic: which failures are safe to retry (idempotent steps) vs not (steps with side effects that may have partially executed)

*Professional completeness:* Formalise the mental checklist — what belongs in a production pipeline that beginners skip. By end of week, can recite and justify each item unprompted.

*End-of-week milestone:* Python connected to Snowflake. dbt project structure understood before opening it. Production pipeline checklist internalised. Ready to write dbt models.

---

**Week 4 — dbt Core foundations**

*Tools:*
- dbt project structure: `dbt_project.yml`, `profiles.yml`, directory layout (models/, tests/, seeds/, snapshots/, macros/)
- What a model is: a SELECT statement materialised by dbt
- Materializations: view vs table vs incremental vs ephemeral — when to use each
- `ref()` and `source()`: what they do, why they create the DAG, why you never hardcode schema names
- Running dbt: `dbt run`, `dbt test`, `dbt docs generate`, `dbt docs serve`
- Staging → intermediate → mart layer pattern and why it exists

*DE Theory:*
- Lineage in practice: run `dbt docs serve` and read the DAG — connect it to the concept from week 3
- Materialisation tradeoffs: no storage cost vs query speed vs incremental complexity

*End-of-week milestone:* dbt connected to Snowflake. Staging, intermediate, and mart models written using `ref()`. Can run dbt, read the output, and explain why `ref()` matters. Can justify the staging → intermediate → mart structure.

---

**Week 5 — dbt Core depth**

*Tools:*
- dbt tests: built-in (unique, not_null, accepted_values, relationships), singular tests for custom checks
- dbt documentation: column and model descriptions, doc blocks
- Incremental models in depth: `is_incremental()`, `unique_key`, incremental strategies (append, merge, delete+insert) — connected back to week 2 theory
- dbt snapshots: SCD Type 2 in dbt (connects to prior SQL implementation)
- Jinja basics: variables, macros, `if` blocks — enough to write a reusable macro
- Source freshness checks

*DE Theory:*
- Testing strategy: testing code correctness (Python unit tests) vs testing data quality (dbt tests) — where each belongs and why both are needed
- Documentation as code: why docs outside the codebase rot

*End-of-week milestone:* Complete dbt project with tested, documented models. Singular test written for a custom data quality rule. Incremental model implemented with justified strategy choice. dbt snapshot connected to prior SCD Type 2 understanding.

---

**Week 6 — Synthesis + architecture review + project planning prep**

No new tools. Integration and judgment.
- Walk the full stack end-to-end: Requests → Snowflake → dbt → Python orchestration. Responsibilities of each component and where the seams are.
- Architecture decisions: when to use dbt incremental vs Snowflake Streams, how to structure a dbt project at scale, where Python orchestration fits without Airflow/Dagster
- Professional completeness applied to this stack specifically
- Testing synthesis: Python unit tests + dbt tests + integration tests — what to test at each layer
- Observability: logging, run tracking, validation — how these translate to this stack
- Project planning: what decisions need to be made before writing a line of code, what you'd regret not knowing

*End-of-week milestone:* Can walk through the full architecture and justify every design decision. Ready for the project planning session — whiteboard, not blank slate.

---

## Outstanding Setup Tasks
1. **Update `~/.dbt/profiles.yml`** — all fields currently set to `placeholder`. Replace with real Snowflake credentials once trial is active.

## Learning Protocol
I am learning by doing. **DO NOT provide code solutions unless explicitly requested with the phrase "Provide a code solution for [X]."**

- **Conceptual explanation:** Explain the WHY behind patterns and best practices
- **Socratic method:** Ask guiding questions to help me arrive at the solution
- **Problem identification:** Point out issues and let me implement the fix
- **Terminal/setup tasks:** Guide with commands to type — do not run them. I execute all commands myself.

## Teaching Mindset
- Never give answers or skip over why things happen — I must arrive at the answer at least 80% of the time
- After completing a hard concept, ask questions to cement understanding before moving on
- Test understanding proactively — not just whether I can do something, but whether I know why
- Test me by questioning my thought process even if I am correct — decisions must be backed by reasoning, not just intuition
- When I check in on progress, probe uncertain areas before moving on. Do not assume understanding — verify it.

## Explanation Style
- **Never assume I know what a technical word means in context.** When introducing any term an average non-developer might not understand in a technical context (e.g. "port", "redirect", "request", "endpoint", "browser" in a networking context), define it inline the first time it appears.
- After a technical noun, add a brief parenthetical or follow-on sentence explaining what it is in plain terms before continuing.
- Do this the first time a term appears in an explanation, not every time.
- I understand general concepts but not their precise technical meaning — explain the technical usage specifically.

## Project Structure
```
spotify_pipeline/
  .venv/            — isolated Python environment (never committed)
  .gitignore
  transform/        — dbt project (all dbt commands run from inside here)
  src/              — Python orchestration scripts (created when needed)
```

## Living Memory
- **Current state:** Week 1 complete (started 2026-05-05). Theory complete. Snowflake trial active. API chosen: Spotify Web API. Project renamed to `spotify_pipeline`.
- **dbt commands:** Must be run from inside `transform/`.
- **Competency benchmark:** ~50-70% means a working mental model of the architecture, confident implementation, awareness of gotchas, knowing there's more but not being blocked.
- **Known gap:** retry logic not yet added to `token_manager.py` — noted for project build stage.
- **Project-stage endpoints to consider:** `top-tracks`, `top-artists`, `audio-features` — adds depth for dbt modelling.
- **Project-stage infrastructure:** watermark/run log table needed in Snowflake — write `played_at` timestamp per pipeline run.

## Week 1 Progress

### Theory (complete)
- Ingestion patterns (batch vs polling vs event-driven) — solid. Spotify pipeline uses batch.
- Watermarking — solid. Pipeline stores one timestamp per run, anchored to external data timestamp not pipeline run time, lives in a run log/watermark table.
- OAuth Authorization Code Flow understood end-to-end. Took significant drilling — revisit if needed.
- Bearer vs Basic auth distinction understood.
- Defensive coding mindset — contract/boundary thinking applied in practice.

### Snowflake (complete)
- UI navigated, virtual warehouse concept understood.
- Object hierarchy understood (account → database → schema → table).
- Created database, schema, and table. Basic SQL running.

### Practical
- `src/auth.py` — complete. One-time OAuth flow, saves tokens to `src/tokens.json`.
- `src/token_manager.py` — production-grade defensive refactor complete (atomic writes, boundary validation, error handling, 60s expiry buffer). **Revisit:** retry logic, logging, module-level credential loading on import (testability issue).
- `src/tokens.json` — written by auth.py, never committed. Contains access_token, refresh_token, expires_at.
- `src/fetch.py` — complete. Authenticated GET with retry logic (429, 5xx, network errors), exponential backoff + jitter, `Retry-After` header handling, response validation at boundary. Type hints added.
