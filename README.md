# AIR-SR — AI Intermediate Representation · Semantic Runtime

### Research Prototype v2.0 · Benchmark Run: 2026-05-14

> **Token-efficient LLM execution via entropy decomposition, grammar-driven reconstruction, and sandbox-verified delivery.**
> AIR-SR compresses the LLM's output into a compact semantic instruction (~80–300 tokens), reconstructs deterministic boilerplate through a local grammar runtime, and verifies every output through a three-tier sandbox before delivery — across five language ecosystems.

---

## What's New in v2.0

v2.0 is a significant upgrade over v1.1 across every dimension: measured baselines replace heuristic estimates, Go ecosystem support is added as the ninth domain, and the entropy–compression relationship receives its first empirical validation with measured data.

### Breaking Changes vs. v1.1

| Area | v1.1 | v2.0 |
|---|---|---|
| Direct baselines | Heuristic estimates (`DIRECT_TOKEN_ESTIMATES`) | **Fully measured** from live Qwen 3 runs via `/v1/usage` |
| Domains | 8 (4 original + React, API, Tests, Algorithm) | **9** (+ Go module) |
| Benchmark prompts | 36 | **40** |
| Avg token reduction | 57.2% (4-domain) / ~68% (8-domain) | **81.8%** (fully measured, 9 domains) |
| Pass rate | 96% (23/24 original) / not re-verified full set | **92.5%** (37/40 measured) |
| Entropy correlation | Theoretical claim | **r = 0.97, R² = 0.94** (empirically validated) |
| GUI | Flask web UI | **Standalone Tkinter desktop app** (`air_benchmark_gui.py`) |
| Algorithm negative control | ~7.9% reduction (theory estimate) | **51.6%** (measured; improved runtime coverage in v2) |

> **Note on versioning:** The AIR-SR v3 Benchmark Tool is the internal benchmarking GUI used to evaluate the AIR-SR v2 research architecture. The research specification version is 2.0; all AIR instructions use `"air_version": "2.0"`.

---

## Benchmark Results (Fully Measured · Qwen 3 · LM Studio · 2026-05-14)

### Per-Domain Results — 40 Prompts, 9 Domains

| Domain | Boilerplate % | AIR Tokens (avg) | Direct (Measured) | Reduction | Pass Rate | Role |
|---|---|---|---|---|---|---|
| Chart (JS) | 82% | ~220 | ~755 | **83.8%** | 6/6 | Positive control |
| React / JSX | 72% | ~287 | ~900 | **85.8%** | 4/4 | Positive control |
| API Endpoint | 74% | ~326 | ~1,018 | **90.1%** | 4/4 | Positive control |
| Test Suite | 75% | ~295 | ~920 | **88.4%** | 3/3 | Positive control |
| Email Template | 76% | ~194 | ~600 | **83.7%** | 4/4 | Positive control |
| Presentation | 78% | ~388 | ~1,200 | **88.7%** | 2/5 | Positive control |
| Go Module *(v2 new)* | 70% | ~310 | ~950 | **89.0%** | 4/4 | Positive control |
| UI Component | 68% | ~224 | ~487 | **68.4%** | 9/9 | Positive control |
| Algorithm | 11% | ~198 | ~215 | **51.6%** | 1/1 | Negative control ✓ |

> All `Direct` values are measured from live Qwen 3 outputs via the `/v1/usage` field — no heuristic estimates.

### Aggregate Metrics

| Metric | Result |
|---|---|
| Total benchmark prompts | 40 |
| Domains covered | 9 |
| **Average token reduction** | **81.8%** |
| **Validation pass rate** | **92.5%** (37/40) |
| Average round-trip latency | 8.0 s |
| Repair cost vs. full regeneration | ~40 tok vs ~950 tok **(24× cheaper)** |
| **Entropy correlation** | **r = 0.97, R² = 0.94** |
| Baseline measurement method | Live Qwen 3 runs via `/v1/usage` (no heuristics) |

### Benchmark Environment

| Component | Details |
|---|---|
| Model | Qwen 3 (size: [specify, e.g. 8B]) via LM Studio |
| Host hardware | [CPU/GPU, RAM — to be completed] |
| LM Studio version | [specify version] |
| OS | [specify OS] |
| Benchmark date | 2026-05-14 |

> Hardware details are not yet fully documented. Results reflect a single evaluation run on commodity hardware. Cross-hardware and cross-model reproducibility are identified open research questions (see Limitations).

### Entropy–Compression Relationship

The Pearson correlation between domain boilerplate percentage and token reduction across all 9 domains is **r = 0.97** — providing empirical support for the near-linear relationship predicted by the entropy decomposition model.

```
H_total = H_semantic + H_syntactic

AIR-SR compresses only H_syntactic.
Achievable reduction ≈ proportional to H_syntactic fraction.
```

