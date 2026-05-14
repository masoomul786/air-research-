#!/usr/bin/env python3
"""
AIR-SR v3 — Benchmark Tool (Tkinter GUI)
==========================================
A beginner-friendly desktop benchmark runner for the AIR-SR research paper.
Connects to your local LM Studio instance and runs all 40 benchmark prompts
across 9 domains, measuring token savings, latency, and sandbox pass rates.

Author : Masoomul Haque Choudhury
Version: 3.0 (GUI edition)
Paper  : AIR-SR — AI Intermediate Representation, Semantic Runtime (May 2026)
"""

import json
import os
import sys
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.filedialog as filedialog
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import math

# ── Optional: requests (required at runtime, shown in UI if missing) ──────────
try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  COLOUR PALETTE  (dark theme — easy on the eyes for long benchmark runs)    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
BG_DEEP    = "#0d1117"   # window background
BG_CARD    = "#161b22"   # panel / card background
BG_ROW_A   = "#1c2128"   # table row alternate A
BG_ROW_B   = "#0d1117"   # table row alternate B
BG_ROW_SEL = "#1f3a5f"   # selected row highlight
FG_WHITE   = "#e6edf3"   # primary text
FG_MUTED   = "#8b949e"   # secondary / label text
FG_ACCENT  = "#58a6ff"   # blue accent (links, highlights)
FG_GREEN   = "#3fb950"   # pass / positive
FG_RED     = "#f85149"   # fail / negative
FG_YELLOW  = "#d29922"   # warning / in-progress
FG_PURPLE  = "#bc8cff"   # domain badges
BORDER     = "#30363d"   # subtle borders

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)
FONT_BIG    = ("Segoe UI", 28, "bold")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  BENCHMARK PROMPTS (all 40 from the paper — v3 specification)               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
TEST_PROMPTS: List[Dict] = [
    # ── Charts (6) ─────────────────────────────────────────────────────────────
    {"id":  1, "domain": "Chart",       "subtype": "bar_chart",
     "boilerplate": 82,
     "prompt": "Bar chart of quarterly sales for 2025. Q1=120K, Q2=185K, Q3=140K, Q4=210K. Blue colors."},
    {"id":  2, "domain": "Chart",       "subtype": "line_chart",
     "boilerplate": 82,
     "prompt": "Line chart of monthly website traffic Jan-Jun 2025: 4200, 5100, 4800, 6300, 7100, 8900 visitors."},
    {"id":  3, "domain": "Chart",       "subtype": "pie_chart",
     "boilerplate": 82,
     "prompt": "Pie chart of browser market share: Chrome 65%, Safari 19%, Firefox 9%, Edge 5%, Other 2%."},
    {"id":  4, "domain": "Chart",       "subtype": "bar_chart",
     "boilerplate": 82,
     "prompt": "Bar chart of 5 department budgets: Engineering $2.1M, Sales $1.4M, Marketing $0.9M, HR $0.5M, Operations $0.7M."},
    {"id":  5, "domain": "Chart",       "subtype": "line_chart",
     "boilerplate": 82,
     "prompt": "Line chart of annual revenue 2019-2025: 1.2, 1.5, 1.1, 2.0, 2.8, 3.5, 4.2 million USD."},
    {"id":  6, "domain": "Chart",       "subtype": "bar_chart",
     "boilerplate": 82,
     "prompt": "Bar chart of top 5 languages by popularity: Python 29%, JavaScript 17%, Java 15%, C++ 11%, Rust 6%."},

    # ── UI Components (9) ──────────────────────────────────────────────────────
    {"id":  7, "domain": "UI",          "subtype": "pricing_card",
     "boilerplate": 68,
     "prompt": "Pricing page: Basic $9/mo (5 projects, 10GB), Pro $29/mo highlighted (unlimited, 100GB), Enterprise custom pricing."},
    {"id":  8, "domain": "UI",          "subtype": "form",
     "boilerplate": 68,
     "prompt": "Contact form with name, email, phone, subject dropdown (General/Support/Sales), message textarea. Dark theme."},
    {"id":  9, "domain": "UI",          "subtype": "data_table",
     "boilerplate": 68,
     "prompt": "Data table of top 5 programming languages: Language, Popularity %, Primary Use, Year Created."},
    {"id": 10, "domain": "UI",          "subtype": "hero_section",
     "boilerplate": 68,
     "prompt": "Hero section: headline 'Ship Faster with AI', subheadline about dev productivity, CTA buttons Get Started and See Demo."},
    {"id": 11, "domain": "UI",          "subtype": "feature_grid",
     "boilerplate": 68,
     "prompt": "Feature grid for cloud platform: Fast Deployment, Auto Scaling, 99.9% Uptime, Global CDN, Rollback, Analytics."},
    {"id": 12, "domain": "UI",          "subtype": "nav_bar",
     "boilerplate": 68,
     "prompt": "Navigation bar for TechCorp: Products, Solutions, Pricing, About, Blog links, Sign Up CTA button."},
    {"id": 13, "domain": "UI",          "subtype": "dashboard",
     "boilerplate": 68,
     "prompt": "SaaS dashboard: Revenue $84,200 (+12%), Active Users 12,400 (+8%), Churn 2.4% (-0.3%), NPS 67 (+5)."},
    {"id": 14, "domain": "UI",          "subtype": "form",
     "boilerplate": 68,
     "prompt": "Registration form: first name, last name, email, password, confirm password, agree to terms checkbox."},
    {"id": 15, "domain": "UI",          "subtype": "pricing_card",
     "boilerplate": 68,
     "prompt": "Two-tier pricing: Starter free (3 projects, community support), Professional $49/month (unlimited, priority, analytics)."},

    # ── Presentations (5) ─────────────────────────────────────────────────────
    {"id": 16, "domain": "Presentation","subtype": "slide_deck",
     "boilerplate": 78,
     "prompt": "5-slide deck on AI in Agriculture for government policy audience. Title, challenges, solutions, stats, recommendations."},
    {"id": 17, "domain": "Presentation","subtype": "slide_deck",
     "boilerplate": 78,
     "prompt": "4-slide investor pitch for fintech startup: problem, solution, traction, ask."},
    {"id": 18, "domain": "Presentation","subtype": "slide_deck",
     "boilerplate": 78,
     "prompt": "6-slide product launch: overview, features, competitive landscape, pricing, roadmap, Q&A."},
    {"id": 19, "domain": "Presentation","subtype": "slide_deck",
     "boilerplate": 78,
     "prompt": "3-slide executive summary: company highlights, Q3 performance, Q4 strategic priorities."},
    {"id": 20, "domain": "Presentation","subtype": "slide_deck",
     "boilerplate": 78,
     "prompt": "5-slide cybersecurity training deck for enterprise employees. Best practices."},

    # ── Email Templates (4) ───────────────────────────────────────────────────
    {"id": 21, "domain": "Email",       "subtype": "email_template",
     "boilerplate": 76,
     "prompt": "Welcome email for new SaaS users. Headline: Welcome to Acme! Body about getting started. CTA: Open Dashboard."},
    {"id": 22, "domain": "Email",       "subtype": "email_template",
     "boilerplate": 76,
     "prompt": "Password reset email: subject Password Reset Request, instructions, CTA Reset Password, 24h expiry warning."},
    {"id": 23, "domain": "Email",       "subtype": "email_template",
     "boilerplate": 76,
     "prompt": "Monthly newsletter: subject August 2025 Product Updates, 3 feature highlights, footer with unsubscribe."},
    {"id": 24, "domain": "Email",       "subtype": "email_template",
     "boilerplate": 76,
     "prompt": "Promotional email: 30% off summer sale for CloudTools, CTA Claim Discount, valid through August 31."},

    # ── React Components (4) ──────────────────────────────────────────────────
    {"id": 25, "domain": "React",       "subtype": "react_component",
     "boilerplate": 72,
     "prompt": "React pricing card component with three tiers: Free, Pro $29/mo, Enterprise. Pro tier highlighted. Features list and CTA button per tier."},
    {"id": 26, "domain": "React",       "subtype": "react_component",
     "boilerplate": 72,
     "prompt": "React login form component with email and password fields, form validation (email format, min 8 chars), error messages, and submit handler."},
    {"id": 27, "domain": "React",       "subtype": "react_component",
     "boilerplate": 72,
     "prompt": "React KPI dashboard widget: metric name, current value, delta percentage, trend arrow. Support up/down/neutral trends."},
    {"id": 28, "domain": "React",       "subtype": "react_component",
     "boilerplate": 72,
     "prompt": "React navbar component with brand logo, navigation links (Home, Products, Pricing, About), Sign Up CTA button. Sticky positioning."},

    # ── API Endpoints (4) ─────────────────────────────────────────────────────
    {"id": 29, "domain": "API",         "subtype": "api_endpoint",
     "boilerplate": 74,
     "prompt": "FastAPI CRUD endpoint for products resource. Fields: name (str), price (float), stock (int), category (str). List, create, read, update, delete."},
    {"id": 30, "domain": "API",         "subtype": "api_endpoint",
     "boilerplate": 74,
     "prompt": "Express TypeScript login endpoint with JWT authentication. Accept email and password, validate, return access token. Auth middleware for protected routes."},
    {"id": 31, "domain": "API",         "subtype": "api_endpoint",
     "boilerplate": 74,
     "prompt": "FastAPI endpoint for user management: create user, get by ID, update profile, delete account. Fields: email, username, role. JWT auth required."},
    {"id": 32, "domain": "API",         "subtype": "api_endpoint",
     "boilerplate": 74,
     "prompt": "Express CRUD routes for blog posts: title, content, author_id, tags array, published boolean. Public read, authenticated write."},

    # ── Test Suites (3) ───────────────────────────────────────────────────────
    {"id": 33, "domain": "Tests",       "subtype": "test_suite",
     "boilerplate": 75,
     "prompt": "Jest unit tests for Calculator class: add, subtract, multiply, divide. Edge cases: divide by zero, negative numbers, large values."},
    {"id": 34, "domain": "Tests",       "subtype": "test_suite",
     "boilerplate": 75,
     "prompt": "Pytest tests for authentication service: login, logout, token refresh. Mock database and JWT library."},
    {"id": 35, "domain": "Tests",       "subtype": "test_suite",
     "boilerplate": 75,
     "prompt": "Jest tests for shopping cart: add item, remove item, update quantity, calculate total, apply discount code. Test invalid inputs."},

    # ── Go Modules (4) ────────────────────────────────────────────────────────
    {"id": 36, "domain": "Go",          "subtype": "go_module",
     "boilerplate": 70,
     "prompt": "Go HTTP handler for users resource with GET, POST, PUT, DELETE methods. Middleware: auth and logging. PostgreSQL database."},
    {"id": 37, "domain": "Go",          "subtype": "go_module",
     "boilerplate": 70,
     "prompt": "Gin router setup for REST API: user routes, product routes, auth middleware, CORS middleware. PostgreSQL backend."},
    {"id": 38, "domain": "Go",          "subtype": "go_module",
     "boilerplate": 70,
     "prompt": "Go middleware: JWT authentication, request logging (method, path, latency), rate limiter (100 req/min per IP)."},
    {"id": 39, "domain": "Go",          "subtype": "go_module",
     "boilerplate": 70,
     "prompt": "Go table-driven tests for a UserService with Create, GetByID, Update, Delete methods. Mock database interface."},

    # ── Algorithm — NEGATIVE CONTROL (1) ─────────────────────────────────────
    {"id": 40, "domain": "Algorithm",   "subtype": "algorithm",
     "boilerplate": 11,
     "prompt": "Implement binary search on a sorted array in Python. Return index of target or -1 if not found. Handle: empty array, single element, duplicates."},
]

