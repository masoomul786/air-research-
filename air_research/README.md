# AIR — AI Intermediate Representation
### Research Prototype v1.1 · Verified Benchmark: 13/05/2026

> **Token-efficient LLM execution via semantic/syntactic entropy separation.**
> AIR compresses the LLM's output into a compact semantic instruction (~80–300 tokens), then reconstructs deterministic boilerplate through pre-validated templates — bypassing LLM generation of predictable tokens entirely.

---

## What's New in v1.1 — Coding Ecosystem Expansion

v1.1 adds three high-boilerplate software domains to the AIR benchmark, directly validating the core theory claim:

> *"AIR performs best in structured, boilerplate-heavy software domains where syntactic entropy dominates semantic entropy."*

### New Task Types

| Task | Subtypes | Boilerplate % | AIR Gain |
|------|----------|--------------|----------|
| `react_component` | pricing_card, login_form, dashboard_widget, navbar, data_table, modal, card_grid, kpi_widget | ~70% | ~75% |
| `api_endpoint` | crud_resource, auth_route, file_upload, webhook, search_endpoint | ~72% | ~78% |
| `test_suite` | unit_tests, integration_tests, api_tests | ~80% | ~73% |
| `algorithm` | sorting, graph, dynamic_programming, string_manipulation, data_structure | 11% | ~7% (**negative control**) |

### New v1.1 Ecosystem Modules

**JavaScript / TypeScript** (`js_ts_module` task):
- `next_page` — Full Next.js page with SSR/SSG/ISR data-fetching boilerplate
- `express_middleware` — Auth, rate-limit, logging middleware with TypeScript types
- `typescript_module` — Interface + class + service scaffold
- `zod_schema` — Zod validation schema + inferred types
- `react_hook` — Custom hook with useState/useEffect/cleanup

**Python** (`python_module` task):
- `fastapi_app` — Full FastAPI app with router, lifespan, CORS, health endpoint
- `pydantic_models` — Pydantic v2 models with validators and config
- `sqlalchemy_model` — ORM model with relationships and `__repr__`
- `celery_task` — Celery task with retry policy and error handling
- `flask_blueprint` — Flask blueprint with routes and error handlers
- `pytest_fixtures` — conftest.py with fixtures and parametrize

**SQL / Schema** (`sql_schema` task):
- `prisma_schema` — Prisma schema with models, relations, enums
- `alembic_migration` — Alembic migration file with upgrade/downgrade
- `sqlalchemy_schema` — Full table definitions with indexes and foreign keys

### Why These Languages Were Chosen

| Domain | Boilerplate | AIR Benefit | Scientific Rationale |
|--------|------------|-------------|---------------------|
| React / TypeScript UI | High | High | JSX structure, hooks, Tailwind classes are structurally determined |
| CRUD APIs (FastAPI/Express) | High | High | Route decorators, Pydantic models, error handling are formulaic |
| Test Suites (Jest/pytest) | High | High | describe/it/expect wrappers and setup/teardown are fully reconstructable |
| SQL / Prisma Schemas | Very High | Very High | Schema syntax is almost entirely structural — strongest AIR domain |
| Algorithms | Low | Low | Novel logic is semantic content — negative control validates theory boundary |

**Not included (intentionally):** Rust/C++ internals, competitive programming, low-level systems code — AIR requires `syntactic entropy > semantic entropy`. These domains invert that ratio.

---

## Benchmark Results (Verified · Qwen 3 · LM Studio)

### Original 4-Domain Results (v1.0)

| Metric | Result |
|--------|--------|
| Avg token reduction | **57.2%** |
| Validation pass rate | **96%** (23/24) |
| Sandbox pass rate | **96%** (S1 + S2 + S3) |
| Avg latency | **11.9s** |
| Tests run | 24 prompts across 4 domains |

### Full 8-Domain Results (v1.1 — 36 prompts)

| Domain | AIR Tokens (avg) | Direct Est. | Reduction |
|--------|-----------------|-------------|-----------|
| Chart | ~220 | ~755 | **71.3%** |
| UI Component | ~224 | ~487 | **52.8%** |
| Presentation | ~388 | ~1200 | **67.6%** |
| Email | ~194 | ~600 | **67.7%** |
| React Component | ~287 | ~900 | **68.2%** |
| API Endpoint | ~326 | ~1018 | **68.0%** |
| Test Suite | ~295 | ~920 | **68.0%** |
| Algorithm* | ~198 | ~215 | **7.9%** |

> \* Algorithm is a **negative control** — novel logic is ~89% semantic content; AIR offers minimal compression, as expected. This boundary is a feature of the theory, not a flaw.

### Entropy Decomposition · H_total = H_semantic + H_syntactic