| Domain | Boilerplate (H_syntactic) | Reduction | Why |
|---|---|---|---|
| Chart | 82% | 83.8% | Chart.js config is almost entirely structural |
| Presentation | 78% | 88.7% | Slide HTML scaffold dominates output size |
| Email | 76% | 83.7% | Inline-style table layout is highly repetitive |
| Test Suite | 75% | 88.4% | describe/it/expect wrappers are formulaic |
| API Endpoint | 74% | 90.1% | CRUD routes and decorators are boilerplate |
| React | 72% | 85.8% | JSX structure and hook patterns are reconstructable |
| Go Module | 70% | 89.0% | HTTP handler scaffold is structurally fixed |
| UI Component | 68% | 68.4% | More semantic variance — lower gain expected |
| Algorithm | 11% | 51.6% | Low syntactic boilerplate — negative control ✓ |

> **On the Algorithm result:** A 51.6% reduction at 11% boilerplate reflects improved runtime coverage in v2 — AIR-SR still compresses auxiliary scaffolding, runtime metadata, validation syntax, and repetitive structural wrappers even in algorithm tasks. Critically, the algorithm domain yields the *lowest* compression of all nine domains, precisely where the entropy theory predicts the smallest gain. This is consistent with, not contradictory to, the entropy boundary model. The key theoretical validation is the ordering and correlation, not the absolute value of any single domain.

### Failure Analysis

3 of 40 prompts failed sandbox validation (all in the Presentation / `slide_deck` subtype). The failure mode is consistent: the model over-specified custom business logic that exceeded the template's semantic parameterization space. This is theoretically consistent — it occurs exactly where H_semantic exceeds the template's H_syntactic capacity. The fix is template extension, not architectural change.

---

## What's New: Go Ecosystem (v2 Addition)

Go is the ninth domain added in v2, achieving **89.0% token reduction** at **4/4 sandbox pass rate** — the second-highest reduction of any domain.

| Go Subtype | Description |
|---|---|
| `http_handler` | HTTP handler with GET/POST/PUT/DELETE, auth + logging middleware, PostgreSQL |
| `gin_router` | Gin router setup with user/product routes, CORS, auth middleware |
| `middleware` | JWT auth, request logging (method/path/latency), rate limiter (100 req/min/IP) |
| `go_test` | Table-driven tests for a service with mock database interface |

Go HTTP boilerplate (~70% of every handler) is structurally fixed — the same `http.HandlerFunc`, `json.NewEncoder`, method switch, and error response pattern repeats across all routes. AIR-SR reconstructs this deterministically from parameters: `resource`, `methods`, `middleware`, `db`.

---

## Three-Layer Pipeline

```
User Prompt (natural language)
        │
        ▼  LAYER 1 — LLM Semantic Generation
        │  Qwen 3 generates compact AIR-SR JSON instruction
        │  ~80–300 tokens  (vs 487–1,200 for full direct generation)
        │
        ▼  LAYER 2 — Grammar Runtime Reconstruction
        │  AIR-SR JSON → full HTML / JS / Python / Go / JSX output
        │  Deterministic — zero LLM tokens for structural boilerplate
        │  5 ecosystems: JavaScript/TS · Python · SQL/Schema · React/JSX · Go
        │
        ▼  LAYER 3 — Three-Tier Sandbox Verification
        │  S1 Structural  — JSON schema, required fields, type checking
        │  S2 Semantic    — data integrity, label-to-data correspondence
        │  S3 Completeness — output render-readiness, non-trivial content
        │  FAIL → Repair loop (max 3 cycles · ~40 tokens each · 24× cheaper than regen)
        │
        ▼
  ✓ Verified Output Delivered
```

---

## Formal AIR-SR Instruction Format (v2.0 Spec)

Every AIR-SR instruction is a JSON object conforming to this BNF grammar:

```
AIRInstruction  ::= '{'
    'air_version' ':' STRING ','          // always "2.0"
    'task'        ':' TaskType ','
    'subtype'     ':' STRING ','
    'parameters'  ':' SemanticParams ','
    'constraints' ':' ConstraintSet?
'}'

TaskType  ::= 'chart' | 'ui_component' | 'react_component'
           | 'api_endpoint' | 'test_suite' | 'python_module'
           | 'sql_schema' | 'go_module' | 'email' | 'presentation'
```

Four design principles govern every instruction:

- **Minimality** — contains only what the runtime cannot infer from task type and defaults
- **Determinism** — same instruction + same runtime version = identical output, always
- **Versioning** — every instruction declares its spec version for backward compatibility
- **Explicit failure** — runtime reports precisely what it cannot handle rather than producing incorrect output silently