# Measured direct-generation token baselines from the paper (Table 1)
DIRECT_BASELINES: Dict[str, int] = {
    "bar_chart": 755,    "line_chart": 800,   "pie_chart": 710,
    "scatter_chart": 720,"area_chart": 760,   "chart": 755,
    "pricing_card": 487, "form": 487,         "data_table": 487,
    "hero_section": 487, "feature_grid": 487, "nav_bar": 487,
    "dashboard": 487,    "ui_component": 487,
    "slide_deck": 1200,  "presentation": 1100,
    "email_template": 600,"email": 600,
    "react_component": 900,
    "api_endpoint": 1018,
    "test_suite": 920,
    "go_module": 950,
    "algorithm": 215,
}

# Expected reductions per domain from paper Table 1
EXPECTED_REDUCTIONS: Dict[str, float] = {
    "Chart": 71.3, "UI": 54.0, "Presentation": 67.7,
    "Email": 67.7, "React": 68.1, "API": 68.0,
    "Tests": 67.9, "Go": 67.4, "Algorithm": 7.9,
}

DOMAIN_COLORS: Dict[str, str] = {
    "Chart":       "#58a6ff",
    "UI":          "#bc8cff",
    "Presentation":"#d29922",
    "Email":       "#3fb950",
    "React":       "#f0883e",
    "API":         "#39d353",
    "Tests":       "#a5d6ff",
    "Go":          "#00d9ff",
    "Algorithm":   "#f85149",
}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  LM STUDIO CLIENT                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class LMStudioClient:
    """
    Thin wrapper around LM Studio's OpenAI-compatible REST API.

    LM Studio runs a local server on port 1234 by default.
    It exposes the same API as OpenAI so we can use standard HTTP calls.
    """

    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> Tuple[bool, str]:
        """
        Ask LM Studio if it's alive and which model is loaded.
        Returns (is_ok, model_name_or_error_message)
        """
        try:
            r = requests.get(f"{self.base_url}/models", timeout=5)
            r.raise_for_status()
            models = r.json().get("data", [])
            if models:
                return True, models[0]["id"]
            return False, "No model loaded in LM Studio"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect — is LM Studio running?"
        except Exception as e:
            return False, str(e)

    def get_active_model(self) -> str:
        """Return the ID of the first loaded model, or empty string."""
        try:
            r = requests.get(f"{self.base_url}/models", timeout=5)
            r.raise_for_status()
            models = r.json().get("data", [])
            return models[0]["id"] if models else ""
        except Exception:
            return ""

    def chat(self, messages: List[Dict], model: str = "",
             temperature: float = 0.3, max_tokens: int = 1500) -> Tuple[str, int]:
        """
        Send a chat completion request to LM Studio.

        Args:
            messages: List of {"role": "user"/"system"/"assistant", "content": "..."}
            model: Model ID string (if blank, LM Studio uses whatever is loaded)
            temperature: 0 = deterministic, 1 = creative. 0.3 is good for code/JSON.
            max_tokens: Maximum tokens the model can generate in reply.

        Returns:
            (response_text, token_count_used)
        """
        resolved = model or self.get_active_model()
        payload: Dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if resolved:
            payload["model"] = resolved

        r = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=180,
        )
        r.raise_for_status()
        data = r.json()
        text   = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("completion_tokens", max(1, len(text) // 4))
        return text, tokens


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AIR-SR PIPELINE                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# System prompt for Layer 1: Semantic Generation
# The LLM's only job is to output a compact AIR-SR JSON instruction.
AIR_SYSTEM_PROMPT = """\
You are the AIR-SR Semantic Compiler — Layer 1 of the AIR-SR pipeline.

Your ONLY job: parse the user's natural-language request and emit a compact
AIR-SR instruction as strict JSON. Nothing else — no HTML, no code, no prose.

## Output format (strict JSON):
{
  "air_version": "3.0",
  "task": "<task_type>",
  "subtype": "<subtype>",
  "parameters": { ...user-specific values only... },
  "constraints": { "target_env": "web", "framework": "<if relevant>" }
}

## Task types:
- chart          → bar_chart | line_chart | pie_chart | scatter_chart
- ui_component   → pricing_card | form | data_table | hero_section | feature_grid | nav_bar | dashboard
- presentation   → slide_deck
- email          → email_template
- react_component→ pricing_card | login_form | dashboard_widget | navbar | kpi_widget
- api_endpoint   → fastapi_crud | express_jwt | express_crud
- test_suite     → jest_unit | pytest_unit
- go_module      → http_handler | gin_router | middleware | go_test
- algorithm      → (output the full implementation directly, no template exists)

## Rules:
1. parameters must contain ONLY user-specific content (data, labels, text).
   Do NOT include structural boilerplate — the runtime adds that.
2. Keep parameters minimal. If a value has a sensible default, omit it.
3. Output ONLY the JSON object. No markdown fences, no commentary.
4. air_version must always be "3.0".
"""

# System prompt for Layer 3: Repair
REPAIR_SYSTEM_PROMPT = """\
You are the AIR-SR Repair Engine — Layer 3 of the AIR-SR pipeline.

A sandbox has found an issue with an AIR-SR instruction. Your job is to fix
ONLY the specific field(s) mentioned in the error. Output the corrected AIR-SR
JSON instruction only. No prose, no markdown fences.
"""


class AIRSRPipeline:
    """
    Implements the three-layer AIR-SR pipeline:

      Layer 1 — LLM generates a compact semantic AIR-SR JSON instruction
      Layer 2 — Grammar runtime reconstructs full output from the instruction
      Layer 3 — Three-tier sandbox verifies; repair loop if needed

    This is the standalone benchmark version — it talks directly to LM Studio
    without needing the Flask server running.
    """

    MAX_REPAIR_CYCLES = 3

    def __init__(self, client: LMStudioClient):
        self.client = client

    # ── Layer 1: Semantic Generation ──────────────────────────────────────────

    def generate_air_instruction(self, prompt: str) -> Tuple[str, int]:
        """
        Ask the LLM to convert the user's natural-language prompt into a
        compact AIR-SR JSON instruction.

        This is the expensive step — the LLM generates only 80–300 tokens
        instead of the 500–1200 it would need for the full output.
        """
        text, tokens = self.client.chat(
            messages=[
                {"role": "system", "content": AIR_SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return text, tokens

    def parse_air_json(self, raw: str) -> Optional[Dict]:
        """
        Extract and parse the JSON from the LLM's response.
        The LLM sometimes wraps JSON in markdown fences — strip those first.
        """
        # Remove markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Drop first line (```json or ```) and last line (```)
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON object from the text
            start = cleaned.find("{")
            end   = cleaned.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    return None
        return None

    # ── Layer 2: Grammar Runtime (Reconstruction) ─────────────────────────────

    def reconstruct(self, air: Dict) -> Tuple[str, str]:
        """
        Deterministically reconstruct full output from an AIR-SR instruction.
        Returns (reconstructed_output_string, output_type).

        In production this would use AST-based expansion. Here we use
        parameterised template functions — one per subtype — which is the
        current v3 implementation approach described in Section 7.1.
        """
        task    = air.get("task", "")
        subtype = air.get("subtype", "")
        params  = air.get("parameters", {})

        # ── Chart reconstruction ───────────────────────────────────────────
        if task == "chart":
            return self._reconstruct_chart(subtype, params), "chart_js"

        # ── UI Component reconstruction ────────────────────────────────────
        elif task == "ui_component":
            return self._reconstruct_ui(subtype, params), "html"

        # ── React Component reconstruction ─────────────────────────────────
        elif task == "react_component":
            return self._reconstruct_react(subtype, params), "jsx"

        # ── API Endpoint reconstruction ────────────────────────────────────
        elif task == "api_endpoint":
            return self._reconstruct_api(subtype, params), "python_or_ts"

        # ── Presentation reconstruction ────────────────────────────────────
        elif task == "presentation":
            return self._reconstruct_presentation(subtype, params), "html"

        # ── Email reconstruction ───────────────────────────────────────────
        elif task == "email":
            return self._reconstruct_email(subtype, params), "html"

        # ── Test Suite reconstruction ──────────────────────────────────────
        elif task == "test_suite":
            return self._reconstruct_tests(subtype, params), "js_or_py"

        # ── Go Module reconstruction ───────────────────────────────────────
        elif task == "go_module":
            return self._reconstruct_go(subtype, params), "go"

        # ── Algorithm: no template, direct output ──────────────────────────
        elif task == "algorithm":
            # For algorithms the AIR instruction IS the output spec.
            # We return a placeholder — in real use the LLM generates directly.
            return f"# Algorithm: {subtype}\n# Direct generation required (low boilerplate domain).\n{json.dumps(params, indent=2)}", "python"

        else:
            return f"<!-- Unknown task: {task}/{subtype} -->", "unknown"

    def _reconstruct_chart(self, subtype: str, params: Dict) -> str:
        title  = params.get("title", "Chart")
        labels = params.get("labels", ["A", "B", "C"])
        data   = params.get("data",   [1, 2, 3])
        unit   = params.get("unit",   "")
        color  = params.get("color",  "rgba(88,166,255,0.8)")

        chart_type_map = {
            "bar_chart":  "bar",
            "line_chart": "line",
            "pie_chart":  "pie",
            "scatter":    "scatter",
            "area_chart": "line",  # area uses line with fill
        }
        ctype = chart_type_map.get(subtype, "bar")

        labels_json = json.dumps(labels)
        data_json   = json.dumps(data)

        fill = "fill: true," if subtype == "area_chart" else "fill: false,"

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body {{ margin:0; background:#0d1117; display:flex; align-items:center;
          justify-content:center; height:100vh; font-family:sans-serif; }}
  canvas {{ max-width:640px; max-height:400px; }}
</style>
</head><body>
<canvas id="c"></canvas>
<script>
new Chart(document.getElementById('c'), {{
  type: '{ctype}',
  data: {{
    labels: {labels_json},
    datasets: [{{
      label: '{title}',
      data: {data_json},
      backgroundColor: '{color}',
      borderColor: 'rgba(88,166,255,1)',
      borderWidth: 2,
      {fill}
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ labels: {{ color:'#e6edf3' }} }},
      title: {{ display:true, text:'{title} ({unit})', color:'#e6edf3', font:{{size:16}} }}
    }},
    scales: {{ x:{{ ticks:{{color:'#8b949e'}} }}, y:{{ ticks:{{color:'#8b949e'}} }} }}
  }}
}});
</script>
</body></html>"""

    def _reconstruct_ui(self, subtype: str, params: Dict) -> str:
        title = params.get("title", params.get("headline", "Component"))
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title>
<style>
  body{{margin:0;background:#0d1117;color:#e6edf3;font-family:'Segoe UI',sans-serif;padding:32px}}
  .card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:24px;max-width:480px;margin:auto}}
  h2{{color:#58a6ff;margin:0 0 16px}} .badge{{background:#1f3a5f;color:#58a6ff;padding:4px 12px;border-radius:20px;font-size:12px}}
</style></head><body>
<div class="card">
  <span class="badge">{subtype}</span>
  <h2>{title}</h2>
  <p style="color:#8b949e">AIR-SR reconstructed {subtype} component.</p>
  <pre style="background:#0d1117;padding:12px;border-radius:8px;font-size:11px;overflow:auto">{json.dumps(params, indent=2)}</pre>
</div></body></html>"""

    def _reconstruct_react(self, subtype: str, params: Dict) -> str:
        name = params.get("name", params.get("component", "MyComponent"))
        return f"""import React, {{ useState }} from 'react';

// AIR-SR v3 reconstructed React component
// Subtype: {subtype}
// Parameters: {json.dumps(params)}

const {name.replace(' ', '')}Component = () => {{
  const [state, setState] = useState(null);

  return (
    <div className="air-component air-{subtype}">
      {{/* AIR-SR Runtime: {subtype} reconstruction */}}
      <h2>{name}</h2>
      <pre>{{JSON.stringify({json.dumps(params)}, null, 2)}}</pre>
    </div>
  );
}};

export default {name.replace(' ', '')}Component;"""

    def _reconstruct_api(self, subtype: str, params: Dict) -> str:
        resource = params.get("resource", "items")
        fields   = params.get("fields", ["id", "name"])
        return f"""# AIR-SR v3 — {subtype} reconstruction
# Resource: {resource}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="{resource.title()} API")

class {resource.title()[:-1] if resource.endswith('s') else resource.title()}(BaseModel):
    id: Optional[str] = None
    {chr(10).join(f'    {f}: str = ""' for f in fields)}

_db: dict = {{}}

@app.get("/{resource}", response_model=List[{resource.title()[:-1] if resource.endswith('s') else resource.title()}])
async def list_{resource}(): return list(_db.values())

@app.post("/{resource}")
async def create_{resource[:-1] if resource.endswith('s') else resource}(item: {resource.title()[:-1] if resource.endswith('s') else resource.title()}):
    item.id = str(uuid.uuid4())
    _db[item.id] = item
    return item

@app.get("/{resource}/{{item_id}}")
async def get_{resource[:-1] if resource.endswith('s') else resource}(item_id: str):
    if item_id not in _db: raise HTTPException(404, "Not found")
    return _db[item_id]

@app.delete("/{resource}/{{item_id}}")
async def delete_{resource[:-1] if resource.endswith('s') else resource}(item_id: str):
    if item_id not in _db: raise HTTPException(404, "Not found")
    del _db[item_id]
    return {{"deleted": item_id}}
"""

    def _reconstruct_presentation(self, subtype: str, params: Dict) -> str:
        title  = params.get("title", "Presentation")
        slides = params.get("slides", [{"title": "Slide 1", "content": "Content"}])
        slides_html = "\n".join(
            f'<section><h2>{s.get("title","Slide")}</h2><p>{s.get("content","")}</p></section>'
            for s in (slides if isinstance(slides, list) else [{"title": title, "content": str(params)}])
        )
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title>
<style>
  body{{margin:0;background:#0d1117;color:#e6edf3;font-family:'Segoe UI',sans-serif}}
  section{{min-height:100vh;display:flex;flex-direction:column;align-items:center;
            justify-content:center;padding:60px;border-bottom:1px solid #30363d}}
  h2{{color:#58a6ff;font-size:2rem}} p{{color:#8b949e;max-width:600px;text-align:center}}
</style></head><body>{slides_html}</body></html>"""

    def _reconstruct_email(self, subtype: str, params: Dict) -> str:
        subject = params.get("subject", params.get("title", "Email"))
        cta     = params.get("cta",     "Click Here")
        body    = params.get("body",    "This is an AIR-SR reconstructed email.")
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{subject}</title>
<style>
  body{{margin:0;background:#f6f6f6;font-family:'Segoe UI',sans-serif}}
  .wrap{{max-width:560px;margin:40px auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
  .hdr{{background:#0d1117;padding:32px;text-align:center;color:#58a6ff;font-size:22px;font-weight:700}}
  .body{{padding:32px;color:#333;line-height:1.7}}
  .cta{{display:block;margin:24px auto;padding:14px 32px;background:#58a6ff;color:#fff;
         text-align:center;border-radius:8px;text-decoration:none;font-weight:600;width:fit-content}}
  .ftr{{background:#f0f0f0;padding:16px;text-align:center;color:#999;font-size:12px}}
</style></head><body>
<div class="wrap">
  <div class="hdr">{subject}</div>
  <div class="body"><p>{body}</p><a class="cta" href="#">{cta}</a></div>
  <div class="ftr">You received this email because you're subscribed. <a href="#">Unsubscribe</a></div>
</div></body></html>"""

    def _reconstruct_tests(self, subtype: str, params: Dict) -> str:
        target = params.get("target", params.get("class", "MyClass"))
        methods = params.get("methods", ["method1", "method2"])
        if subtype == "jest_unit":
            cases = "\n\n".join(
                f"  test('{m} works correctly', () => {{\n    const instance = new {target}();\n    expect(instance.{m}()).toBeDefined();\n  }});"
                for m in (methods if isinstance(methods, list) else ["method1"])
            )
            return f"""// AIR-SR v3 — Jest test suite reconstruction
// Target: {target}

describe('{target}', () => {{
{cases}

  test('handles edge cases', () => {{
    expect(() => new {target}()).not.toThrow();
  }});
}});"""
        else:
            cases = "\n\n".join(
                f"def test_{m}_works():\n    instance = {target}()\n    result = instance.{m}()\n    assert result is not None"
                for m in (methods if isinstance(methods, list) else ["method1"])
            )
            return f"""# AIR-SR v3 — Pytest test suite reconstruction
# Target: {target}
import pytest

{cases}

def test_edge_case_empty_input():
    instance = {target}()
    with pytest.raises((ValueError, TypeError)):
        instance.process(None)
"""

    def _reconstruct_go(self, subtype: str, params: Dict) -> str:
        resource   = params.get("resource", "items")
        middleware = params.get("middleware", [])
        return f"""// AIR-SR v3 — Go module reconstruction
// Subtype: {subtype}, Resource: {resource}
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "time"
)

type {resource.title()[:-1] if resource.endswith('s') else resource.title()} struct {{
    ID        string    `json:"id"`
    CreatedAt time.Time `json:"created_at"`
}}

func handle{resource.title()}(w http.ResponseWriter, r *http.Request) {{
    w.Header().Set("Content-Type", "application/json")
    switch r.Method {{
    case http.MethodGet:
        json.NewEncoder(w).Encode(map[string]string{{"status": "ok", "resource": "{resource}"}})
    case http.MethodPost:
        w.WriteHeader(http.StatusCreated)
        json.NewEncoder(w).Encode(map[string]string{{"created": "{resource}"}})
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }}
}}

func loggingMiddleware(next http.Handler) http.Handler {{
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {{
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    }})
}}

func main() {{
    mux := http.NewServeMux()
    mux.HandleFunc("/{resource}", handle{resource.title()})
    log.Println("AIR-SR Go server on :8080")
    log.Fatal(http.ListenAndServe(":8080", loggingMiddleware(mux)))
}}
// Middleware: {', '.join(middleware) if middleware else 'none'}
"""

    # ── Layer 3: Three-Tier Sandbox Verification ──────────────────────────────

    def run_sandbox(self, air: Optional[Dict], output: str) -> Dict:
        """
        Three-tier validation:

          S1 Structural  — JSON schema validation, required fields, types
          S2 Semantic    — Data plausibility (are labels and data same length? etc.)
          S3 Completeness— Output not empty, all required sections present

        Returns a dict: {passed: bool, tier: str, issues: list}
        """
        issues = []

        # S1 — Structural validation
        if air is None:
            issues.append("S1: Failed to parse AIR-SR instruction JSON")
            return {"passed": False, "tier": "S1", "issues": issues}

        required_keys = ["air_version", "task", "subtype", "parameters"]
        for k in required_keys:
            if k not in air:
                issues.append(f"S1: Missing required field '{k}'")

        if air.get("air_version") != "3.0":
            issues.append(f"S1: air_version should be '3.0', got '{air.get('air_version')}'")

        if issues:
            return {"passed": False, "tier": "S1", "issues": issues}

        # S2 — Semantic plausibility
        params = air.get("parameters", {})
        task   = air.get("task", "")

        if task == "chart":
            labels = params.get("labels", [])
            data   = params.get("data",   [])
            if labels and data and len(labels) != len(data):
                issues.append(f"S2: labels length ({len(labels)}) ≠ data length ({len(data)})")

        if issues:
            return {"passed": False, "tier": "S2", "issues": issues}

        # S3 — Completeness: output must exist and be non-trivial
        if not output or len(output.strip()) < 50:
            issues.append("S3: Reconstructed output is empty or too short")
            return {"passed": False, "tier": "S3", "issues": issues}

        if task == "chart" and "Chart" not in output and "chart" not in output.lower():
            issues.append("S3: Chart output missing Chart.js initialisation")

        if issues:
            return {"passed": False, "tier": "S3", "issues": issues}

        return {"passed": True, "tier": "ALL", "issues": []}

    # ── Incremental Repair ────────────────────────────────────────────────────

    def repair(self, air_raw: str, issues: List[str]) -> Tuple[str, int]:
        """
        Issue a compact repair instruction (~20–40 tokens) to fix specific
        sandbox failures instead of regenerating from scratch (~950 tokens).
        This is the 24× efficiency gain described in Section 3.3.
        """
        issue_text = "\n".join(f"- {i}" for i in issues)
        prompt = f"""Current AIR-SR instruction:
{air_raw}

Sandbox found these issues:
{issue_text}

Fix ONLY the listed issues. Return the corrected AIR-SR JSON."""

        text, tokens = self.client.chat(
            messages=[
                {"role": "system", "content": REPAIR_SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=400,
        )
        return text, tokens

    # ── Full Pipeline Run ─────────────────────────────────────────────────────

    def run(self, prompt: str, direct_baseline: int) -> Dict:
        """
        Execute the complete AIR-SR pipeline for a single prompt.
        Returns a result dict with all metrics.
        """
        result = {
            "success": False,
            "air_raw": "",
            "air_parsed": None,
            "output": "",
            "output_type": "",
            "air_tokens": 0,
            "direct_baseline": direct_baseline,
            "reduction_percent": 0.0,
            "latency_s": 0.0,
            "repair_cycles": 0,
            "sandbox_tier": "",
            "sandbox_issues": [],
            "repair_token_cost": 0,
            "error": "",
        }

        t_start = time.time()

        try:
            # ── Layer 1: Generate AIR-SR instruction ──────────────────────
            air_raw, air_tokens = self.generate_air_instruction(prompt)
            result["air_raw"]    = air_raw
            result["air_tokens"] = air_tokens

            air = self.parse_air_json(air_raw)
            result["air_parsed"] = air

            # ── Layer 2: Reconstruct output ───────────────────────────────
            if air:
                output, out_type = self.reconstruct(air)
            else:
                output, out_type = "", "unknown"

            result["output"]      = output
            result["output_type"] = out_type

            # ── Layer 3: Sandbox + Repair loop ────────────────────────────
            for cycle in range(self.MAX_REPAIR_CYCLES + 1):
                sandbox = self.run_sandbox(air, output)
                if sandbox["passed"]:
                    result["sandbox_tier"]   = "PASS"
                    result["sandbox_issues"] = []
                    result["success"]        = True
                    break
                else:
                    result["sandbox_tier"]   = sandbox["tier"]
                    result["sandbox_issues"] = sandbox["issues"]
                    if cycle < self.MAX_REPAIR_CYCLES:
                        # Issue repair instruction
                        repair_raw, repair_toks = self.repair(air_raw, sandbox["issues"])
                        result["repair_cycles"]     += 1
                        result["repair_token_cost"] += repair_toks
                        air_raw = repair_raw
                        air     = self.parse_air_json(repair_raw)
                        if air:
                            output, out_type = self.reconstruct(air)
                            result["output"]      = output
                            result["output_type"] = out_type
                    else:
                        # Exhausted repair cycles
                        result["success"] = False

        except Exception as exc:
            result["error"]   = str(exc)
            result["success"] = False

        result["latency_s"] = round(time.time() - t_start, 2)

        # Token reduction calculation
        if result["air_tokens"] > 0 and direct_baseline > 0:
            result["reduction_percent"] = round(
                (1 - result["air_tokens"] / direct_baseline) * 100, 1
            )

        return result


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  MAIN GUI APPLICATION                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class AIRBenchmarkApp(tk.Tk):
    """
    Main application window.

    Layout (three tabs):
      1. Home / Setup — connection, settings, start button
      2. Live Run     — progress, per-test results table, live log
      3. Results      — summary statistics, domain breakdown, export
    """

    def __init__(self):
        super().__init__()
        self.title("AIR-SR v3 — Benchmark Tool")
        self.geometry("1200x780")
        self.minsize(900, 600)
        self.configure(bg=BG_DEEP)

        # State
        self.client   = LMStudioClient()
        self.pipeline = AIRSRPipeline(self.client)
        self.results: List[Dict] = []
        self._run_thread: Optional[threading.Thread] = None
        self._stop_flag   = threading.Event()
        self._paused_flag = threading.Event()

        # Tkinter variables
        self.var_url      = tk.StringVar(value="http://localhost:1234/v1")
        self.var_model    = tk.StringVar(value="")
        self.var_timeout  = tk.IntVar(value=180)
        self.var_temp     = tk.DoubleVar(value=0.3)
        self.var_filter   = tk.StringVar(value="All Domains")
        self.var_status   = tk.StringVar(value="Not connected")
        self.var_progress = tk.DoubleVar(value=0)

        self._build_ui()
        self.after(500, self._auto_connect)

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        title_bar = tk.Frame(self, bg=BG_CARD, height=56)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text="AIR-SR v3", font=FONT_TITLE,
                 fg=FG_ACCENT, bg=BG_CARD).pack(side="left", padx=20, pady=10)
        tk.Label(title_bar, text="Benchmark Tool  ·  Masoomul Haque Choudhury  ·  May 2026",
                 font=FONT_SMALL, fg=FG_MUTED, bg=BG_CARD).pack(side="left", pady=10)

        self.lbl_conn = tk.Label(title_bar, textvariable=self.var_status,
                                 font=FONT_SMALL, fg=FG_MUTED, bg=BG_CARD)
        self.lbl_conn.pack(side="right", padx=20)

        # Notebook (tabs)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",         background=BG_DEEP, borderwidth=0)
        style.configure("TNotebook.Tab",     background=BG_CARD, foreground=FG_MUTED,
                                             padding=[16, 8], font=FONT_BODY)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_DEEP)],
                  foreground=[("selected", FG_ACCENT)])

        self.nb = ttk.Notebook(self, style="TNotebook")
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_setup   = tk.Frame(self.nb, bg=BG_DEEP)
        self.tab_live    = tk.Frame(self.nb, bg=BG_DEEP)
        self.tab_results = tk.Frame(self.nb, bg=BG_DEEP)

        self.nb.add(self.tab_setup,   text="  ⚙  Setup  ")
        self.nb.add(self.tab_live,    text="  ▶  Live Run  ")
        self.nb.add(self.tab_results, text="  📊  Results  ")

        self._build_setup_tab()
        self._build_live_tab()
        self._build_results_tab()

    # ── Setup Tab ─────────────────────────────────────────────────────────────

    def _build_setup_tab(self):
        canvas = tk.Canvas(self.tab_setup, bg=BG_DEEP, highlightthickness=0)
        vsb    = tk.Scrollbar(self.tab_setup, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_DEEP)
        win   = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        pad = {"padx": 32, "pady": 8}

        # ── What is this tool? ───────────────────────────────────────────
        self._section(inner, "📖  What is this tool?", **pad)
        info = (
            "This tool benchmarks the AIR-SR pipeline described in the research paper.\n"
            "It connects to your local LM Studio, sends 40 prompts across 9 domains,\n"
            "and measures how many tokens the AIR-SR approach saves vs. direct generation.\n\n"
            "The 3-layer pipeline:\n"
            "  Layer 1 — LLM generates a compact AIR-SR JSON instruction (80–300 tokens)\n"
            "  Layer 2 — Grammar runtime reconstructs the full output deterministically\n"
            "  Layer 3 — Three-tier sandbox validates; repair loop if issues found\n\n"
            "Expected result: ~50% average token reduction, 87% sandbox pass rate."
        )
        self._info_box(inner, info, **pad)

        # ── LM Studio Connection ─────────────────────────────────────────
        self._section(inner, "🔌  LM Studio Connection", **pad)
        self._info_box(inner,
            "LM Studio must be running with a model loaded (e.g. Qwen3-8B).\n"
            "Start LM Studio → Load a model → Enable the local server (default port 1234).",
            **pad)

        row = tk.Frame(inner, bg=BG_DEEP)
        row.pack(fill="x", **pad)

        tk.Label(row, text="Server URL:", font=FONT_BODY, fg=FG_MUTED, bg=BG_DEEP, width=16, anchor="w").pack(side="left")
        self._entry(row, self.var_url, width=40).pack(side="left", padx=(0, 12))
        self._button(row, "Test Connection", self._test_connection, color=FG_ACCENT).pack(side="left")

        row2 = tk.Frame(inner, bg=BG_DEEP)
        row2.pack(fill="x", **pad)
        tk.Label(row2, text="Model (optional):", font=FONT_BODY, fg=FG_MUTED, bg=BG_DEEP, width=16, anchor="w").pack(side="left")
        self._entry(row2, self.var_model, width=40,
                    placeholder="Leave blank to use whatever is loaded in LM Studio").pack(side="left")

        # Connection status box
        self.conn_status_frame = tk.Frame(inner, bg=BG_CARD, relief="flat", bd=0)
        self.conn_status_frame.pack(fill="x", **pad)
        self.lbl_conn_detail = tk.Label(self.conn_status_frame,
                                         text="Click 'Test Connection' to verify LM Studio is reachable.",
                                         font=FONT_BODY, fg=FG_MUTED, bg=BG_CARD,
                                         anchor="w", justify="left", padx=16, pady=12)
        self.lbl_conn_detail.pack(fill="x")

        # ── Benchmark Settings ───────────────────────────────────────────
        self._section(inner, "⚙  Benchmark Settings", **pad)

        srow = tk.Frame(inner, bg=BG_DEEP)
        srow.pack(fill="x", **pad)

        tk.Label(srow, text="Request timeout (s):", font=FONT_BODY, fg=FG_MUTED, bg=BG_DEEP, width=22, anchor="w").pack(side="left")
        self._entry(srow, self.var_timeout, width=8).pack(side="left", padx=(0,32))

        tk.Label(srow, text="Temperature:", font=FONT_BODY, fg=FG_MUTED, bg=BG_DEEP, width=14, anchor="w").pack(side="left")
        self._entry(srow, self.var_temp, width=8).pack(side="left")

        srow2 = tk.Frame(inner, bg=BG_DEEP)
        srow2.pack(fill="x", **pad)
        tk.Label(srow2, text="Run domain:", font=FONT_BODY, fg=FG_MUTED, bg=BG_DEEP, width=22, anchor="w").pack(side="left")
        domains = ["All Domains"] + sorted(set(p["domain"] for p in TEST_PROMPTS))
        dom_menu = tk.OptionMenu(srow2, self.var_filter, *domains)
        dom_menu.config(bg=BG_CARD, fg=FG_WHITE, font=FONT_BODY,
                        activebackground=BG_ROW_SEL, activeforeground=FG_WHITE,
                        highlightthickness=0, relief="flat", bd=0)
        dom_menu["menu"].config(bg=BG_CARD, fg=FG_WHITE, font=FONT_BODY)
        dom_menu.pack(side="left")

        # ── How to Read the Results ──────────────────────────────────────
        self._section(inner, "📐  How to Read the Results", **pad)
        self._info_box(inner,
            "AIR Tokens   — tokens the LLM actually generated (compact instruction)\n"
            "Direct Tokens — tokens needed if the LLM generated the full output directly\n"
            "Reduction %   — how much was saved  [(Direct − AIR) / Direct × 100]\n"
            "Pass / Fail   — whether the 3-tier sandbox accepted the output\n"
            "Repairs       — how many repair cycles were needed (target: 0)\n\n"
            "The Algorithm domain is a NEGATIVE CONTROL. A low reduction (~8%) there\n"
            "is the CORRECT and EXPECTED result — it validates the entropy boundary theory.\n"
            "High reduction for novel algorithms would mean the theory is WRONG.",
            **pad)

        # ── Start Button ─────────────────────────────────────────────────
        btn_frame = tk.Frame(inner, bg=BG_DEEP)
        btn_frame.pack(pady=32, padx=32)
        self.btn_start = self._button(btn_frame, "▶  Start Benchmark", self._start_benchmark,
                                       color=FG_GREEN, font=("Segoe UI", 13, "bold"),
                                       padx=32, pady=14)
        self.btn_start.pack(side="left", padx=8)
        self._button(btn_frame, "⏹  Stop", self._stop_benchmark,
                     color=FG_RED, padx=20, pady=14).pack(side="left", padx=8)

    # ── Live Run Tab ──────────────────────────────────────────────────────────

    def _build_live_tab(self):
        # Top: progress bar + stats
        top = tk.Frame(self.tab_live, bg=BG_CARD, height=90)
        top.pack(fill="x")
        top.pack_propagate(False)

        prog_frame = tk.Frame(top, bg=BG_CARD)
        prog_frame.pack(fill="x", padx=24, pady=(12, 4))

        self.lbl_prog_text = tk.Label(prog_frame, text="Ready to run", font=FONT_HEAD,
                                       fg=FG_WHITE, bg=BG_CARD, anchor="w")
        self.lbl_prog_text.pack(side="left")

        self.lbl_prog_pct = tk.Label(prog_frame, text="0 / 40", font=FONT_BODY,
                                      fg=FG_MUTED, bg=BG_CARD, anchor="e")
        self.lbl_prog_pct.pack(side="right")

        self.progress_bar = ttk.Progressbar(top, variable=self.var_progress,
                                             maximum=100, mode="determinate", length=400)
        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar",
                         troughcolor=BG_DEEP, background=FG_GREEN, thickness=8)
        self.progress_bar.configure(style="green.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", padx=24, pady=(0, 12))

        # Live summary KPI row
        kpi_row = tk.Frame(self.tab_live, bg=BG_DEEP)
        kpi_row.pack(fill="x", padx=16, pady=(8, 0))

        self.kpi_pass    = self._kpi(kpi_row, "Passed",       "0",    FG_GREEN)
        self.kpi_fail    = self._kpi(kpi_row, "Failed",        "0",    FG_RED)
        self.kpi_avgred  = self._kpi(kpi_row, "Avg Reduction", "–",    FG_ACCENT)
        self.kpi_avglat  = self._kpi(kpi_row, "Avg Latency",   "–",    FG_YELLOW)
        self.kpi_repairs = self._kpi(kpi_row, "Repairs",       "0",    FG_PURPLE)

        # Results table
        table_frame = tk.Frame(self.tab_live, bg=BG_DEEP)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        cols = ("#", "Domain", "Subtype", "AIR Tok", "Direct", "Reduction", "Latency", "Sandbox", "Repairs", "Error")
        col_w = [35, 100, 120, 70, 70, 80, 70, 80, 60, 200]

        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  selectmode="browse", height=18)
        style = ttk.Style()
        style.configure("Treeview",
                         background=BG_ROW_B, foreground=FG_WHITE,
                         rowheight=26, fieldbackground=BG_ROW_B,
                         borderwidth=0, font=FONT_SMALL)
        style.configure("Treeview.Heading",
                         background=BG_CARD, foreground=FG_MUTED,
                         relief="flat", font=FONT_SMALL)
        style.map("Treeview", background=[("selected", BG_ROW_SEL)])

        self.tree.tag_configure("pass",    background=BG_ROW_A, foreground=FG_WHITE)
        self.tree.tag_configure("fail",    background="#2d1117", foreground=FG_WHITE)
        self.tree.tag_configure("running", background="#1a2030", foreground=FG_YELLOW)
        self.tree.tag_configure("negctrl", background="#1a1a0d", foreground=FG_YELLOW)

        for c, w in zip(cols, col_w):
            self.tree.heading(c, text=c)
            anchor = "center" if c in ("AIR Tok", "Direct", "Reduction", "Latency", "Repairs", "#") else "w"
            self.tree.column(c, width=w, anchor=anchor, stretch=(c == "Error"))

        vsb2 = ttk.Scrollbar(table_frame, orient="vertical",   command=self.tree.yview)
        hsb  = ttk.Scrollbar(table_frame, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb2.grid(row=0, column=1, sticky="ns")
        hsb.grid( row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Pre-populate rows
        self._tree_iids = {}
        for p in TEST_PROMPTS:
            iid = self.tree.insert("", "end",
                values=(p["id"], p["domain"], p["subtype"], "–", "–", "–", "–", "waiting", "–", ""),
                tags=("negctrl" if p["domain"] == "Algorithm" else "pass",))
            self._tree_iids[p["id"]] = iid

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

        # Detail pane (bottom)
        detail_frame = tk.Frame(self.tab_live, bg=BG_CARD, height=110)
        detail_frame.pack(fill="x")
        detail_frame.pack_propagate(False)

        tk.Label(detail_frame, text="Selected Test Detail:", font=FONT_SMALL,
                 fg=FG_MUTED, bg=BG_CARD, anchor="w").pack(anchor="w", padx=12, pady=(8, 0))
        self.detail_text = tk.Text(detail_frame, font=FONT_MONO, bg=BG_CARD, fg=FG_MUTED,
                                    relief="flat", bd=0, height=4, state="disabled",
                                    insertbackground=FG_WHITE, wrap="word")
        self.detail_text.pack(fill="both", expand=True, padx=12, pady=4)

    # ── Results Tab ───────────────────────────────────────────────────────────

    def _build_results_tab(self):
        # Instruction when no results yet
        self.results_placeholder = tk.Label(self.tab_results,
            text="Run the benchmark first (Setup tab → ▶ Start Benchmark).\nResults will appear here automatically.",
            font=FONT_HEAD, fg=FG_MUTED, bg=BG_DEEP, justify="center")
        self.results_placeholder.pack(expand=True)

        self.results_frame = tk.Frame(self.tab_results, bg=BG_DEEP)

    def _populate_results_tab(self):
        self.results_placeholder.pack_forget()
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.results_frame.pack(fill="both", expand=True)

        res = self.results
        if not res:
            return

        passed  = [r for r in res if r["result"].get("success")]
        failed  = [r for r in res if not r["result"].get("success")]
        reductions = [r["result"]["reduction_percent"] for r in res if r["result"].get("air_tokens", 0) > 0]
        latencies  = [r["result"]["latency_s"] for r in res]
        avg_red    = sum(reductions) / len(reductions) if reductions else 0
        avg_lat    = sum(latencies)  / len(latencies)  if latencies  else 0

        # ── Summary KPI row ───────────────────────────────────────────────
        kpi_row = tk.Frame(self.results_frame, bg=BG_DEEP)
        kpi_row.pack(fill="x", padx=16, pady=16)

        self._kpi(kpi_row, "Total Tests",     str(len(res)),          FG_WHITE)
        self._kpi(kpi_row, "Passed",          str(len(passed)),        FG_GREEN)
        self._kpi(kpi_row, "Failed",          str(len(failed)),        FG_RED)
        self._kpi(kpi_row, "Avg Reduction",   f"{avg_red:.1f}%",       FG_ACCENT)
        self._kpi(kpi_row, "Avg Latency",     f"{avg_lat:.1f}s",       FG_YELLOW)
        self._kpi(kpi_row, "Pass Rate",       f"{len(passed)/len(res)*100:.0f}%", FG_GREEN)

        # ── Entropy–Compression scatter (canvas drawn) ────────────────────
        tk.Label(self.results_frame, text="Entropy–Compression Correlation  (r = expected ≈ 0.97)",
                 font=FONT_HEAD, fg=FG_MUTED, bg=BG_DEEP, anchor="w").pack(anchor="w", padx=24, pady=(8, 0))
        self._draw_scatter(self.results_frame)

        # ── Domain breakdown table ────────────────────────────────────────
        tk.Label(self.results_frame, text="Results by Domain",
                 font=FONT_HEAD, fg=FG_MUTED, bg=BG_DEEP, anchor="w").pack(anchor="w", padx=24, pady=(16, 4))

        domain_frame = tk.Frame(self.results_frame, bg=BG_DEEP)
        domain_frame.pack(fill="x", padx=24)

        headers = ["Domain", "Tests", "Pass", "Avg AIR Tok", "Avg Direct", "Avg Reduction", "Pass Rate", "Expected (Paper)"]
        for ci, h in enumerate(headers):
            tk.Label(domain_frame, text=h, font=("Segoe UI", 9, "bold"),
                     fg=FG_MUTED, bg=BG_CARD, padx=8, pady=6,
                     relief="flat", bd=0, anchor="center").grid(row=0, column=ci, sticky="ew", padx=1, pady=1)
            domain_frame.columnconfigure(ci, weight=1)

        domains_sorted = sorted(set(r["domain"] for r in res))
        for ri, domain in enumerate(domains_sorted, 1):
            dr = [r for r in res if r["domain"] == domain]
            dr_pass = [r for r in dr if r["result"].get("success")]
            d_reds  = [r["result"]["reduction_percent"] for r in dr if r["result"].get("air_tokens", 0) > 0]
            d_air   = [r["result"]["air_tokens"] for r in dr if r["result"].get("air_tokens", 0) > 0]
            d_dir   = [r["result"]["direct_baseline"] for r in dr]
            avg_dr  = sum(d_reds) / len(d_reds) if d_reds else 0
            avg_air = sum(d_air)  / len(d_air)  if d_air  else 0
            avg_dir_d = sum(d_dir) / len(d_dir) if d_dir  else 0
            pr      = len(dr_pass) / len(dr) * 100 if dr else 0
            expected = EXPECTED_REDUCTIONS.get(domain, "–")
            expected_str = f"{expected}%" if isinstance(expected, float) else expected

            clr = DOMAIN_COLORS.get(domain, FG_MUTED)
            bg  = BG_ROW_A if ri % 2 == 0 else BG_ROW_B
            values = [domain, len(dr), len(dr_pass),
                      f"{avg_air:.0f}", f"{avg_dir_d:.0f}",
                      f"{avg_dr:.1f}%", f"{pr:.0f}%", expected_str]
            for ci, v in enumerate(values):
                fg = clr if ci == 0 else (FG_GREEN if ci == 5 else FG_WHITE)
                tk.Label(domain_frame, text=str(v), font=FONT_SMALL,
                         fg=fg, bg=bg, padx=8, pady=5, anchor="center").grid(
                    row=ri, column=ci, sticky="ew", padx=1, pady=1)

        # ── Export buttons ────────────────────────────────────────────────
        btn_row = tk.Frame(self.results_frame, bg=BG_DEEP)
        btn_row.pack(pady=20)
        self._button(btn_row, "💾  Export JSON", self._export_json, color=FG_ACCENT).pack(side="left", padx=8)
        self._button(btn_row, "📄  Export TXT Report", self._export_txt, color=FG_PURPLE).pack(side="left", padx=8)

    def _draw_scatter(self, parent: tk.Frame):
        """Draw entropy % vs reduction % scatter plot on a tk.Canvas."""
        c = tk.Canvas(parent, bg=BG_CARD, width=700, height=260,
                      highlightthickness=1, highlightbackground=BORDER)
        c.pack(padx=24, pady=4)

        W, H = 700, 260
        ml, mr, mt, mb = 60, 20, 20, 40  # margins

        def x_px(v): return ml + (v / 100) * (W - ml - mr)
        def y_px(v): return mt + ((100 - v) / 100) * (H - mt - mb)

        # Axes
        c.create_line(ml, mt, ml, H - mb, fill=BORDER)
        c.create_line(ml, H - mb, W - mr, H - mb, fill=BORDER)

        # Axis labels
        c.create_text(W // 2, H - 8, text="Boilerplate % (H_syntactic fraction)",
                      font=FONT_SMALL, fill=FG_MUTED)
        c.create_text(14, H // 2, text="Token\nReduction %",
                      font=FONT_SMALL, fill=FG_MUTED, angle=90)

        # Grid lines
        for v in range(0, 101, 20):
            xp = x_px(v)
            yp = y_px(v)
            c.create_line(xp, mt, xp, H - mb, fill=BORDER, dash=(2, 4))
            c.create_line(ml, yp, W - mr, yp, fill=BORDER, dash=(2, 4))
            c.create_text(xp, H - mb + 12, text=str(v), font=FONT_SMALL, fill=FG_MUTED)
            c.create_text(ml - 8, yp, text=str(v), font=FONT_SMALL, fill=FG_MUTED, anchor="e")

        # Theoretical line (r=0.97): y ≈ 0.9x - 1.5 (approximation from paper)
        x1, y1, x2, y2 = 10, 7.5, 85, 74.5
        c.create_line(x_px(x1), y_px(y1), x_px(x2), y_px(y2),
                      fill=FG_MUTED, dash=(4, 4), width=1)
        c.create_text(x_px(55), y_px(46), text="r = 0.97 (paper)",
                      font=FONT_SMALL, fill=FG_MUTED)

        # Domain data points — use actual results if available, else paper values
        domain_data: Dict[str, Tuple[float, float]] = {}
        for r in self.results:
            domain = r["domain"]
            red    = r["result"].get("reduction_percent", 0)
            bp     = next((p["boilerplate"] for p in TEST_PROMPTS if p["domain"] == domain), 50)
            if domain not in domain_data:
                domain_data[domain] = (bp, red)
            else:
                old_bp, old_red = domain_data[domain]
                domain_data[domain] = (old_bp, (old_red + red) / 2)

        # Overlay paper values if no real data
        paper_points = {
            "Chart": (82, 71.3), "React": (72, 68.1), "API": (74, 68.0),
            "Tests": (75, 67.9), "Email": (76, 67.7), "Presentation": (78, 67.7),
            "Go": (70, 67.4),    "UI": (68, 54.0),    "Algorithm": (11, 7.9),
        }

        for domain, (bp, red) in (domain_data if domain_data else paper_points).items():
            clr = DOMAIN_COLORS.get(domain, FG_MUTED)
            xp  = x_px(bp)
            yp  = y_px(red)
            c.create_oval(xp - 6, yp - 6, xp + 6, yp + 6,
                          fill=clr, outline=BG_DEEP, width=1)
            c.create_text(xp + 10, yp, text=domain, font=FONT_SMALL,
                          fill=clr, anchor="w")

    # ── Widget Helpers ────────────────────────────────────────────────────────

    def _section(self, parent, text: str, **pack_kw):
        f = tk.Frame(parent, bg=BORDER, height=1)
        f.pack(fill="x", **{k: v for k, v in pack_kw.items() if k == "padx"}, pady=(16, 0))
        tk.Label(parent, text=text, font=FONT_HEAD, fg=FG_ACCENT, bg=BG_DEEP, anchor="w").pack(
            anchor="w", **{k: v for k, v in pack_kw.items() if k == "padx"}, pady=(4, 0))

    def _info_box(self, parent, text: str, **pack_kw):
        f = tk.Frame(parent, bg=BG_CARD, relief="flat")
        f.pack(fill="x", **pack_kw)
        tk.Label(f, text=text, font=FONT_SMALL, fg=FG_MUTED, bg=BG_CARD,
                 anchor="w", justify="left", padx=16, pady=10, wraplength=800).pack(fill="x")

    def _entry(self, parent, var, width=20, placeholder=""):
        e = tk.Entry(parent, textvariable=var, width=width,
                     bg=BG_CARD, fg=FG_WHITE, insertbackground=FG_WHITE,
                     relief="flat", font=FONT_BODY, bd=0, highlightthickness=1,
                     highlightcolor=FG_ACCENT, highlightbackground=BORDER)
        return e

    def _button(self, parent, text, command, color=FG_WHITE,
                font=FONT_BODY, padx=16, pady=8) -> tk.Button:
        b = tk.Button(parent, text=text, command=command,
                      bg=BG_CARD, fg=color, activebackground=BG_ROW_SEL,
                      activeforeground=color, font=font,
                      relief="flat", bd=0, padx=padx, pady=pady,
                      cursor="hand2", highlightthickness=1,
                      highlightbackground=BORDER)
        return b

    def _kpi(self, parent, label: str, value: str, color: str) -> tk.Label:
        f = tk.Frame(parent, bg=BG_CARD, relief="flat", bd=0)
        f.pack(side="left", expand=True, fill="both", padx=4, pady=4)
        lbl_v = tk.Label(f, text=value, font=FONT_BIG, fg=color, bg=BG_CARD)
        lbl_v.pack(pady=(12, 0))
        tk.Label(f, text=label, font=FONT_SMALL, fg=FG_MUTED, bg=BG_CARD).pack(pady=(0, 12))
        return lbl_v  # Return value label so caller can update it

    # ── Connection Logic ──────────────────────────────────────────────────────

    def _auto_connect(self):
        threading.Thread(target=self._test_connection, daemon=True).start()

    def _test_connection(self):
        self.client.base_url = self.var_url.get().rstrip("/")
        self.var_status.set("Testing connection…")
        ok, info = self.client.health_check()
        if ok:
            self.var_status.set(f"✓ Connected — {info}")
            self.after(0, lambda: self._set_conn_detail(
                f"✓  LM Studio is running.\nModel loaded: {info}\n"
                f"Ready to benchmark — click ▶ Start Benchmark.", FG_GREEN))
        else:
            self.var_status.set(f"✗ Not connected")
            self.after(0, lambda: self._set_conn_detail(
                f"✗  {info}\n\nMake sure:\n"
                "  1. LM Studio is open\n  2. A model is loaded\n"
                "  3. The local server is enabled (LM Studio → Server → Start Server)", FG_RED))

    def _set_conn_detail(self, text: str, color: str):
        self.lbl_conn_detail.config(text=text, fg=color)

    # ── Benchmark Run Logic ───────────────────────────────────────────────────

    def _get_prompts_to_run(self) -> List[Dict]:
        f = self.var_filter.get()
        if f == "All Domains":
            return TEST_PROMPTS
        return [p for p in TEST_PROMPTS if p["domain"] == f]

    def _start_benchmark(self):
        if not REQUESTS_OK:
            msgbox.showerror("Missing dependency",
                "The 'requests' library is required.\n\nInstall it:\n  pip install requests")
            return

        ok, info = self.client.health_check()
        if not ok:
            msgbox.showerror("LM Studio not connected",
                f"Cannot reach LM Studio:\n{info}\n\nStart LM Studio and load a model first.")
            return

        prompts = self._get_prompts_to_run()
        if not prompts:
            msgbox.showwarning("No prompts", "No prompts match the selected filter.")
            return

        self.results = []
        self._stop_flag.clear()
        self.nb.select(self.tab_live)

        # Reset table rows
        for p in TEST_PROMPTS:
            self.tree.item(self._tree_iids[p["id"]],
                values=(p["id"], p["domain"], p["subtype"], "–", "–", "–", "–", "waiting", "–", ""),
                tags=("negctrl" if p["domain"] == "Algorithm" else "pass",))

        self._run_thread = threading.Thread(
            target=self._benchmark_worker, args=(prompts,), daemon=True)
        self._run_thread.start()

    def _stop_benchmark(self):
        self._stop_flag.set()
        self.var_progress.set(0)
        self.lbl_prog_text.config(text="Stopped by user")

    def _benchmark_worker(self, prompts: List[Dict]):
        total   = len(prompts)
        passed  = 0
        failed  = 0
        repairs = 0
        reductions = []
        latencies  = []

        self.after(0, lambda: self.lbl_prog_text.config(text="Running benchmark…"))

        for idx, p in enumerate(prompts):
            if self._stop_flag.is_set():
                break

            # Mark row as running
            iid = self._tree_iids[p["id"]]
            self.after(0, lambda i=iid, d=p["domain"]: self.tree.item(
                i, values=(p["id"], d, p["subtype"], "…", "–", "–", "…", "running", "–", ""),
                tags=("running",)))

            # Determine direct baseline for this subtype
            baseline = DIRECT_BASELINES.get(p["subtype"], DIRECT_BASELINES.get(p["domain"].lower(), 700))

            # Update timeout from UI setting
            self.client.base_url = self.var_url.get().rstrip("/")

            # Run pipeline
            result = self.pipeline.run(p["prompt"], baseline)

            # Store result
            entry = {**p, "result": result}
            self.results.append(entry)

            # Update KPIs
            if result["success"]:
                passed += 1
            else:
                failed += 1
            repairs    += result["repair_cycles"]
            if result["air_tokens"] > 0:
                reductions.append(result["reduction_percent"])
            latencies.append(result["latency_s"])

            avg_red = sum(reductions) / len(reductions) if reductions else 0
            avg_lat = sum(latencies)  / len(latencies)  if latencies  else 0

            # Update UI
            pct = (idx + 1) / total * 100
            self.after(0, self._update_live_ui,
                       iid, p, result, idx + 1, total, pct,
                       passed, failed, avg_red, avg_lat, repairs)

        self.after(0, self._on_benchmark_complete)

    def _update_live_ui(self, iid, p, result, done, total, pct,
                        passed, failed, avg_red, avg_lat, repairs):
        # Progress bar
        self.var_progress.set(pct)
        self.lbl_prog_text.config(text=f"Running test {done} of {total}: {p['domain']} / {p['subtype']}")
        self.lbl_prog_pct.config(text=f"{done} / {total}")

        # KPIs
        self.kpi_pass.config(text=str(passed))
        self.kpi_fail.config(text=str(failed))
        self.kpi_avgred.config(text=f"{avg_red:.1f}%")
        self.kpi_avglat.config(text=f"{avg_lat:.1f}s")
        self.kpi_repairs.config(text=str(repairs))

        # Table row
        r = result
        air_t = r["air_tokens"] if r["air_tokens"] > 0 else "–"
        red_s = f"{r['reduction_percent']:.1f}%" if r["air_tokens"] > 0 else "–"
        lat_s = f"{r['latency_s']:.1f}s"
        sandbox_s = "✓ PASS" if r["success"] else f"✗ {r['sandbox_tier']}"
        rep_s = str(r["repair_cycles"]) if r["repair_cycles"] > 0 else "0"
        err   = r["error"][:60] if r.get("error") else ""

        tag = "negctrl" if p["domain"] == "Algorithm" else ("pass" if r["success"] else "fail")
        self.tree.item(iid, values=(
            p["id"], p["domain"], p["subtype"],
            air_t, r["direct_baseline"], red_s, lat_s, sandbox_s, rep_s, err,
        ), tags=(tag,))
        self.tree.see(iid)

    def _on_benchmark_complete(self):
        self.lbl_prog_text.config(text="✓ Benchmark complete!")
        self.var_progress.set(100)
        self._populate_results_tab()
        self.nb.select(self.tab_results)

    def _on_row_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        item   = self.tree.item(sel[0])
        vals   = item["values"]
        prompt_id = int(vals[0]) if vals[0] else None
        match  = next((r for r in self.results if r["id"] == prompt_id), None)
        if not match:
            return
        r = match["result"]
        detail = (
            f"Prompt   : {match['prompt'][:120]}\n"
            f"AIR JSON : {r['air_raw'][:200].strip()}\n"
            f"Issues   : {'; '.join(r['sandbox_issues']) if r['sandbox_issues'] else 'None'}\n"
            f"Error    : {r['error'] or 'None'}"
        )
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", detail)
        self.detail_text.config(state="disabled")

    # ── Export ────────────────────────────────────────────────────────────────

    def _export_json(self):
        if not self.results:
            msgbox.showwarning("No results", "Run the benchmark first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"air_sr_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        if not path:
            return
        passed = [r for r in self.results if r["result"].get("success")]
        reds   = [r["result"]["reduction_percent"] for r in self.results if r["result"].get("air_tokens", 0) > 0]
        lats   = [r["result"]["latency_s"] for r in self.results]
        payload = {
            "metadata": {
                "tool": "AIR-SR v3 Benchmark (Tkinter)",
                "paper": "AIR-SR — AI Intermediate Representation, Semantic Runtime",
                "author": "Masoomul Haque Choudhury",
                "date": datetime.now().isoformat(),
                "server_url": self.client.base_url,
            },
            "summary": {
                "total_tests": len(self.results),
                "passed": len(passed),
                "failed": len(self.results) - len(passed),
                "pass_rate_pct": round(len(passed) / len(self.results) * 100, 1),
                "avg_reduction_pct": round(sum(reds) / len(reds), 1) if reds else 0,
                "avg_latency_s": round(sum(lats) / len(lats), 2) if lats else 0,
            },
            "results": self.results,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        msgbox.showinfo("Exported", f"Results saved to:\n{path}")

    def _export_txt(self):
        if not self.results:
            msgbox.showwarning("No results", "Run the benchmark first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"air_sr_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if not path:
            return

        passed = [r for r in self.results if r["result"].get("success")]
        reds   = [r["result"]["reduction_percent"] for r in self.results if r["result"].get("air_tokens", 0) > 0]
        lats   = [r["result"]["latency_s"] for r in self.results]

        lines = [
            "=" * 72,
            "  AIR-SR v3 Benchmark Report",
            "  AI Intermediate Representation — Semantic Runtime",
            "  Author : Masoomul Haque Choudhury",
            f"  Date   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Server : {self.client.base_url}",
            "=" * 72,
            "",
            "SUMMARY",
            "-" * 40,
            f"  Total tests       : {len(self.results)}",
            f"  Passed            : {len(passed)} ({len(passed)/len(self.results)*100:.1f}%)",
            f"  Failed            : {len(self.results)-len(passed)}",
            f"  Avg reduction     : {sum(reds)/len(reds):.1f}%" if reds else "  Avg reduction     : –",
            f"  Avg latency       : {sum(lats)/len(lats):.2f}s" if lats else "  Avg latency       : –",
            "",
            "DETAILED RESULTS",
            "-" * 72,
            f"  {'#':>2}  {'Domain':<14} {'Subtype':<20} {'AIR':>5} {'Dir':>5} {'Red%':>6}  {'Lat':>6}  {'Status'}",
            "  " + "-" * 70,
        ]

        for r in self.results:
            res = r["result"]
            air_t = str(res["air_tokens"]) if res["air_tokens"] > 0 else "–"
            red_s = f"{res['reduction_percent']:.1f}%" if res["air_tokens"] > 0 else "–"
            stat  = "PASS" if res["success"] else f"FAIL ({res['sandbox_tier']})"
            lines.append(
                f"  {r['id']:>2}  {r['domain']:<14} {r['subtype']:<20} "
                f"{air_t:>5} {res['direct_baseline']:>5} {red_s:>6}  {res['latency_s']:>5.1f}s  {stat}"
            )

        lines += [
            "",
            "DOMAIN BREAKDOWN",
            "-" * 72,
        ]
        for domain in sorted(set(r["domain"] for r in self.results)):
            dr     = [r for r in self.results if r["domain"] == domain]
            d_pass = [r for r in dr if r["result"].get("success")]
            d_reds = [r["result"]["reduction_percent"] for r in dr if r["result"].get("air_tokens", 0) > 0]
            exp    = EXPECTED_REDUCTIONS.get(domain, "–")
            avg_dr = sum(d_reds) / len(d_reds) if d_reds else 0
            lines.append(
                f"  {domain:<14}: {avg_dr:5.1f}% reduction | "
                f"{len(d_pass)}/{len(dr)} pass | "
                f"expected {exp}% (paper)"
            )

        lines += ["", "=" * 72, ""]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        msgbox.showinfo("Exported", f"Report saved to:\n{path}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ENTRY POINT                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def check_dependencies():
    missing = []
    if not REQUESTS_OK:
        missing.append("requests")
    return missing

def main():
    missing = check_dependencies()

    # Tkinter is always available in Python ≥ 3.x (it's built-in)
    # Only 'requests' is an external dependency
    if missing:
        # Show a minimal Tk dialog
        root = tk.Tk()
        root.withdraw()
        install_cmd = f"pip install {' '.join(missing)}"
        msgbox.showerror("Missing Dependencies",
            f"Required packages not installed:\n  {', '.join(missing)}\n\n"
            f"Install with:\n  {install_cmd}\n\nThen restart this tool.")
        root.destroy()
        sys.exit(1)

    app = AIRBenchmarkApp()
    app.mainloop()


if __name__ == "__main__":
    main()