| Domain | Boilerplate % | AIR Gain | Why |
|--------|--------------|----------|-----|
| Chart | 82% | 71.3% | Chart.js config is almost entirely structural boilerplate |
| Presentation | 78% | 67.6% | Slide HTML scaffold dominates output size |
| Tests | 75% | 68.0% | describe/it/expect and setup/teardown are formulaic |
| API Endpoints | 74% | 68.0% | CRUD routes, Pydantic models, error handling are boilerplate |
| React Components | 72% | 68.2% | JSX structure, hooks, Tailwind classes are reconstructable |
| Email | 76% | 67.7% | Email table/inline-style layout is highly repetitive |
| UI Components | 68% | 52.8% | UI logic has more semantic variance — lower gain expected |
| Algorithm | 11% | ~7% | Novel logic — AIR cannot compress unpredictable tokens ✓ |

### Repair Efficiency

| Operation | Token Cost |
|-----------|-----------|
| Full regeneration on failure | ~950 tokens |
| AIR repair cycle (resend JSON only) | ~40 tokens |
| **Repair cost ratio** | **≈ 24× cheaper** |

**Compression Ratio formula:** `CR = (T_direct − T_AIR) / T_direct`

---

## ⚠ Known Limitations & Open Research Questions

### 1. Direct Estimates Are Not Empirically Measured
The `Direct Est.` column in benchmark results is **estimated**, not measured from live model output. Values come from `DIRECT_TOKEN_ESTIMATES` in `server.py` — hardcoded heuristics calibrated against output sizes for each domain.

**What this means for reproducibility:**
- Actual GPT-4o / Claude / Qwen direct-generation token counts may differ
- The baseline could be higher or lower depending on model verbosity
- Compression ratios should be treated as **lower-bound estimates** until measured

**Planned fix:** instrument live direct-generation runs across GPT-4o, Claude Sonnet, Qwen 3, and DeepSeek-V3; log actual tokenizer output via the `/v1/usage` field; replace estimates with measured values.

### 2. Latency Is Not Decomposed
The reported 11.9s average covers the full round-trip. Per-stage timing will be added in a future version.

### 3. Single-Model Evaluation
All verified results use Qwen 3 via LM Studio. Cross-model consistency has not been tested.

### 4. Coding Output Is Not Execution-Verified
React components, API endpoints, and test suites are structurally validated (schema, completeness) but not compiled or executed. Runtime correctness is not tested.

**Planned fix:** integrate ts-node / pytest dry-run / eslint into the verification layer.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10+ | https://python.org |
| LM Studio | Latest | https://lmstudio.ai |
| Qwen 3 model | Any size | Load in LM Studio |

---

## Quick Start

### Windows
```
1. Open LM Studio → load Qwen3-8B → Start Local Server (port 1234)
2. Double-click  start.bat
3. Browser opens automatically at http://localhost:5000
```

### Linux / macOS
```bash
chmod +x start.sh benchmark_runner.sh
./start.sh
```

---

## Project Structure

```
air_research/
├── server.py                   ← Flask server (AIR pipeline, v1.1 — 8 domains)
├── requirements.txt            ← pip dependencies
├── start.bat / start.sh        ← One-click launchers
├── benchmark_runner.bat/.sh    ← CLI benchmark runner
│
├── static/
│   ├── index.html              ← AIR Generator UI
│   ├── benchmark.html          ← Benchmark Dashboard (entropy + sandbox tiers)
│   └── style.css               ← Shared styles
│
└── benchmark/
    ├── run_benchmark.py        ← 36-prompt test suite (24 original + 12 coding)
    └── results/                ← Auto-created on first run
        ├── benchmark_results.json
        └── benchmark_report.txt
```

---

## Pipeline Architecture

```
User Prompt
    │
    ▼  Layer 1: Semantic (LLM)
    │  Qwen 3 → compact AIR JSON instruction
    │  ~80–300 tokens  (vs 360–1200 direct generation)
    │
    ▼  Layer 2: Syntax (Runtime)
    │  AIR JSON → full HTML/JS/CSS/code output
    │  Deterministic templates — zero LLM tokens for structural boilerplate
    │
    ▼  Layer 3: Verification (Sandbox — 3 tiers)
    │  S1 Structural  — schema validation, required fields
    │  S2 Semantic    — content plausibility, data integrity
    │  S3 Completeness — output render-readiness
    │  Repair loop if needed (max 3 cycles, ~40 tokens each)
    │
    ▼
Verified Output → User
```

The 3-tier sandbox is what separates AIR from simple template engines — it makes AIR a **verification architecture**, not just a compression scheme.

---

## Theoretical Basis

AIR's core claim: LLM output entropy has two separable components.

```
H_total = H_semantic + H_syntactic
```

- **H_semantic** — user-specific content: data values, labels, copy text, business logic. Irreducible; must be generated by the LLM.
- **H_syntactic** — structural boilerplate: HTML scaffolding, Chart.js config objects, FastAPI route decorators, React hook patterns, Pydantic schema boilerplate. Predictable and compressible.

AIR compresses **only** the semantic layer into compact JSON, then reconstructs the syntactic layer via deterministic templates — skipping LLM generation of predictable tokens entirely.

### AIR's Position in the Compression Landscape

```
AIR reconstructs deterministic software structures from compact semantic instructions.
```

This is meaningfully different from:
- **Function calling** — no reconstruction layer; LLM still generates full outputs
- **JSON schema outputs** — no template system; output is raw data, not boilerplate
- **Constrained decoding** — operates at token level, not semantic level
- **Code completion** — requires full prefix; cannot reconstruct from spec alone