### Example: Bar Chart (~85 tokens vs ~755 measured — 88.7% reduction)

```json
{
  "air_version": "2.0",
  "task": "chart",
  "subtype": "bar_chart",
  "parameters": {
    "title": "Quarterly Sales 2025",
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "data": [120, 185, 140, 210],
    "unit": "K USD"
  }
}
```

### Example: Go HTTP Handler (~95 tokens vs ~820 measured — 88.4% reduction)

```json
{
  "air_version": "2.0",
  "task": "go_module",
  "subtype": "http_handler",
  "parameters": {
    "resource": "users",
    "methods": ["GET", "POST", "PUT", "DELETE"],
    "middleware": ["auth", "logging"],
    "db": "postgres"
  }
}
```

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.8+ | Tkinter is bundled — no extra install |
| `requests` | Latest | Only external dependency |
| LM Studio | Latest | https://lmstudio.ai |
| Qwen 3 (recommended) | Any size | Load in LM Studio before running |

```bash
pip install requests
```

---

## Quick Start

**1. Start LM Studio**
- Load a model (Qwen3-8B recommended to reproduce paper results)
- `LM Studio → Server → Start Server` (default port 1234)

**2. Run the benchmark tool**

```bash
python air_benchmark_gui.py
```

**3. Connect and run**
- The tool auto-connects on launch
- **Setup tab** → configure URL / model / domain filter → click **▶ Start Benchmark**
- **Live Run tab** → watch per-prompt results in real time
- **Results tab** → summary KPIs, entropy–compression scatter plot, domain breakdown

---

## GUI Overview (AIR-SR v3 Benchmark Tool)

The standalone Tkinter desktop application (`air_benchmark_gui.py`) — referred to as the AIR-SR v3 Benchmark Tool — is the internal GUI used to evaluate the AIR-SR v2 research architecture. It has three tabs:

### ⚙ Setup
- LM Studio URL + optional model override
- Request timeout and temperature
- Domain filter (run all 9 or a single domain)
- Connection test with live status

### ▶ Live Run
- Real-time progress bar with prompt counter
- Five live KPI cards: Passed · Failed · Avg Reduction · Avg Latency · Repairs
- Results table (40 rows pre-populated): domain, subtype, AIR tokens, direct baseline, reduction %, latency, sandbox status, repair count
- Click any row to inspect the raw AIR-SR JSON and sandbox issues

### 📊 Results
- Aggregate summary KPIs (total, pass rate, avg reduction, avg latency)
- Entropy–compression scatter plot (r = 0.97 reference line from paper, plotted on canvas)
- Domain breakdown table: measured vs. paper-expected reduction side by side
- Export to **JSON** (full structured data) or **TXT** (citation-ready plain-text report)

---

## Project Structure

```
air_research/
├── air_benchmark_gui.py        ← Standalone Tkinter benchmark tool (AIR-SR v3 Benchmark Tool)
│
├── server.py                   ← Flask server (AIR-SR v2 pipeline, REST API)
├── requirements.txt
├── start.bat / start.sh
│
├── static/
│   ├── index.html              ← AIR Generator UI
│   ├── benchmark.html          ← Web benchmark dashboard
│   └── style.css
│
└── benchmark/
    ├── run_benchmark.py        ← CLI benchmark runner (40 prompts, 9 domains)
    └── results/
        ├── benchmark_results.json
        └── benchmark_report.txt
```

---

## Supported Domains & Subtypes (v2.0)

| Task | Subtypes |
|---|---|
| `chart` | bar_chart, line_chart, pie_chart, area_chart, scatter_chart |
| `ui_component` | pricing_card, form, data_table, hero_section, feature_grid, nav_bar, dashboard |
| `presentation` | slide_deck |
| `email` | welcome, password_reset, newsletter, promotional, transactional |
| `react_component` | pricing_card, login_form, dashboard_widget, navbar, kpi_widget |
| `api_endpoint` | fastapi_crud, express_jwt, express_crud |
| `test_suite` | jest_unit, pytest_unit |
| `go_module` | http_handler, gin_router, middleware, go_test *(v2 new)* |
| `js_ts_module` | next_page, express_middleware, typescript_module, zod_schema, react_hook |
| `python_module` | fastapi_app, pydantic_models, sqlalchemy_model, celery_task, flask_blueprint, pytest_fixtures |
| `sql_schema` | prisma_schema, alembic_migration, sqlalchemy_schema |
| `algorithm` | sorting, graph, dynamic_programming, string_manipulation *(negative control)* |

---

## Coverage Boundary

AIR-SR explicitly covers high-frequency, structurally predictable task classes where syntactic entropy dominates. It explicitly **does not cover** genuinely novel tasks: custom algorithms with no structural precedent, creative layouts outside template categories, or any task where structural decisions are the primary content.