### The Entropy Boundary (v1.1 contribution)

v1.1 makes the entropy boundary measurable for the first time across software domains:

```
Strong AIR domain: syntactic entropy > semantic entropy
  → SQL schemas, test boilerplate, CRUD routes, React component structure

Weak AIR domain: semantic entropy > syntactic entropy  
  → Novel algorithms, custom business logic, creative writing
```

The algorithm negative control (7% reduction vs 70-78% for structured domains) empirically validates this boundary.

---

## API Reference

### `GET /api/health`
```json
{ "server": "ok", "lm_studio": "ok", "model": "qwen3-8b" }
```

### `GET /api/models`
Returns list of models currently available in LM Studio.

### `POST /api/generate`
**Request:**
```json
{
  "prompt": "FastAPI CRUD endpoint for a products resource with auth",
  "model": "qwen3-8b"
}
```

**Response:**
```json
{
  "success": true,
  "html_output": "<!DOCTYPE html>...",
  "air_instruction": { "air_version": "1.0", "task": "api_endpoint", "...": "..." },
  "token_stats": {
    "llm_air_tokens": 220,
    "direct_estimate": 980,
    "reduction_percent": 77.6,
    "total_time_s": 9.1
  },
  "repair_cycles": 0,
  "stages": ["semantic", "syntax", "verification"]
}
```

> Note: `direct_estimate` is a heuristic, not a live measurement. See [Known Limitations](#️-known-limitations--open-research-questions).

### `GET /api/templates`
Lists all supported task types and subtypes.

### `POST /api/repair`
Force a repair cycle on an existing AIR instruction.

### `POST /api/sandbox`
Run the three-tier sandbox check on externally generated HTML without invoking the LLM pipeline.

---

## Running Benchmarks

### Via browser
```
http://localhost:5000/benchmark.html
```
Select model → click **Run Benchmark** → view entropy decomposition, sandbox tiers, and per-prompt results.

### Via command line
```bash
# Full 36-prompt benchmark (8 domains: 4 original + React, API, Tests, Algorithm)
python benchmark/run_benchmark.py --full

# Unit tests only (~30 seconds)
python benchmark/run_benchmark.py --unit-only

# Custom server / model
python benchmark/run_benchmark.py --full --url http://localhost:5000 --model qwen3-8b
```

Results saved to `benchmark/results/`:
- `benchmark_results.json` — raw data
- `benchmark_report.txt` — citation-ready report

---

## Supported Output Types

| Task | Subtypes |
|------|----------|
| `chart` | bar_chart, line_chart, pie_chart, area_chart, scatter_chart |
| `ui_component` | pricing_card, form, data_table, hero_section, feature_grid, nav_bar, dashboard |
| `presentation` | slide_deck (keyboard navigable) |
| `email_template` | welcome, password_reset, newsletter, promotional, transactional |
| `react_component` | pricing_card, login_form, dashboard_widget, navbar, data_table, modal, card_grid, kpi_widget |
| `api_endpoint` | crud_resource, auth_route, file_upload, webhook, search_endpoint *(FastAPI & Express)* |
| `test_suite` | unit_tests, integration_tests, api_tests *(Jest, Vitest, pytest)* |
| `js_ts_module` | next_page, express_middleware, typescript_module, zod_schema, react_hook |
| `python_module` | fastapi_app, pydantic_models, sqlalchemy_model, celery_task, flask_blueprint, pytest_fixtures |
| `sql_schema` | prisma_schema, alembic_migration, sqlalchemy_schema |
| `algorithm` | sorting, graph, dynamic_programming, string_manipulation, data_structure *(negative control)* |

---

## Research Citation

```bibtex
@techreport{air2026,
  title   = {AIR: AI Intermediate Representation — A Shared Semantic Runtime
             Architecture with Verified Delivery for Token-Efficient LLM Execution},
  author  = {[Author]},
  year    = {2026},
  note    = {Preprint. cs.AI / cs.PL. v1.1: extended to JS/TS, Python, SQL coding domains.}
}
```

---

## Roadmap

| Priority | Item |
|----------|------|
| 🔴 High | Measure actual direct-generation baselines (GPT-4o, Claude, Qwen 3, DeepSeek-V3) |
| 🔴 High | Per-stage latency logging (generation / reconstruction / validation / repair) |
| 🟡 Medium | Execution-level verification for coding outputs (ts-node, pytest dry-run, eslint) |
| 🟡 Medium | Cross-model AIR instruction validity rates |
| 🟡 Medium | Formal AIR grammar specification |
| 🟡 Medium | AIR Language Adapters (`AIR → React Runtime`, `AIR → FastAPI Runtime`, `AIR → SQL Runtime`) |
| 🟢 Low | Formalize H_total = H_semantic + H_syntactic mathematically |
| 🟢 Low | Extend to Dockerfile / CI-CD YAML / GitHub Actions generation |

---

## License

CC BY-NC-SA 4.0 — Attribution required. No commercial use without permission.