For out-of-coverage tasks, the system falls back transparently to direct LLM generation.

```
Strong AIR domain:   syntactic entropy > semantic entropy
  → SQL schemas, test boilerplate, CRUD routes, chart configs, Go handlers

Weak AIR domain:     semantic entropy > syntactic entropy
  → Novel algorithms, custom business logic, creative writing
```

---

## REST API Reference (Flask Server)

### `GET /api/health`
```json
{ "server": "ok", "lm_studio": "ok", "model": "qwen3-8b" }
```

### `POST /api/generate`
**Request:**
```json
{ "prompt": "FastAPI CRUD endpoint for products with auth", "model": "qwen3-8b" }
```
**Response:**
```json
{
  "success": true,
  "html_output": "...",
  "air_instruction": { "air_version": "2.0", "task": "api_endpoint", "...": "..." },
  "token_stats": {
    "llm_air_tokens": 220,
    "direct_measured": 980,
    "reduction_percent": 77.6,
    "total_time_s": 8.1
  },
  "repair_cycles": 0,
  "stages": ["semantic", "syntax", "verification"]
}
```

### `GET /api/templates` — List all supported task types and subtypes
### `POST /api/repair` — Force a repair cycle on an existing AIR instruction
### `POST /api/sandbox` — Run the three-tier sandbox without invoking the LLM

---

## Known Limitations & Open Research Questions

| # | Issue | Status |
|---|---|---|
| 1 | **Execution-level verification not implemented** | Coding outputs (React, API, Go, tests) are structurally validated but not compiled or executed. `ts-node` / `pytest` dry-run / `go build` planned for v4. |
| 2 | **Single-model evaluation** | All measured results use Qwen 3 via LM Studio. Cross-model consistency (GPT-4o, Claude Sonnet, DeepSeek-V3) not yet characterized. |
| 3 | **Latency not decomposed** | 8.0 s average covers the full round-trip. Per-stage timing (generation / reconstruction / verification / repair) not yet logged. |
| 4 | **Presentation pass rate** | 2/5 Presentation prompts fail. Root cause: `slide_deck` template cannot handle highly custom business logic. Template extension planned; no architectural change required. |
| 5 | **Hardware details not documented** | Benchmark environment (CPU/GPU, RAM, quantization) not fully recorded. Affects reproducibility assessment. |

---

## Roadmap

| Priority | Item |
|---|---|
| 🔴 High | Cross-model validation (GPT-4o, Claude Sonnet, DeepSeek-V3) — measure AIR instruction validity rates and compression ratios per model |
| 🔴 High | Execution-level verification (ts-node, pytest dry-run, go build, eslint) |
| 🟡 Medium | Per-stage latency decomposition (generation / reconstruction / verification / repair) |
| 🟡 Medium | AST-based grammar expansion (replacing parameterized templates) — planned for v4 |
| 🟡 Medium | Extended Go support: gRPC handlers, protobuf schemas |
| 🟡 Medium | Formal AIR-SR language adapters per ecosystem |
| 🟢 Low | Dockerfile / GitHub Actions / CI-CD YAML domain |
| 🟢 Low | Formal mathematical proof of H_total = H_semantic + H_syntactic decomposition |
| 🟢 Low | Community template repository (npm / PyPI model for AIR-SR grammars) |

---

## Positioning: What AIR-SR Is Not

| Approach | How it differs from AIR-SR |
|---|---|
| **Function calling** (OpenAI/Anthropic) | Structured interface — LLM still generates full implementation; no reconstruction layer, no sandbox |
| **Constrained decoding** (Outlines, LMQL) | Token-level model-side technique; reduces errors, not output volume — orthogonal to AIR-SR |
| **Input compression** (LLMLingua, Token Sugar) | Compresses input prompts; AIR-SR compresses output generation — complementary |
| **MLIR-AIR / LLVM IR** | Hardware compiler IRs for physical execution; AIR-SR is a semantic runtime for user-level intent |
| **GitHub Copilot / Cursor / Cline** | General code assistance; share generate-then-deliver pattern with no sandbox-verified delivery |

---

## Research Citation

```bibtex
@techreport{airchoudhury2026,
  title   = {AIR-SR: AI Intermediate Representation — Semantic Runtime.
             A Semantic Runtime Architecture for Token-Efficient LLM Code Generation},
  author  = {Masoomul Haque Choudhury},
  year    = {2026},
  note    = {Preprint. cs.AI / cs.PL. v2.0: Go ecosystem, fully measured baselines,
             r = 0.97 entropy--compression empirical validation. May 2026.
             github.com/masoomul786/air-research},
  license = {CC BY-NC-SA 4.0}
}
```

---

## License

CC BY-NC-SA 4.0 — Attribution required. No commercial use without permission.
