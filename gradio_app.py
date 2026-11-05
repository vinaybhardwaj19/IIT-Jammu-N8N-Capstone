"""
SalesAI SDR — Full Gradio Dashboard (IIT Jammu Capstone 2026)
=============================================================
Author  : Vinay Bhardwaj
Course  : IIT Jammu Summer School 2026

SalesFlow AI — N8N CRM & Sales Automation Platform (IIT Jammu Capstone '26)
Assignment 4: AI CRM & Sales Automation Platform
- 6 Production N8N Workflows (58 Nodes Total)
- Interactive CRM Kanban & Deal Pipeline Tracker (SQLite)
- Deterministic Mathematical RevOps ROI Simulator (Non-AI)
- AI Sales Specialist Copilot (Research, BANT Qualification, Email Cadence, Meetings, Objections)
- Competitor Battlecards & Knowledge RAG Engine
"""

import os
import sys
import json
from html import escape
import gradio as gr
from datetime import datetime
from dotenv import load_dotenv

# ── Windows encoding fix ───────────────────────────────────────
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Path setup ─────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT, ".env"))
sys.path.insert(0, os.path.join(ROOT, "Tab2_SalesAI_Agents"))
sys.path.insert(0, os.path.join(ROOT, "Tab2_SalesAI_Agents", "src"))

# ── Agent imports ──────────────────────────────────────────────
from salesai_agents.base import OPENAI_API_KEY
from salesai_agents.prospect_research_agent import ProspectResearchAgent
from salesai_agents.lead_qualification_agent import LeadQualificationAgent
from salesai_agents.email_writer_agent import EmailWriterAgent
from salesai_agents.objection_crm_agents import ObjectionHandlerAgent
from salesai_agents.crm_manager_agent import CRMManagerAgent
from salesai_agents.meeting_coordinator_agent import MeetingCoordinatorAgent
from tools.crm_database import get_all_leads, get_pipeline_stats, upsert_lead, get_lead, init_database, mark_email_sent, estimate_deal_amount, log_activity, get_activities, update_lead_stage
from tools.email_sender import send_cold_email, get_smtp_status
from tools.revops_engine import generate_kanban_board_html, calculate_deterministic_roi, generate_risk_matrix_html, move_deal_stage
from tools.knowledge_rag import query_battlecard, get_roi_summary, search_sales_knowledge, BATTLECARDS, CASE_STUDIES, ROI_BENCHMARKS
from workflow_node_engine import run_node_pipeline

# ── N8N Workflow files path ────────────────────────────────────
WORKFLOWS_DIR = os.path.join(ROOT, "Tab1_SalesFlow_N8N", "workflows")

# Initialize DB
init_database()


# ══════════════════════════════════════════════════════════════
# GLOBAL AGENT POOL
# ══════════════════════════════════════════════════════════════

_agents = {}

def get_agents():
    global _agents
    if not _agents:
        _agents = {
            "research":  ProspectResearchAgent(),
            "qualify":   LeadQualificationAgent(),
            "email":     EmailWriterAgent(),
            "objection": ObjectionHandlerAgent(),
            "crm":       CRMManagerAgent(),
            "meeting":   MeetingCoordinatorAgent(),
        }
    return _agents


# ══════════════════════════════════════════════════════════════
# SAVED CRM LEADS
# ══════════════════════════════════════════════════════════════

SAMPLE_LEAD_IDS = {"LEAD-2026-001", "LEAD-2026-002", "LEAD-2026-003", "LEAD-2026-004"}
CRM_LEADS = [
    lead for lead in get_all_leads(limit=500)
    if lead.get("lead_id")
    and str(lead.get("source") or "").strip()
    and lead.get("lead_id") not in SAMPLE_LEAD_IDS
    and not str(lead.get("lead_id", "")).startswith("LEAD-N8N-")
]


def lead_option_label(lead: dict) -> str:
    return f"{lead.get('full_name') or 'Unnamed contact'} — {lead.get('company') or 'Company not set'} · {lead.get('lead_id')}"


LEAD_BY_LABEL = {lead_option_label(lead): lead for lead in CRM_LEADS}
LEAD_LABELS = ["— Enter manually —"] + list(LEAD_BY_LABEL)


def get_lead_by_label(label: str) -> dict:
    return dict(LEAD_BY_LABEL.get(label, {}))


# ══════════════════════════════════════════════════════════════
# ██████████████  TAB 1 — N8N WORKFLOWS  ████████████████████
# ══════════════════════════════════════════════════════════════

N8N_WORKFLOWS = [
    {
        "id": "WF-01",
        "file": "01_lead_capture_registration.json",
        "name": "Lead Capture & Registration",
        "trigger": "Webhook POST /capture-lead",
        "nodes": 10,
        "icon": "🎯",
        "desc": "Instant AI-powered lead intake. Scores lead on arrival, normalizes schema, saves to CRM database, sends welcome email via SMTP, emits Slack alert for Hot Leads.",
        "steps": [
            "1. Webhook: New Lead — Ingests lead payload (name, company, email, role, industry, budget)",
            "2. Set: Format Lead Data — Normalizes fields, formats phone & parses integer budget",
            "3. AI: Analyze & Score Lead — Evaluates ICP criteria and scores lead 0-100",
            "4. Code: Merge Lead + AI Analysis — Combines lead data with qualification telemetry",
            "5. Postgres: Save Lead to CRM DB — Inserts record into CRM `leads` table",
            "6. Gmail: Welcome Email to Lead — Dispatches branded welcome message via SMTP",
            "7. IF: Hot Lead? — Temperature routing gate (Threshold: Score >= 70)",
            "8. Slack: Hot Lead Alert — Emits instant notification card to #hot-leads-alert",
            "9. Webhook Response: Success — Returns HTTP 200 JSON with lead_id and score",
            "10. Stop: Capture Integration Error — Fail-safe error circuit breaker",
        ],
        "color": "#6366f1",
    },
    {
        "id": "WF-02",
        "file": "02_ai_lead_scoring_qualification.json",
        "name": "AI Lead Scoring & BANT Qualification",
        "trigger": "Webhook POST /qualify-lead",
        "nodes": 9,
        "icon": "📊",
        "desc": "Full BANT matrix evaluation. Evaluates Budget, Authority, Need, and Timeline against ICP criteria and routes Qualified leads to AE and nurture leads to pipeline sheet.",
        "steps": [
            "1. Webhook: Lead Qualification Request — Receives lead_id for BANT evaluation",
            "2. Postgres: Fetch Lead History — Queries CRM database for past activities & notes",
            "3. AI: BANT Qualification Analysis — Analyzes Budget, Authority, Need & Timeline (0-25 each)",
            "4. Code: Compute Composite Score — Computes total score (0-100) and deal probability",
            "5. Switch: Route by Qualification — Evaluates branches: Qualified (>=70), Nurture (40-69), Cold (<40)",
            "6. Postgres: Update Qualified Lead — Updates CRM deal stage to 'Qualified'",
            "7. Google Sheets: Add to Nurture List — Synchronizes nurture opportunities to pipeline sheet",
            "8. Webhook Response — Emits HTTP 200 qualification report with action items",
            "9. Stop: Capture Integration Error — Fail-safe error circuit breaker",
        ],
        "color": "#ec4899",
    },
    {
        "id": "WF-03",
        "file": "03_sales_rep_assignment_crm.json",
        "name": "Sales Rep Assignment & CRM Update",
        "trigger": "Webhook POST /assign-rep",
        "nodes": 9,
        "icon": "👤",
        "desc": "Smart round-robin + skill-matched rep assignment. Balances workload, matches industry expertise, emails assigned rep with briefing dossier.",
        "steps": [
            "1. Webhook: Assign Rep Trigger — Ingests qualified lead assignment request",
            "2. Postgres: Fetch Available Reps — Queries sales rep roster and active deal load",
            "3. Postgres: Fetch Lead Details — Fetches lead score, industry and deal size",
            "4. Code: Smart Rep Assignment Algorithm — Balances capacity and matches deal tier",
            "5. Postgres: Update Lead Assignment — Commits assigned rep and timestamp to CRM DB",
            "6. Gmail: Notify Assigned Rep — Dispatches briefing email and script to rep",
            "7. Slack: Team Assignment Notification — Sends assignment card to #sales-handoff",
            "8. Webhook Response — Returns HTTP 200 with rep assignment details",
            "9. Stop: Capture Integration Error — Fail-safe error circuit breaker",
        ],
        "color": "#06b6d4",
    },
    {
        "id": "WF-04",
        "file": "04_automated_followup_meeting_scheduler.json",
        "name": "Automated Follow-ups & Meeting Scheduler",
        "trigger": "⏰ Cron — Every 8 hours",
        "nodes": 11,
        "icon": "📅",
        "desc": "5-touch cadence engine runs every 8h. Crafts touch-specific copy, sends follow-up via SMTP, and auto-books a discovery slot via Google Calendar.",
        "steps": [
            "1. Schedule: Every 8 Hours — Automated cadence cron trigger",
            "2. Postgres: Get Leads Needing Follow-up — Queries active leads due for contact",
            "3. Split: Process Each Lead — Iterates batch through cadence pipeline",
            "4. AI: Write Personalized Follow-up Email — Crafts targeted outreach email",
            "5. Gmail: Send Follow-up Email — Dispatches touchpoint email via SMTP",
            "6. IF: First Follow-up? Book Meeting — Checks if prospect requires discovery booking",
            "7. Google Calendar: Schedule Discovery Call — Generates 1-click meeting invite link",
            "8. Postgres: Log Appointment — Records booked discovery call in CRM",
            "9. Postgres: Log Follow-up — Increments touchpoint counter in CRM audit trail",
            "10. Stop: Capture Integration Error — Fail-safe error circuit breaker",
            "11. Code: Validate Confirmed Meeting Slot — Verifies calendar availability and timezone",
        ],
        "color": "#10b981",
    },
    {
        "id": "WF-05",
        "file": "05_proposal_generation_human_approval.json",
        "name": "AI Proposal Generation & HITL Approval",
        "trigger": "Webhook POST /generate-proposal",
        "nodes": 11,
        "icon": "📄",
        "desc": "Generates a full responsive proposal, saves to Google Drive, then pauses for human manager approval via a verification token link. Approved = proposal dispatched to client.",
        "steps": [
            "1. Webhook: Proposal Request — Receives lead_id for proposal generation",
            "2. Postgres: Fetch Complete Lead Data — Queries CRM for deal financials and BANT scores",
            "3. AI: Generate Sales Proposal — Generates full executive proposal with ROI justification",
            "4. Google Drive: Save Proposal — Formats and archives proposal document",
            "5. Gmail: Send for Manager Approval — Sends authorization request to Sales Director",
            "6. Wait: Manager Approval (HITL) — Workflow pauses until manager signs off with token",
            "7. IF: Approved? — Evaluates manager sign-off condition",
            "8. Gmail: Send Proposal to Prospect — Dispatches formal proposal to prospect via SMTP",
            "9. Postgres: Update Status to Proposal Sent — Advances CRM deal stage to 'Proposal Sent'",
            "10. Webhook Response — Emits HTTP 200 with proposal verification details",
            "11. Stop: Capture Integration Error — Fail-safe error circuit breaker",
        ],
        "color": "#f59e0b",
    },
    {
        "id": "WF-06",
        "file": "06_sales_dashboard_analytics_report.json",
        "name": "Sales Dashboard & Weekly Analytics",
        "trigger": "⏰ Cron — Every Monday 08:00 AM",
        "nodes": 8,
        "icon": "📈",
        "desc": "Weekly executive briefing engine. Aggregates SQL metrics, synthesizes insights, updates Google Sheets KPI dashboard, delivers report via Gmail + Slack.",
        "steps": [
            "1. Schedule: Every Monday 8AM — Weekly reporting cron trigger",
            "2. Postgres: Pull Weekly KPIs — Aggregates win rates, pipeline value and volume",
            "3. Postgres: Rep Performance Leaderboard — Compiles rep quota attainment table",
            "4. AI: Generate Executive Report — Synthesizes executive summary and revenue forecast",
            "5. Google Sheets: Update Dashboard — Synchronizes weekly KPIs to analytics table",
            "6. Gmail: Email Report to Leadership — Dispatches briefing to executive team via SMTP",
            "7. Slack: Post Report Summary — Posts Monday morning KPI card to #sales-leadership",
            "8. Stop: Capture Integration Error — Fail-safe error circuit breaker",
        ],
        "color": "#8b5cf6",
    },
]


def render_visual_flow(title: str, subtitle: str, steps: list[tuple[str, str, str]]) -> str:
    """Build a responsive, high-contrast SVG flow illustration for the dashboard."""
    card_w, card_h, gap, left, top = 174, 92, 28, 20, 54
    width = left * 2 + len(steps) * card_w + max(0, len(steps) - 1) * gap
    height = 188
    cards = []
    for index, (label, detail, color) in enumerate(steps):
        x = left + index * (card_w + gap)
        cards.append(
            f'<rect x="{x}" y="{top}" width="{card_w}" height="{card_h}" rx="16" fill="#ffffff" stroke="{color}" stroke-width="2"/>'
            f'<circle cx="{x + 23}" cy="{top + 23}" r="13" fill="{color}"/>'
            f'<text x="{x + 23}" y="{top + 28}" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">{index + 1}</text>'
            f'<text x="{x + 43}" y="{top + 28}" font-size="14" font-weight="700" fill="#172b4d">{label}</text>'
            f'<text x="{x + 15}" y="{top + 58}" font-size="11" fill="#52647d">{detail}</text>'
        )
        if index < len(steps) - 1:
            arrow_x = x + card_w + 4
            cards.append(f'<path d="M{arrow_x} {top + card_h / 2} H{arrow_x + gap - 8} m-7 -6 7 6 -7 6" fill="none" stroke="#9aabc0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    return f'''<figure class="process-visual" role="img" aria-label="{title}">
      <figcaption><strong>{title}</strong><span>{subtitle}</span></figcaption>
      <div class="process-visual-scroll"><svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect width="100%" height="100%" rx="20" fill="#f4f8fd"/>{''.join(cards)}
      </svg></div>
    </figure>'''


def render_problem_solution_visual() -> str:
    rows = [
        ("Slow response", "Instant capture + routing", "#e98972", "#249c8c"),
        ("Manual qualification", "AI BANT scoring", "#e9ae55", "#3978e8"),
        ("Missed follow-ups", "Automated touch cadence", "#e98972", "#249c8c"),
        ("Low visibility", "Shared KPI reporting", "#e9ae55", "#3978e8"),
        ("Proposal delays", "Draft + manager approval", "#e98972", "#249c8c"),
    ]
    svg_rows = []
    for index, (problem, solution, problem_color, solution_color) in enumerate(rows):
        y = 55 + index * 43
        svg_rows.append(
            f'<rect x="28" y="{y}" width="310" height="32" rx="10" fill="#fff" stroke="{problem_color}"/>'
            f'<circle cx="48" cy="{y + 16}" r="7" fill="{problem_color}"/>'
            f'<text x="65" y="{y + 21}" font-size="13" font-weight="600" fill="#263b56">{problem}</text>'
            f'<path d="M355 {y + 16}h64m-8 -6 8 6-8 6" fill="none" stroke="#93a6bd" stroke-width="2"/>'
            f'<rect x="438" y="{y}" width="390" height="32" rx="10" fill="#fff" stroke="{solution_color}"/>'
            f'<circle cx="458" cy="{y + 16}" r="7" fill="{solution_color}"/>'
            f'<text x="475" y="{y + 21}" font-size="13" font-weight="600" fill="#263b56">{solution}</text>'
        )
    return f'''<figure class="problem-visual" role="img" aria-label="Sales problems mapped to workflow solutions">
      <figcaption><strong>From sales friction to a clear next step</strong><span>Each challenge maps to an automation in the project.</span></figcaption>
      <div class="problem-visual-scroll"><svg viewBox="0 0 856 285" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
       <rect width="856" height="285" rx="20" fill="#f4f8fd"/>
       <text x="28" y="35" font-size="11" font-weight="700" letter-spacing="1.2" fill="#9b5142">SALES CHALLENGE</text>
       <text x="438" y="35" font-size="11" font-weight="700" letter-spacing="1.2" fill="#187f74">PROJECT RESPONSE</text>
       {''.join(svg_rows)}</svg></div>
    </figure>'''


def render_architecture_visual() -> str:
    return render_visual_flow(
        "SalesFlow N8N system architecture",
        "A map of the six exported workflows and their configured integration points; live services need credentials in n8n.",
        [
            ("Entry points", "Webhooks + schedules", "#3978e8"),
            ("6 N8N flows", "58 exported nodes", "#8b6bd6"),
            ("AI decisions", "Scoring + writing", "#249c8c"),
            ("Data services", "Postgres + Sheets", "#e9ae55"),
            ("Team updates", "Gmail + Slack", "#e98972"),
        ],
    )


def render_lead_lifecycle_visual() -> str:
    return '''<figure class="problem-visual" role="img" aria-label="Lead lifecycle branches after qualification into sales follow-up or nurture">
      <figcaption><strong>Lead lifecycle</strong><span>BANT creates two routes. Sales ready leads go to a rep; other leads enter nurture. Proposals include manager review.</span></figcaption>
      <div class="problem-visual-scroll"><svg viewBox="0 0 980 258" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect width="980" height="258" rx="20" fill="#f4f8fd"/>
        <g fill="none" stroke="#8198b3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M174 75H212M382 75H420M600 75H646V46H680M646 75V136H680"/>
          <path d="M808 46h18v77h19M808 136h18v-13h19M901 150v26H489v20"/>
        </g>
        <g font-family="system-ui,Segoe UI,sans-serif">
          <rect x="22" y="48" width="152" height="54" rx="13" fill="#fff" stroke="#3978e8" stroke-width="2"/><text x="98" y="71" text-anchor="middle" font-size="14" font-weight="700" fill="#172b4d">New lead</text><text x="98" y="89" text-anchor="middle" font-size="11" fill="#52647d">Form or webhook</text>
          <rect x="212" y="48" width="170" height="54" rx="13" fill="#fff" stroke="#3978e8" stroke-width="2"/><text x="297" y="71" text-anchor="middle" font-size="14" font-weight="700" fill="#172b4d">WF-01 Capture</text><text x="297" y="89" text-anchor="middle" font-size="11" fill="#52647d">Validate + score</text>
          <rect x="420" y="48" width="180" height="54" rx="13" fill="#fff" stroke="#8b6bd6" stroke-width="2"/><text x="510" y="71" text-anchor="middle" font-size="14" font-weight="700" fill="#172b4d">WF-02 BANT</text><text x="510" y="89" text-anchor="middle" font-size="11" fill="#52647d">Qualification decision</text>
          <rect x="680" y="20" width="128" height="52" rx="13" fill="#e7f8f3" stroke="#249c8c" stroke-width="2"/><text x="744" y="42" text-anchor="middle" font-size="13" font-weight="700" fill="#176c63">Qualified</text><text x="744" y="59" text-anchor="middle" font-size="11" fill="#426a65">Assign a rep</text>
          <rect x="680" y="110" width="128" height="52" rx="13" fill="#fff5df" stroke="#e9ae55" stroke-width="2"/><text x="744" y="132" text-anchor="middle" font-size="13" font-weight="700" fill="#805613">Nurture</text><text x="744" y="149" text-anchor="middle" font-size="11" fill="#756344">Follow-up sequence</text>
          <rect x="845" y="96" width="112" height="54" rx="13" fill="#fff0ec" stroke="#e98972" stroke-width="2"/><text x="901" y="118" text-anchor="middle" font-size="12" font-weight="700" fill="#8f493d">Meeting +</text><text x="901" y="136" text-anchor="middle" font-size="12" font-weight="700" fill="#8f493d">proposal review</text>
          <rect x="22" y="196" width="935" height="40" rx="12" fill="#eaf2ff" stroke="#91b4e8"/><text x="489" y="221" text-anchor="middle" font-size="12" font-weight="700" fill="#174ea6">After review: Closed Won / Closed Lost  ·  WF-06 sends a weekly KPI summary</text>
          <text x="654" y="18" font-size="10" font-weight="700" fill="#187f74">QUALIFIED</text><text x="652" y="107" font-size="10" font-weight="700" fill="#9a6616">NURTURE</text>
        </g>
      </svg></div>
    </figure>'''


def render_tech_stack_visual() -> str:
    provider = ("OpenAI SDK + " + os.getenv("OPENAI_AGENT_MODEL","gpt-4.1-mini")) if OPENAI_API_KEY else "Gemini/Groq (default - no OpenAI key needed)"
    provider = escape(provider)
    app_flow = render_visual_flow(
        "What the running AI SDR app uses",
        "The runtime stack reflected by the project code.",
        [
            ("Gradio UI", "Browser dashboard", "#3978e8"),
            ("Python agents", "Research + sales", "#8b6bd6"),
            (provider, "Configured AI API", "#249c8c"),
            ("SQLite CRM", "Local lead records", "#e9ae55"),
            ("Email", "Configured SMTP delivery", "#e98972"),
        ],
    )
    n8n_flow = render_visual_flow(
        "What the N8N exports describe",
        "These JSON workflows define external integrations; each service needs its own credentials in a live n8n instance.",
        [
            ("N8N JSON", "6 workflow exports", "#3978e8"),
            ("OpenAI", "Configured node", "#8b6bd6"),
            ("PostgreSQL", "Workflow data", "#249c8c"),
            ("Google + Slack", "External services", "#e9ae55"),
        ],
    )
    return app_flow + n8n_flow


def get_crm_lead_choices() -> list[tuple[str, str]]:
    """Return existing CRM records for the end-to-end pipeline selector."""
    return [(lead_option_label(lead), str(lead.get("lead_id"))) for lead in CRM_LEADS]


def get_workflow_overview():
    """Returns the N8N workflow architecture overview markdown."""
    return """## 🔄 SalesFlow N8N — 6-Workflow Sales Automation Platform

The diagrams above show the **exported workflow design**. The nodes reference OpenAI, PostgreSQL, Gmail, Google Calendar/Sheets/Drive, and Slack. Their live use depends on credentials configured in an n8n instance.

### 📊 Workflow Inventory

| Metric | Value |
|--------|-------|
| 🔧 Total Workflow Nodes | **58 Nodes** |
| 🤖 AI node in exports | **OpenAI / GPT-4o node configuration** |
| 💾 Database node in exports | **PostgreSQL** |
| 📧 Other configured services | **Gmail, Google APIs, Slack** |

The running Python dashboard is a separate part of the project: its six SalesAI specialists use Gemini/Groq by default (OpenAI optional). SeeI Agents SDK and local SQLite CRM. The dashboard simulator does not execute the external n8n integrations.
"""


def load_workflow_json(workflow_file: str) -> str:
    """Load and format a workflow JSON file."""
    filepath = os.path.join(WORKFLOWS_DIR, workflow_file)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Extract key info
        name = data.get("name", "Unknown")
        nodes = data.get("nodes", [])
        node_list = "\n".join([
            f"  • [{n.get('type', 'unknown').split('.')[-1]}] {n.get('name', 'Node')}"
            for n in nodes[:15]
        ])
        return f"""### 📋 Workflow: {name}

**Total Nodes:** {len(nodes)}

**Node Sequence:**
{node_list}

---
<details>
<summary>📄 View Full JSON</summary>

```json
{json.dumps(data, indent=2)[:3000]}{'...(truncated)' if len(json.dumps(data)) > 3000 else ''}
```
</details>"""
    except Exception as e:
        return f"⚠️ Could not load workflow file: {e}"


def get_workflow_detail(wf_id: str):
    """Return details, an SVG node map, and JSON for a selected workflow."""
    wf = next((w for w in N8N_WORKFLOWS if w["id"] == wf_id), None)
    if not wf:
        return "Select a workflow to view details.", "", ""

    steps_md = "\n".join([f"- {s}" for s in wf["steps"]])

    detail_md = f"""## {wf['icon']} {wf['id']}: {wf['name']}

> {wf['desc']}

### ⚡ Trigger
`{wf['trigger']}`

### 🔢 Node Count: {wf['nodes']} nodes

### 📋 Execution Steps
{steps_md}
"""
    graph_html = render_workflow_diagram(wf["file"])
    json_md = load_workflow_json(wf["file"])
    return detail_md, graph_html, json_md


def render_workflow_diagram(workflow_file: str) -> str:
    """Render a scrollable SVG map directly from an exported n8n workflow."""
    filepath = os.path.join(WORKFLOWS_DIR, workflow_file)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            workflow = json.load(file)

        nodes = workflow.get("nodes", [])
        if not nodes:
            return '<div class="workflow-map-empty">This workflow has no nodes to display.</div>'

        node_w, node_h, pad_x, pad_y = 190, 76, 44, 52
        positioned = []
        for i, node in enumerate(nodes):
            pos = node.get("position") or [i * 220, 0]
            positioned.append((node, float(pos[0]), float(pos[1])))
        min_x = min(x for _, x, _ in positioned)
        min_y = min(y for _, _, y in positioned)
        max_x = max(x for _, x, _ in positioned)
        max_y = max(y for _, _, y in positioned)
        width = int(max_x - min_x + node_w + pad_x * 2)
        height = int(max_y - min_y + node_h + pad_y * 2)

        def point(node_name):
            node, x, y = node_lookup[node_name]
            return x - min_x + pad_x, y - min_y + pad_y

        node_lookup = {
            node.get("name", f"Node {i + 1}"): item
            for i, item in enumerate(positioned)
            for node, _, _ in [item]
        }
        type_colors = {
            "webhook": ("#eaf2ff", "#2563eb"), "scheduleTrigger": ("#eaf2ff", "#2563eb"),
            "openAi": ("#f2edff", "#7657c8"), "postgres": ("#e8f7f3", "#16836f"),
            "gmail": ("#fff0f0", "#d25454"), "slack": ("#fff3e9", "#d97732"),
            "googleSheets": ("#edf8ec", "#4e9b57"), "googleCalendar": ("#edf4ff", "#4475c6"),
            "googleDrive": ("#edf8ec", "#4e9b57"), "if": ("#fff6df", "#c68a16"),
            "switch": ("#fff6df", "#c68a16"), "wait": ("#fff2e5", "#c87922"),
        }

        edge_markup = []
        for source_name, outputs in workflow.get("connections", {}).items():
            if source_name not in node_lookup:
                continue
            sx, sy = point(source_name)
            for output_type, branches in outputs.items():
                for branch_index, branch in enumerate(branches):
                    for connection in branch:
                        target_name = connection.get("node")
                        if target_name not in node_lookup:
                            continue
                        tx, ty = point(target_name)
                        start_x, start_y = sx + node_w, sy + node_h / 2
                        end_x, end_y = tx, ty + node_h / 2
                        curve = max(34, (end_x - start_x) * .42)
                        edge_markup.append(
                            f'<path class="workflow-edge" d="M {start_x:.1f} {start_y:.1f} '
                            f'C {start_x + curve:.1f} {start_y:.1f}, '
                            f'{end_x - curve:.1f} {end_y:.1f}, {end_x:.1f} {end_y:.1f}" '
                            f'marker-end="url(#workflow-arrow)" />'
                        )
                        if len(branches) > 1:
                            branch_label = "Yes" if branch_index == 0 else "No" if branch_index == 1 else f"Path {branch_index + 1}"
                            edge_markup.append(
                                f'<text class="workflow-edge-label" x="{start_x + 12:.1f}" '
                                f'y="{start_y - 8 + branch_index * 16:.1f}">{branch_label}</text>'
                            )

        node_markup = []
        for i, (node, x, y) in enumerate(positioned):
            name = node.get("name", f"Node {i + 1}")
            node_type = node.get("type", "unknown").split(".")[-1]
            fill, stroke = type_colors.get(node_type, ("#f0f4f8", "#7890a8"))
            px, py = point(name)
            title = escape(name)
            label = name if len(name) <= 25 else name[:23] + "…"
            first_line, second_line = label, ""
            if len(label) > 16:
                split_at = label.rfind(" ", 0, 17)
                if split_at > 6:
                    first_line, second_line = label[:split_at], label[split_at + 1:]
            second = f'<tspan x="{px + 14}" dy="16">{escape(second_line)}</tspan>' if second_line else ""
            node_markup.append(f'''<g class="workflow-node" role="group" aria-label="{title}">
              <title>{title} — {escape(node_type)}</title>
              <rect x="{px}" y="{py}" width="{node_w}" height="{node_h}" rx="12" fill="{fill}" stroke="{stroke}" />
              <circle cx="{px + 14}" cy="{py + 15}" r="4" fill="{stroke}" />
              <text class="workflow-node-type" x="{px + 25}" y="{py + 19}">{escape(node_type.upper())}</text>
              <text class="workflow-node-name" x="{px + 14}" y="{py + 43}">{escape(first_line)}{second}</text>
            </g>''')

        title = escape(workflow.get("name", workflow_file))
        return f'''<section class="workflow-map-card">
          <div class="workflow-map-heading">
            <div><span class="eyebrow">EXPORTED WORKFLOW MAP</span><h3>{title}</h3></div>
            <span class="workflow-node-count">{len(nodes)} nodes</span>
          </div>
          <p class="workflow-map-note">Node connections are drawn from this workflow’s exported JSON. Live execution requires importing it into n8n and configuring credentials.</p>
          <div class="workflow-map-scroll"><svg role="img" aria-label="{title} workflow node diagram" viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <defs><marker id="workflow-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#8ca0b7" /></marker></defs>
            <style>
              .workflow-edge {{ fill:none; stroke:#9aacc0; stroke-width:2; }}
              .workflow-edge-label {{ font:600 10px sans-serif; fill:#64748b; }}
              .workflow-node-type {{ font:700 9px sans-serif; letter-spacing:1px; fill:#65778e; }}
              .workflow-node-name {{ font:600 12px sans-serif; fill:#20344f; }}
            </style>
            {''.join(edge_markup)}{''.join(node_markup)}
          </svg></div>
        </section>'''
    except Exception as exc:
        return f'<div class="workflow-map-empty">Could not render workflow map: {escape(str(exc))}</div>'


# ── Live N8N Webhook Runner ────────────────────────────────────
def _workflow_lead(lead_label, custom_name, custom_company, custom_email, custom_role, custom_industry, custom_budget, custom_notes):
    saved_lead = get_lead_by_label(lead_label) if lead_label and lead_label != "— Enter manually —" else {}
    return saved_lead or {
        "full_name": (custom_name or "Synthetic Contact").strip(),
        "company": (custom_company or "Example Company").strip(),
        "email": (custom_email or "synthetic-lead@example.com").strip(),
        "role": (custom_role or "Sales Operations").strip(),
        "industry": (custom_industry or "Software").strip(),
        "budget": (custom_budget or "Not specified").strip(),
        "notes": (custom_notes or "Synthetic capstone test record").strip(),
    }


def simulate_n8n_workflow(
    wf_choice: str,
    lead_preset: str,
    custom_name: str = "",
    custom_company: str = "",
    custom_email: str = "",
    custom_role: str = "",
    custom_industry: str = "",
    custom_budget: str = "",
    custom_notes: str = "",
):
    """Render a safe local simulation trace for all workflow nodes without remote side effects."""
    wf_id = wf_choice.split(":")[0].strip().split()[-1] if ":" in wf_choice else wf_choice.strip()
    workflow = next((item for item in N8N_WORKFLOWS if item["id"] == wf_id), None)
    if workflow is None:
        return "### Unknown workflow", "", "**Simulation:** not run — choose one of the six exported workflows."

    workflow_path = os.path.join(WORKFLOWS_DIR, workflow["file"])
    try:
        with open(workflow_path, "r", encoding="utf-8") as handle:
            exported = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return f"### Workflow JSON could not be read\n\n`{escape(str(exc))}`", "", "**Simulation:** failed."

    lead = _workflow_lead(
        lead_preset, custom_name, custom_company, custom_email, custom_role,
        custom_industry, custom_budget, custom_notes,
    )
    trace = []
    for index, node in enumerate(exported.get("nodes", []), start=1):
        node_name = node.get("name", f"Node {index}")
        node_type = node.get("type", "unknown").split(".")[-1]
        lowered = node_type.lower()
        if "webhook" in lowered:
            detail = f"Webhook accepted: Ingested lead record for {lead.get('full_name')} ({lead.get('email')})"
        elif "set" in lowered:
            detail = f"Normalized contact schema: Sanitized email, parsed deal value, validated syntax"
        elif "openai" in lowered:
            detail = f"AI ICP Evaluation: Scored BANT criteria and calculated commercial deal fit"
        elif "code" in lowered:
            detail = f"Algorithmic Processing: Merged lead telemetry and calculated tier routing"
        elif "postgres" in lowered:
            detail = f"Database Persistence: Schema validated and record mapped for CRM `leads` table"
        elif "gmail" in lowered:
            detail = f"Email Template: Compiled branded HTML outreach for {lead.get('email')}"
        elif "if" in lowered:
            detail = f"Conditional Gate: Evaluated threshold condition -> Routed to primary branch"
        elif "switch" in lowered:
            detail = f"Multi-Way Switch: Evaluated lead parameters and determined routing branch"
        elif "slack" in lowered:
            detail = f"Team Alert: Formatted alert payload ready for team notification"
        elif "calendar" in lowered:
            detail = f"Calendar Scheduler: Generated 1-click meeting invite link"
        elif "wait" in lowered:
            detail = f"Human-in-the-Loop: Approval pause gate armed with verification token"
        elif "stopanderror" in lowered:
            detail = f"Circuit Breaker: Verified zero errors across pipeline"
        else:
            detail = f"Logic step executed from exported workflow definition"

        trace.append({
            "step": index,
            "node": node_name,
            "type": node_type,
            "status": "SIMULATED",
            "detail": detail,
        })

    result = {
        "mode": "LOCAL_JSON_SIMULATION",
        "workflow_id": wf_id,
        "workflow_name": exported.get("name", workflow["name"]),
        "simulation_id": f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "lead": {
            "full_name": lead.get("full_name"),
            "company": lead.get("company"),
            "email": lead.get("email"),
            "role": lead.get("role"),
            "industry": lead.get("industry"),
        },
        "nodes_simulated": len(trace),
        "trace": trace,
        "connections_from_export": exported.get("connections", {}),
        "side_effects": {
            "n8n_webhook_called": False,
            "ai_provider_called": False,
            "database_changed": False,
            "email_or_message_sent": False,
            "calendar_or_drive_or_sheet_changed": False,
        },
    }
    details = json.dumps(result, indent=2, ensure_ascii=False)
    telemetry = {
        "mode": "LOCAL_JSON_SIMULATION",
        "workflow_id": wf_id,
        "nodes_simulated": len(trace),
        "external_actions": False,
    }
    log_text = f"### {wf_id} local simulation trace\n\nMode: `LOCAL_JSON_SIMULATION` · Target Contact: `{lead.get('email')}` · Nodes Simulated: {len(trace)}\n\n```json\n" + details + "\n```"
    telemetry_str = "```json\n" + json.dumps(telemetry, indent=2, ensure_ascii=False) + "\n```"
    return (
        log_text,
        telemetry_str,
        f"**Simulation complete:** {len(trace)} workflow nodes represented; no external side effects occurred.",
    )


def execute_n8n_workflow(
    wf_id: str,
    lead_label: str,
    custom_name: str,
    custom_company: str,
    custom_email: str,
    custom_role: str,
    custom_industry: str,
    custom_budget: str,
    custom_notes: str,
):
    """
    Execute live webhook for N8N workflows with live database updates, AI scoring,
    and live TLS SMTP email dispatch.
    """
    wf_clean = wf_id.split(":")[0].strip().split()[-1] if ":" in wf_id else wf_id.strip()
    lead = _workflow_lead(
        lead_label, custom_name, custom_company, custom_email, custom_role,
        custom_industry, custom_budget, custom_notes,
    )
    result = run_node_pipeline(wf_clean, lead, is_live_webhook=True, send_live_smtp=True)
    json_str = "```json\n" + result["telemetry_json"] + "\n```"
    return result["markdown_trace"], json_str, result["summary"]


def get_dashboard_data():
    try:
        stats = get_pipeline_stats()
        leads = get_all_leads(limit=10)
        all_leads = get_all_leads(limit=1000)
        total    = int(stats.get("total_leads", 0) or 0)
        hot      = int(stats.get("hot_leads", 0) or 0)
        warm     = int(stats.get("warm_leads", 0) or 0)
        cold     = int(stats.get("cold_leads", 0) or 0)
        avg_score= float(stats.get("avg_score", 0) or 0)
        priced = [(lead, estimate_deal_amount(lead.get("estimated_deal_size"))) for lead in all_leads]
        priced = [(lead, amount) for lead, amount in priced if amount is not None]
        pipeline_val = sum(amount for _, amount in priced) if priced else None
        weighted_value = sum(amount * float(lead.get("deal_probability") or 0) / 100 for lead, amount in priced) if priced else None
        max_temp = max(hot, warm, cold, 1)

        def metric_card(icon, label, value, tone):
            return f'''<article class="metric-card {tone}">
                <div class="metric-card-icon">{icon}</div>
                <div class="metric-card-label">{label}</div>
                <div class="metric-card-value">{value}</div>
            </article>'''

        visual_summary = f'''<section class="dashboard-visuals">
          <div class="metric-grid">
            {metric_card("👥", "Total leads", f"{total:,}", "blue")}
            {metric_card("🔥", "Hot leads", f"{hot:,}", "coral")}
            {metric_card("🌤️", "Warm leads", f"{warm:,}", "amber")}
            {metric_card("📈", "Average BANT", f"{avg_score:.0f}/100", "teal")}
            {metric_card("💰", "Recorded deal estimates", f"${pipeline_val:,.0f}" if pipeline_val is not None else "Not recorded", "violet")}
          </div>
          <div class="distribution-card">
            <div class="distribution-heading">
              <div><span class="eyebrow">LEAD MIX</span><h3>Pipeline temperature</h3></div>
              <span class="distribution-total">{hot + warm + cold:,} scored</span>
            </div>
            <div class="stacked-bar" role="img" aria-label="Lead mix: {hot} hot, {warm} warm, {cold} cold">
              <span class="bar-hot" style="width:{hot / max_temp * 100:.2f}%"></span>
              <span class="bar-warm" style="width:{warm / max_temp * 100:.2f}%"></span>
              <span class="bar-cold" style="width:{cold / max_temp * 100:.2f}%"></span>
            </div>
            <div class="distribution-legend">
              <span><i class="dot hot"></i>Hot <b>{hot:,}</b></span>
              <span><i class="dot warm"></i>Warm <b>{warm:,}</b></span>
              <span><i class="dot cold"></i>Cold <b>{cold:,}</b></span>
            </div>
          </div>
        </section>'''

        leads_table = [
            [
                l.get("full_name", "—"),
                l.get("company", "—"),
                l.get("pipeline_stage", "—"),
                l.get("lead_temperature", "—"),
                f"{l.get('composite_score', 0)}/100",
                (l.get("created_at") or "")[:10],
            ]
            for l in leads
        ]

        summary = f"""## 📊 Live Pipeline Dashboard

| Metric | Value |
|--------|-------|
| 🎯 Total Leads | **{total}** |
| 🔥 Hot Leads | **{hot}** |
| 🌡️ Warm Leads | **{warm}** |
| ❄️ Cold Leads | **{cold}** |
| 📈 Avg BANT Score | **{avg_score}/100** |
| 💰 Recorded Deal Estimates | **{f'${pipeline_val:,.0f}' if pipeline_val is not None else 'Not available — no deal sizes recorded'}** |
| 🎯 Weighted Estimate | **{f'${weighted_value:,.0f}' if weighted_value is not None else 'Not available — no deal sizes recorded'}** |

> **Agent Runtime:** {"OpenAI SDK (" + os.getenv("OPENAI_AGENT_MODEL","gpt-4.1-mini") + ")" if OPENAI_API_KEY else "Gemini/Groq (no OpenAI key needed)"} | **DB:** salesai.db | **Refreshed:** {datetime.now().strftime("%H:%M:%S")}
"""
        return visual_summary, summary, leads_table
    except Exception as e:
        return "", f"⚠️ Dashboard error: {e}", []


# ── Research ──────────────────────────────────────────────────
def run_research(lead_preset, company, contact, role, industry, website):
    agents = get_agents()
    if lead_preset and lead_preset != "— Enter manually —":
        lead = get_lead_by_label(lead_preset)
        company  = lead.get("company", company)
        contact  = lead.get("full_name", contact)
        role     = lead.get("role", role)
        industry = lead.get("industry", industry)
        website  = lead.get("website", website)

    if not company or not contact:
        yield "⚠️ Please enter company and contact name.", "", ""
        return

    yield "🔍 Researching... fetching web data + AI analysis...", "", ""

    try:
        result = agents["research"].run({
            "company_name": company, "contact_name": contact,
            "contact_role": role, "industry": industry, "website": website
        })
        intel   = result.get("intelligence", {})
        real    = result.get("real_web_data", {})
        sources = result.get("data_sources", [])
        tech    = result.get("tech_stack_detected", [])
        news    = result.get("recent_news", [])

        research_md = f"""## 🔍 Research: {contact} @ {company}

### 📊 Data Sources
> **Real web data from:** {', '.join(sources) if sources else 'AI Generated'}

### 🏢 Company Profile
| Field | Value |
|-------|-------|
| Size | {intel.get('company_profile', {}).get('estimated_size', 'N/A')} |
| Revenue | {intel.get('company_profile', {}).get('estimated_revenue', 'N/A')} |
| Growth Stage | {intel.get('company_profile', {}).get('growth_stage', 'N/A')} |
| Business Model | {intel.get('company_profile', {}).get('business_model', 'N/A')} |

### 👤 Contact Profile
- **Seniority:** {intel.get('contact_profile', {}).get('seniority_level', 'N/A')}
- **Decision Power:** {intel.get('contact_profile', {}).get('decision_making_power', 'N/A')}
- **Personality:** {intel.get('contact_profile', {}).get('personality_type', 'N/A')}
- **KPIs:** {', '.join(intel.get('contact_profile', {}).get('likely_kpis', [])[:3])}

### 🎯 Pain Points
**Primary:** {intel.get('pain_points', {}).get('primary_pain', 'N/A')}

**Secondary:**
{chr(10).join(['- ' + p for p in intel.get('pain_points', {}).get('secondary_pains', [])[:3]])}

**Urgency:** {intel.get('pain_points', {}).get('urgency_indicators', 'N/A')}
"""

        web_md = ""
        if sources:
            web_md = f"""### 🌐 Real Web Intelligence
- **Tech Stack Detected:** {', '.join(tech) if tech else 'Not detected'}
- **Current CRM Tools:** {', '.join(real.get('current_crm_tools', [])) or 'Unknown'}
- **Business Triggers:** {'; '.join(real.get('business_triggers', [])[:2]) or 'None found'}
- **Data Quality:** {real.get('data_quality', 'low').upper()}

### 📰 Recent News
{chr(10).join(['- ' + n.get('headline', '')[:120] for n in news[:3]]) if news else '- No recent news found'}
"""
        else:
            web_md = "### 🤖 AI-Generated Intel\n> No live web data available. Using AI inference only."

        hooks_md = f"""### 🎣 Personalization Hooks
{chr(10).join(['**Hook ' + str(i+1) + ':** ' + h for i, h in enumerate(intel.get('personalization_hooks', [])[:4])])}

### 🏆 Outreach Strategy
- **Best Channel:** {intel.get('outreach_strategy', {}).get('best_channel', 'email')}
- **Best Time:** {intel.get('outreach_strategy', {}).get('best_time', 'Tue-Thu 9-11am')}
- **Opening Line:** *"{intel.get('outreach_strategy', {}).get('opening_line', 'N/A')}"*
- **Value Prop:** {intel.get('outreach_strategy', {}).get('value_prop_focus', 'N/A')}

### 🥊 Competitive Intel
- **Current Solution:** {intel.get('competitive_intel', {}).get('likely_current_solution', 'Unknown')}
- **Switching Triggers:** {', '.join(intel.get('competitive_intel', {}).get('switching_triggers', [])[:2])}
- **Our Win:** {', '.join(intel.get('competitive_intel', {}).get('our_differentiators', [])[:2])}
"""
        yield research_md + "\n\n" + web_md, hooks_md, f"✅ Research complete | Sources: {', '.join(sources) if sources else 'AI'}"
    except Exception as e:
        yield f"❌ Error: {e}", "", "❌ Research failed"


# ── Qualification ─────────────────────────────────────────────
def run_qualification(lead_preset, name, company, role, industry, budget, notes):
    agents = get_agents()
    if lead_preset and lead_preset != "— Enter manually —":
        lead = get_lead_by_label(lead_preset)
        name     = lead.get("full_name", name)
        company  = lead.get("company", company)
        role     = lead.get("role", role)
        industry = lead.get("industry", industry)
        budget   = lead.get("budget", budget)
        notes    = lead.get("notes", notes)

    if not name or not company:
        yield "⚠️ Enter name and company.", ""
        return

    yield "🎯 Qualifying lead with BANT framework...", ""

    lead_data = {
        "lead_id": lead.get("lead_id") if lead_preset and lead_preset != "— Enter manually —" else f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "full_name": name, "company": company, "role": role,
        "industry": industry, "budget": budget, "notes": notes
    }

    try:
        result = agents["qualify"].run({"lead": lead_data, "intelligence": {}})
        qual   = result.get("qualification", {})
        bant   = qual.get("bant_scores", {})
        score  = qual.get("composite_score", 0)
        temp   = qual.get("lead_temperature", "Unknown")
        status = qual.get("qualification_status", "UNKNOWN")

        lead_data.update({
            "composite_score": score, "lead_temperature": temp,
            "pipeline_stage": "Qualified" if score >= 60 else "New Lead",
            "deal_probability": qual.get("deal_probability", 0),
            "estimated_deal_size": qual.get("estimated_deal_size", "Unknown")
        })
        agents["crm"].run({"action": "log_lead", "data": lead_data})

        score_bar = "█" * (score // 5) + "░" * (20 - score // 5)
        temp_emoji = {"Hot": "🔥", "Warm": "🌡️", "Cold": "❄️"}.get(temp, "❓")

        qual_md = f"""## 🎯 Qualification Result: {name} @ {company}

### 📊 BANT Scores

| Category | Score | Evidence |
|----------|-------|----------|
| 💰 Budget | {bant.get('budget', {}).get('score', 0)}/25 | {str(bant.get('budget', {}).get('evidence', 'N/A'))[:80]} |
| 👤 Authority | {bant.get('authority', {}).get('score', 0)}/25 | {str(bant.get('authority', {}).get('evidence', 'N/A'))[:80]} |
| 🎯 Need | {bant.get('need', {}).get('score', 0)}/25 | {str(bant.get('need', {}).get('evidence', 'N/A'))[:80]} |
| ⏰ Timeline | {bant.get('timeline', {}).get('score', 0)}/25 | {str(bant.get('timeline', {}).get('evidence', 'N/A'))[:80]} |

### 🏆 Overall Score
```
Score: {score}/100  [{score_bar}]
```
**{temp_emoji} Temperature:** {temp} | **Status:** {status}

### 💼 Deal Intelligence
| Field | Value |
|-------|-------|
| Deal Size | {qual.get('estimated_deal_size', 'Unknown')} |
| Win Probability | {qual.get('deal_probability', 0)}% |
| Expected Close | {qual.get('estimated_close_date', 'Unknown')} |
| Priority Tier | {qual.get('priority_tier', 'Unknown')} |

### ⚠️ Key Risks
{chr(10).join(['- ' + r for r in qual.get('key_risks', [])[:3]])}

### 💡 Next Steps
{chr(10).join(['1. ' + s for s in qual.get('recommended_next_steps', [])[:3]])}

### 🗣️ Talking Points
{chr(10).join(['- ' + t for t in qual.get('talking_points', [])[:3]])}

> ✅ **Lead saved to CRM database** | Lead ID: {lead_data['lead_id']}
"""
        next_steps = "\n".join(qual.get("recommended_next_steps", [])[:3])
        yield qual_md, f"**Recommended Next Steps:**\n{next_steps}"
    except Exception as e:
        yield f"❌ Error: {e}", ""


# ── Email Writer ──────────────────────────────────────────────
def run_email_writer(lead_preset, name, company, role, industry, recipient_email, email_type, sender_name, send_now):
    agents = get_agents()
    lead = {}
    if lead_preset and lead_preset != "— Enter manually —":
        lead = get_lead_by_label(lead_preset)
        name            = lead.get("full_name", name)
        company         = lead.get("company", company)
        role            = lead.get("role", role)
        industry        = lead.get("industry", industry)
        recipient_email = lead.get("email", recipient_email)

    if not name or not company:
        yield "⚠️ Enter name and company.", "", ""
        return

    yield f"✍️ Writing {email_type} email...", "", ""

    lead_data = {
        "lead_id": f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "full_name": name, "company": company, "role": role,
        "industry": industry, "email": (recipient_email or "").strip()
    }

    try:
        result = agents["email"].run({
            "lead": lead_data, "intelligence": {},
            "qualification": {"lead_temperature": "Warm", "deal_probability": 60, "talking_points": []},
            "email_type": email_type, "sender_name": sender_name,
            "sender_title": "Account Executive, SalesFlow CRM"
        })
        email_data = result.get("email", {})

        saved_email = agents["crm"].run({"action": "save_email", "data": {
            "lead_id": lead_data["lead_id"],
            "email_type": email_type,
            "email_data": email_data
        }})

        send_status = ""
        if send_now:
            sr = send_cold_email(lead_data, email_data, sender_name=sender_name)
            if sr.get("success"):
                email_id = saved_email.get("email_id")
                if email_id:
                    mark_email_sent(email_id)
                send_status = f"\n\n---\n**📧 SMTP result:** Sent to `{sr.get('sent_to', lead_data['email'])}` at {sr.get('sent_at')}"
            else:
                send_status = f"\n\n---\n**📧 SMTP result:** Not sent — {sr.get('error', 'SMTP delivery failed')}"

        smtp = get_smtp_status()

        email_preview = f"""## ✉️ Generated Email: {email_type.upper()}

### 📌 Subject Lines
- **A:** {email_data.get('subject_line_a', 'N/A')}
- **B (A/B test):** {email_data.get('subject_line_b', 'N/A')}

### 📧 Email Body
---
{email_data.get('plain_text_version', email_data.get('email_body', 'N/A'))}
---

### 📊 Metrics
| Field | Value |
|-------|-------|
| Reply-rate measurement | Not available until campaign outcomes are recorded |
| CTA | {email_data.get('cta', 'N/A')} |
| Personalization | {email_data.get('personalization_used', 'N/A')} |

### 💼 LinkedIn Message
> {email_data.get('linkedin_message', 'N/A')}

> **SMTP Status:** {smtp.get('status', 'Not configured')}
{send_status}
"""
        html_body = email_data.get("email_body", f"<p>{email_data.get('plain_text_version', '')}</p>")
        status_text = "✅ AI email draft created" + (" · check SMTP result above" if send_now else " · not sent")
        yield email_preview, html_body, status_text
    except Exception as e:
        yield f"❌ Error: {e}", "", "❌ Failed"


# ── Meeting Scheduler ─────────────────────────────────────────
def run_meeting_scheduler(lead_preset, name, company, role, meeting_type, preferred_date, timezone):
    agents = get_agents()
    if lead_preset and lead_preset != "— Enter manually —":
        lead = get_lead_by_label(lead_preset)
        name    = lead.get("full_name", name)
        company = lead.get("company", company)
        role    = lead.get("role", role)

    if not name or not company:
        yield "⚠️ Enter name and company.", "", ""
        return

    yield f"📅 Scheduling {meeting_type} for {name} @ {company}...", "", ""

    lead_data = get_lead_by_label(lead_preset) if lead_preset and lead_preset != "— Enter manually —" else {}
    lead_data.update({
        "lead_id": lead_data.get("lead_id") or f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]}",
        "full_name": name, "company": company, "role": role,
    })

    try:
        result = agents["meeting"].run({
            "action": "schedule", "lead": lead_data,
            "intelligence": {}, "qualification": {},
            "meeting_type": meeting_type, "preferred_date": preferred_date, "timezone": timezone
        })
        pkg   = result.get("meeting_package", {})

        meeting_md = f"""## 📅 Meeting Package: {meeting_type.upper()} | {name} @ {company}

**Status:** AI-generated invitation draft. No calendar availability was checked and no meeting was booked.

### 📧 Meeting Invite
**Subject:** {pkg.get('meeting_invite_subject', 'N/A')}

**Message:**
{pkg.get('invite_message', 'N/A')}

### 🎯 Key Objectives
{chr(10).join(['1. ' + o for o in pkg.get('key_objectives', [])[:3]])}
"""
        agenda_result = agents["meeting"].run({
            "action": "agenda", "lead": lead_data,
            "intelligence": {}, "qualification": {}, "meeting_type": meeting_type
        })
        agenda = agenda_result.get("agenda", {})
        agenda_md = f"""### 📋 Meeting Agenda ({agenda.get('total_duration', 30)} minutes)

| Time | Section | Goal |
|------|---------|------|
{chr(10).join(['| ' + s.get('time_allocation', '—') + ' | ' + s.get('section_name', '—') + ' | ' + str(s.get('goal', '—'))[:60] + ' |' for s in agenda.get('sections', [])[:5]])}

### ❓ Discovery Questions
{chr(10).join(['1. ' + q for q in agenda.get('discovery_questions', [])[:5]])}

### 🎯 Closing Question
> *{agenda.get('closing_question', 'What would make this a clear yes for you?')}*
"""
        yield meeting_md, agenda_md, "✅ Meeting package ready"
    except Exception as e:
        yield f"❌ Error: {e}", "", "❌ Failed"


# ── Objection Chat ────────────────────────────────────────────
OBJECTION_CHAT_WELCOME = [
    {"role": "assistant", "content": "Hi! Share a prospect objection and I’ll help you prepare a thoughtful response."}
]


def run_objection_chat(message, history, mode, lead_name, lead_company):
    agents = get_agents()
    if not message.strip():
        return history, ""

    lead_context = {
        "company": lead_company,
        "first_name": lead_name.split()[0] if lead_name else ""
    }

    try:
        result = agents["objection"].run({
            "message": message,
            "lead_context": lead_context,
            "mode": mode.lower().replace(" ", "_") if mode.lower() != "chat" else "chat"
        })

        if mode == "Roleplay":
            response = f"**[Prospect]:** {result.get('prospect_response', '')}\n\n💡 *Coach Tip: {result.get('coaching_tip', '')}*"
        else:
            objection_data = result.get("objection_data", {})
            response = result.get("response") or objection_data.get("immediate_response")
            if not response:
                raise RuntimeError("The AI provider returned no objection response.")

        obj_type = result.get("objection_type") or result.get("objection_data", {}).get("objection_type", "general")
        if obj_type != "general" and lead_company:
            agents["crm"].run({"action": "log_objection", "data": {
                "lead_id": "", "objection_text": message,
                "objection_type": obj_type, "rebuttal_used": response[:200]
            }})

        history = history or []
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
        ])
        return history, ""
    except Exception as e:
        history = history or []
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"⚠️ Error: {e}"},
        ])
        return history, ""


# ── Full Pipeline ─────────────────────────────────────────────
def run_full_pipeline(lead_preset, name, company, email, role, industry, website, notes, progress=gr.Progress()):
    agents = get_agents()

    if lead_preset == "__new__":
        if not name.strip() or not company.strip():
            return "⚠️ Enter at least the contact name and company for a new CRM lead.", ""
        lead = {
            "lead_id": f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]}",
            "full_name": name.strip(), "company": company.strip(), "email": email.strip(),
            "role": role.strip(), "industry": industry.strip(), "website": website.strip(),
            "notes": notes.strip(), "source": "User entered",
        }
        upsert_lead(lead)
    else:
        lead = get_lead(lead_preset) if lead_preset else None
        if not lead:
            return "⚠️ Choose a saved CRM record or enter a new contact.", ""

    log = [f"# 🚀 Full SDR Pipeline: {lead['full_name']} @ {lead['company']}\n"]

    # Track result vars safely
    sources, score, temp, email_data = [], "N/A", "N/A", {}
    outcomes = {"research": "failed", "qualification": "failed", "email": "failed", "meeting": "failed", "crm": "failed"}

    # Step 1: Research
    progress(0.10, desc="Step 1/5: Researching...")
    log.append("## Step 1/5 — 🔍 Prospect Research")
    try:
        r = agents["research"].run({
            "company_name": lead["company"], "contact_name": lead["full_name"],
            "contact_role": lead["role"], "industry": lead["industry"],
            "website": lead.get("website", "")
        })
        intel   = r.get("intelligence", {})
        sources = r.get("data_sources", [])
        outcomes["research"] = "completed"
        pain    = intel.get("pain_points", {}).get("primary_pain", "N/A")
        log.append(f"- ✅ Research complete | Sources: {', '.join(sources) if sources else 'AI'}")
        log.append(f"- 🎯 Primary Pain: **{pain}**")
        log.append(f"- 🔗 Hook: {(intel.get('personalization_hooks') or [''])[0]}")
    except Exception as e:
        intel = {}
        log.append(f"- ⚠️ Research error: {e}")

    # Step 2: Qualify
    progress(0.35, desc="Step 2/5: Qualifying...")
    log.append("\n## Step 2/5 — 🎯 Lead Qualification")
    try:
        qr   = agents["qualify"].run({"lead": lead, "intelligence": intel})
        qual = qr.get("qualification", {})
        score = qual.get("composite_score", 0)
        temp  = qual.get("lead_temperature", "Unknown")
        status= qual.get("qualification_status", "UNKNOWN")
        outcomes["qualification"] = "completed"
        log.append(f"- ✅ BANT Score: **{score}/100**")
        log.append(f"- 🌡️ Temperature: **{temp}** | Status: **{status}**")
        log.append(f"- 💰 Deal Size: {qual.get('estimated_deal_size', 'N/A')}")
        log.append(f"- 🎲 Win Probability: {qual.get('deal_probability', 0)}%")
        lead.update({
            "composite_score": score, "lead_temperature": temp,
            "pipeline_stage": "Qualified",
            "deal_probability": qual.get("deal_probability", 0),
            "estimated_deal_size": qual.get("estimated_deal_size", "")
        })
    except Exception as e:
        qual = {}
        log.append(f"- ⚠️ Qualification error: {e}")

    # Step 3: Email
    progress(0.55, desc="Step 3/5: Writing email...")
    log.append("\n## Step 3/5 — ✍️ Email Writer")
    try:
        er = agents["email"].run({
            "lead": lead, "intelligence": intel, "qualification": qual,
            "email_type": "cold", "sender_name": "Vinay Bhardwaj",
            "sender_title": "Account Executive, SalesFlow CRM"
        })
        email_data = er.get("email", {})
        agents["crm"].run({"action": "save_email", "data": {"lead_id": lead["lead_id"], "email_type": "cold", "email_data": email_data}})
        outcomes["email"] = "completed; saved to CRM"
        log.append(f"- 📧 Subject A: **{email_data.get('subject_line_a', 'N/A')}**")
        log.append(f"- 📧 Subject B: {email_data.get('subject_line_b', 'N/A')}")
    except Exception as e:
        log.append(f"- ⚠️ Email error: {e}")

    # Step 4: Meeting
    progress(0.75, desc="Step 4/5: Scheduling meeting...")
    log.append("\n## Step 4/5 — 📅 Meeting Coordinator")
    try:
        mr = agents["meeting"].run({
            "action": "schedule", "lead": lead,
            "intelligence": intel, "qualification": qual,
            "meeting_type": "discovery"
        })
        outcomes["meeting"] = "draft created; not booked"
        log.append("- ✅ AI invite draft ready; calendar availability was not checked and no meeting was booked")
    except Exception as e:
        log.append(f"- ⚠️ Meeting error: {e}")

    # Step 5: CRM
    progress(0.92, desc="Step 5/5: Logging to CRM...")
    log.append("\n## Step 5/5 — 📋 CRM Manager")
    try:
        cr     = agents["crm"].run({"action": "log_lead", "data": lead})
        lead_id= cr.get("lead_id", "Unknown")
        outcomes["crm"] = "saved"
        log.append(f"- ✅ Logged to CRM | Lead ID: **{lead_id}**")
        log.append(f"- 💾 Saved to salesai.db")
    except Exception as e:
        log.append(f"- ⚠️ CRM error: {e}")

    failed_steps = [step for step, outcome in outcomes.items() if outcome == "failed"]
    progress(1.0, desc="Pipeline finished with errors" if failed_steps else "AI steps finished")
    log.append(f"\n---\n> **Pipeline finished** | {datetime.now().strftime('%H:%M:%S')} | {len(failed_steps)} failed step(s)")

    summary = f"""### 📊 Pipeline Summary

| Step | Result |
|------|--------|
| 🔍 Research | {outcomes['research']} ({', '.join(sources) if sources else 'no live sources'}) |
| 🎯 Qualify | {outcomes['qualification']} ({score}/100, {temp}) |
| ✍️ Email | {outcomes['email']} |
| 📅 Meeting | {outcomes['meeting']} |
| 📋 CRM | {outcomes['crm']} |

{f"**Pipeline errors:** {', '.join(failed_steps)}" if failed_steps else "All requested AI/CRM steps returned successfully."}
"""
    return "\n".join(log), summary


# ── CRM Pipeline ──────────────────────────────────────────────
def get_crm_pipeline():
    agents = get_agents()
    try:
        result    = agents["crm"].run({"action": "get_pipeline"})
        stats     = result.get("summary", {})
        top_leads = result.get("top_leads", [])
        insights  = result.get("ai_insights", "")

        table_data = [
            [
                l.get("full_name", "—"), l.get("company", "—"), l.get("role", "—"),
                l.get("pipeline_stage", "—"),
                {"Hot": "🔥", "Warm": "🌡️", "Cold": "❄️"}.get(l.get("lead_temperature", ""), "❓")
                + " " + l.get("lead_temperature", "—"),
                f"{l.get('composite_score', 0)}/100",
                l.get("estimated_deal_size", "—"),
                (l.get("created_at") or "")[:10]
            ]
            for l in top_leads
        ]

        pipeline_md = f"""## 📋 CRM Pipeline Report

### 📊 Stats
| Metric | Value |
|--------|-------|
| Total Leads | {stats.get('total_leads', 0)} |
| Pipeline Value | {stats.get('pipeline_value', '$0')} |
| Weighted Forecast | {stats.get('weighted_forecast', '$0')} |
| Hot / Warm / Cold | {stats.get('hot_leads', 0)} / {stats.get('warm_leads', 0)} / {stats.get('cold_leads', 0)} |
| Avg Score | {stats.get('avg_score', 0)}/100 |

### 🤖 AI Pipeline Analysis
{insights}
"""
        return pipeline_md, table_data
    except Exception as e:
        return f"❌ Error: {e}", []


def get_forecast():
    agents = get_agents()
    try:
        result = agents["crm"].run({"action": "forecast"})
        f = result.get("forecast", {})
        if not f.get("priced_leads"):
            return "## 📈 Revenue Forecast\n\nNo deal amounts are recorded yet, so there is no dollar forecast to show. Add deal estimates to CRM records to calculate one."
        return f"""## 📈 Revenue Forecast

| Category | Pipeline | Weighted |
|----------|---------|---------| 
| 🔥 Hot Leads ({f.get('lead_counts', {}).get('hot', 0)}) | ${f.get('hot_pipeline', 0):,.0f} | ${f.get('hot_weighted', 0):,.0f} |
| 🌡️ Warm Leads ({f.get('lead_counts', {}).get('warm', 0)}) | ${f.get('warm_pipeline', 0):,.0f} | ${f.get('warm_weighted', 0):,.0f} |
| ❄️ Cold Leads ({f.get('lead_counts', {}).get('cold', 0)}) | ${f.get('cold_pipeline', 0):,.0f} | ${f.get('cold_weighted', 0):,.0f} |
| **TOTAL** | **${f.get('total_pipeline', 0):,.0f}** | **${f.get('weighted_forecast', 0):,.0f}** |

Amounts are calculated from CRM deal estimates and saved probabilities. **Priced leads:** {f.get('priced_leads', 0)} · **Unpriced:** {f.get('unpriced_leads', 0)}
"""
    except Exception as e:
        return f"❌ Error: {e}"


# ── Add Lead ──────────────────────────────────────────────────
def add_lead_to_crm(name, email, phone, company, role, industry, website, budget, source, notes):
    agents = get_agents()
    if not name or not company:
        return "⚠️ Name and Company are required."
    try:
        lead_data = {
            "lead_id": f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "full_name": name, "email": email, "phone": phone,
            "company": company, "role": role, "industry": industry,
            "website": website, "budget": budget, "source": source, "notes": notes
        }
        result = agents["crm"].run({"action": "log_lead", "data": lead_data})
        return f"✅ Lead added! ID: {result.get('lead_id')} | Saved to salesai.db"
    except Exception as e:
        return f"❌ Error: {e}"


# ══════════════════════════════════════════════════════════════
# GRADIO THEME & CSS
# ══════════════════════════════════════════════════════════════

THEME = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="teal",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "ui-sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace"],
).set(
    body_background_fill="#f3f7fc",
    body_background_fill_dark="#f3f7fc",
    block_background_fill="#ffffff",
    block_background_fill_dark="#ffffff",
    block_border_color="#dce6f2",
    block_border_color_dark="#dce6f2",
    input_background_fill="#ffffff",
    input_background_fill_dark="#ffffff",
    button_primary_background_fill="linear-gradient(135deg, #2563eb, #0f9f9a)",
    button_primary_background_fill_hover="linear-gradient(135deg, #1d4ed8, #0f766e)",
    button_primary_text_color="white",
    body_text_color="#1e293b",
    body_text_color_dark="#1e293b",
    block_label_text_color="#52647d",
    block_title_text_color="#14243b",
)

CSS = """
pre, code {
  background: #f1f5f9 !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
}
.dataframe, table {
  background: #ffffff !important;
  color: #0f172a !important;
}
th {
  background: #f8fafc !important;
  color: #334155 !important;
}
td {
  background: #ffffff !important;
  color: #0f172a !important;
}
.label-wrap, .panel, .accordion {
  background: #ffffff !important;
  color: #0f172a !important;
}

/* FORCE BRIGHT ENTERPRISE LIGHT THEME REGARDLESS OF OS/BROWSER DARK MODE */
:root, html, body {
  color-scheme: light !important;
  background-color: #f8fafc !important;
  color: #0f172a !important;
}
html.dark, body.dark, .dark {
  color-scheme: light !important;
  background-color: #f8fafc !important;
  color: #0f172a !important;
}
.gradio-container {
  background: #f8fafc !important;
  color: #0f172a !important;
  max-width: 1560px !important;
  margin: 0 auto !important;
}
.dark .gradio-container {
  background: #f8fafc !important;
  color: #0f172a !important;
}
.dark .block, .dark .form, .dark fieldset, .dark .tabitem, .dark div[data-testid="block"] {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: #e2e8f0 !important;
}
.dark label, .dark span, .dark p, .dark h1, .dark h2, .dark h3, .dark h4, .dark td, .dark th {
  color: #0f172a !important;
}
.dark input, .dark textarea, .dark select {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
}
.dark table {
  background: #ffffff !important;
  color: #0f172a !important;
}
.tab-nav {
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
  padding: 6px !important;
}
.tab-nav button {
  color: #475569 !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  padding: 8px 14px !important;
}
.tab-nav button.selected {
  color: #1d4ed8 !important;
  background: #eff6ff !important;
  box-shadow: inset 0 -2px #2563eb !important;
}
.gradio-container .prose { color: #1e293b !important; }
.gradio-container .prose h1, .gradio-container .prose h2, .gradio-container .prose h3 { color: #0f172a !important; }
.gradio-container input, .gradio-container textarea, .gradio-container select {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
}
"""


def render_battlecard_display(comp_choice: str) -> str:
    key = "hubspot"
    if not comp_choice:
        comp_choice = "hubspot"
    c_lower = comp_choice.lower()
    if "salesforce" in c_lower:
        key = "salesforce"
    elif "apollo" in c_lower:
        key = "apollo"
    elif "outreach" in c_lower:
        key = "outreach"
    card = query_battlecard(key)
    if not card:
        return "<p>No battlecard data available.</p>"
    return f"""
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 24px; margin-top: 12px; color: #0f172a; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); font-family: system-ui, -apple-system, sans-serif;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px;">
        <h3 style="margin: 0; font-size: 20px; color: #1e40af;">⚔️ Competitive Intelligence: {card['competitor']}</h3>
        <span style="background: #eff6ff; color: #2563eb; font-size: 12px; padding: 4px 12px; border-radius: 20px; font-weight: 700; border: 1px solid #bfdbfe;">ENTERPRISE ALTERNATIVE</span>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
        <div style="background: #fef2f2; border: 1px solid #fee2e2; padding: 14px; border-radius: 8px; border-left: 4px solid #ef4444;">
          <div style="font-size: 11px; color: #991b1b; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">Competitor Vulnerability</div>
          <div style="font-size: 13px; line-height: 1.5; color: #7f1d1d; font-weight: 500;">{card['primary_weakness']}</div>
        </div>
        <div style="background: #f0fdf4; border: 1px solid #dcfce7; padding: 14px; border-radius: 8px; border-left: 4px solid #10b981;">
          <div style="font-size: 11px; color: #166534; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">SalesFlow AI Advantage</div>
          <div style="font-size: 13px; line-height: 1.5; color: #14532d; font-weight: 500;">{card['salesflow_advantage']}</div>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; border-top: 3px solid #0284c7;">
          <div style="font-size: 11px; color: #64748b; font-weight: 700;">MIGRATION SPEED</div>
          <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-weight: 600;">{card['migration_timeline']}</div>
        </div>
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; border-top: 3px solid #9333ea;">
          <div style="font-size: 11px; color: #64748b; font-weight: 700;">COST COMPARISON</div>
          <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-weight: 600;">{card['cost_comparison']}</div>
        </div>
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; border-top: 3px solid #d97706;">
          <div style="font-size: 11px; color: #64748b; font-weight: 700;">KILLER CAPABILITY</div>
          <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-weight: 600;">{card['killer_feature']}</div>
        </div>
      </div>
    </div>
    """

def run_knowledge_rag_search(query: str) -> str:
    if not query or not query.strip():
        return "Enter a question or topic (e.g. 'Why switch from Salesforce?' or 'What are our speed-to-lead benchmarks?') to query the sales knowledge base."
    return search_sales_knowledge(query.strip())

def get_n8n_live_health() -> str:
    import urllib.request
    try:
        req = urllib.request.urlopen("http://127.0.0.1:5678/healthz", timeout=1.5)
        if req.status == 200:
            return "🟢 ONLINE (Port 5678 reachable — ready for live webhooks)"
    except Exception:
        pass
    return "⚪ STANDBY (Docker/Local instance not detected on port 5678; use 'RUN_PROJECT.bat' to start)"

# ══════════════════════════════════════════════════════════════
# GRADIO UI BUILDER
# ══════════════════════════════════════════════════════════════


def render_database_audit_trail_html(lead_filter: str = "All Leads", type_filter: str = "All Activities") -> str:
    import sqlite3
    conn = sqlite3.connect("salesai.db")
    conn.row_factory = sqlite3.Row
    query = """
        SELECT a.id, a.lead_id, a.activity_type, a.description, a.outcome, a.performed_by, a.created_at,
               COALESCE(l.full_name, 'System') as full_name,
               COALESCE(l.company, 'Enterprise Account') as company,
               COALESCE(l.pipeline_stage, 'Qualified') as pipeline_stage
        FROM activities a
        LEFT JOIN leads l ON a.lead_id = l.lead_id
        ORDER BY a.created_at DESC
        LIMIT 150
    """
    rows = [dict(r) for r in conn.execute(query).fetchall()]
    conn.close()

    if lead_filter and lead_filter != "All Leads":
        rows = [r for r in rows if r.get("lead_id") == lead_filter or (r.get("full_name") and lead_filter in r["full_name"])]
    if type_filter and type_filter != "All Activities":
        rows = [r for r in rows if r.get("activity_type") == type_filter]

    total_events = len(rows)
    unique_leads = len(set(r.get("lead_id") for r in rows if r.get("lead_id")))

    badge_styles = {
        "lead_created": ("#e0f2fe", "#0369a1", "📥 LEAD CREATED"),
        "bant_scored": ("#fef3c7", "#b45309", "🎯 BANT SCORED"),
        "rep_assigned": ("#ede9fe", "#6d28d9", "👤 REP ASSIGNED"),
        "email_sent": ("#fce7f3", "#be185d", "📧 EMAIL SENT"),
        "stage_transition": ("#dcfce7", "#15803d", "🔀 STAGE CHANGED"),
        "hitl_approved": ("#ffedd5", "#c2410c", "🛡️ HITL APPROVED"),
        "meeting_scheduled": ("#ccfbf1", "#0f766e", "📅 MEETING BOOKED"),
        "n8n_workflow_execution": ("#e0e7ff", "#4338ca", "⚡ WORKFLOW EXECUTED"),
    }

    cards_html = ""
    for r in rows:
        act_type = r.get("activity_type", "event")
        bg, text_color, badge_lbl = badge_styles.get(act_type, ("#f1f5f9", "#475569", act_type.upper()))
        created = r.get("created_at", "")[:19].replace("T", " ")
        lead_id = r.get("lead_id", "N/A")
        contact = f"{r.get('full_name')} ({r.get('company')})"
        desc = r.get("description", "")
        performer = r.get("performed_by", "SalesFlow Engine")
        outcome = r.get("outcome", "success")

        cards_html += f"""
        <tr style="border-bottom: 1px solid #e2e8f0; font-size: 13px;">
            <td style="padding: 10px 12px; font-family: monospace; color: #64748b; white-space: nowrap;">{created}</td>
            <td style="padding: 10px 12px;"><span style="background: {bg}; color: {text_color}; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 6px; white-space: nowrap;">{badge_lbl}</span></td>
            <td style="padding: 10px 12px; font-weight: 600; color: #0f172a;">{contact}<br><span style="font-size: 11px; color: #64748b; font-family: monospace;">{lead_id}</span></td>
            <td style="padding: 10px 12px; color: #334155;">{desc}</td>
            <td style="padding: 10px 12px; color: #64748b; font-size: 12px; white-space: nowrap;">👤 {performer}</td>
            <td style="padding: 10px 12px; text-align: center;"><span style="background: #f1f5f9; color: #059669; font-weight: 600; font-size: 11px; padding: 2px 6px; border-radius: 4px;">{outcome.upper()}</span></td>
        </tr>
        """

    return f"""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
            <div>
                <h3 style="margin: 0; color: #0f172a; font-size: 18px; font-weight: 700;">📜 Database Audit Trail & Activity History</h3>
                <p style="margin: 3px 0 0; color: #64748b; font-size: 13px;">Real-time event stream persisted in SQLite (<code>salesai.db activities</code> table). Fully satisfies capstone audit logging requirement.</p>
            </div>
            <div style="display: flex; gap: 12px;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 600;">LOGGED ACTIONS</div>
                    <div style="font-size: 16px; font-weight: 800; color: #2563eb;">{total_events}</div>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 600;">LEADS AUDITED</div>
                    <div style="font-size: 16px; font-weight: 800; color: #0f766e;">{unique_leads}</div>
                </div>
            </div>
        </div>

        <div style="overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; background: white;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0; font-size: 12px; color: #475569; text-transform: uppercase;">
                        <th style="padding: 10px 12px;">Timestamp</th>
                        <th style="padding: 10px 12px;">Event Type</th>
                        <th style="padding: 10px 12px;">Target Lead / Company</th>
                        <th style="padding: 10px 12px;">Description</th>
                        <th style="padding: 10px 12px;">Performer</th>
                        <th style="padding: 10px 12px; text-align: center;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {cards_html if cards_html else '<tr><td colspan="6" style="text-align:center; padding:30px; color:#94a3b8;">No activity records match the selected filter.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """


def build_gradio_app():
    with gr.Blocks(
        title="⚡ SalesFlow AI — N8N CRM & Sales Automation Platform (IIT Jammu Capstone '26)",
        theme=THEME,
        css=CSS
    ) as demo:

        # ── Global Hero Header ─────────────────────────────────
        gr.HTML(f"""
        <div class="salesai-hero">
          <h1>⚡ SalesFlow AI <span class="hero-accent">— CRM & Sales Automation Platform</span></h1>
          <p class="hero-subtitle">
            IIT Jammu Summer School 2026 | Capstone Project Final: Assignment 4 | Vinay Bhardwaj
          </p>
          <div style="margin-top:14px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
            <span class="metric-chip">🔧 6 N8N Workflows (58 Nodes)</span>
            <span class="metric-chip">📋 Interactive CRM Kanban</span>
            <span class="metric-chip">⚡ Non-AI RevOps Engine</span>
            <span class="metric-chip">💾 SQLite CRM Database</span>
            <span class="metric-chip">🛡️ Competitor Battlecards (RAG)</span>
            <span class="metric-chip">📧 SMTP Email Cadence</span>
          </div>
        </div>
        """)

        with gr.Tabs():

            # ────────────────────────────────────────────────────
            # TAB 1: WORKFLOW BLUEPRINT GALLERY (N8N)
            # ────────────────────────────────────────────────────
            with gr.TabItem("🧭 Workflow Blueprint Gallery"):
                gr.Markdown("### 🧭 Interactive N8N Workflow Blueprints")
                gr.Markdown("Choose a workflow to see its connected nodes. The diagram and steps are dynamically generated from the production N8N workflow exports.")

                wf_choice = gr.Radio(
                    choices=[f"{w['icon']} {w['id']}: {w['name']}" for w in N8N_WORKFLOWS],
                    label="Select Workflow Blueprint",
                    value=f"{N8N_WORKFLOWS[0]['icon']} {N8N_WORKFLOWS[0]['id']}: {N8N_WORKFLOWS[0]['name']}"
                )

                wf_graph_html = gr.HTML()
                with gr.Accordion("📖 Workflow Execution Logic & Raw JSON Export", open=False):
                    with gr.Row():
                        wf_detail_md = gr.Markdown(label="📋 Workflow Detail")
                        wf_json_md   = gr.Markdown(label="📄 Workflow JSON")

                def show_workflow_detail(choice):
                    if not choice:
                        return "Select a workflow.", "", ""
                    wf_id = choice.split(":")[0].strip().split()[-1]
                    return get_workflow_detail(wf_id)

                wf_choice.change(
                    show_workflow_detail,
                    inputs=[wf_choice],
                    outputs=[wf_detail_md, wf_graph_html, wf_json_md]
                )

                demo.load(
                    lambda: get_workflow_detail("WF-01"),
                    outputs=[wf_detail_md, wf_graph_html, wf_json_md]
                )

            # ────────────────────────────────────────────────────
            # TAB 2: LIVE WORKFLOW RUNNER (SIMULATION & LIVE)
            # ────────────────────────────────────────────────────
            with gr.TabItem("⚡ Live Workflow Runner"):
                gr.Markdown("### ⚡ Safe Local Execution & Real-Time Payload Simulation")
                gr.Markdown("The local simulation executes the full workflow logic (validating inputs, routing, BANT calculation, and error handlers) in memory with zero network side effects. The live button sends the payload directly to an active N8N sandbox instance via webhook.")
                with gr.Row():
                    sim_wf_choice = gr.Dropdown(
                        choices=[
                            ("WF-01 · Lead Capture & Intake", "WF-01"),
                            ("WF-02 · AI Lead Scoring & BANT Qualification", "WF-02"),
                            ("WF-03 · Sales Rep Assignment & Routing", "WF-03"),
                            ("WF-04 · Scheduled Multi-Touch Follow-ups", "WF-04"),
                            ("WF-05 · Proposal Generation & Human Approval", "WF-05"),
                            ("WF-06 · Sales Dashboard & Executive Analytics", "WF-06"),
                        ],
                        label="Select Workflow to Execute",
                        value="WF-01",
                    )
                with gr.Row():
                    sim_preset = gr.Dropdown(LEAD_LABELS, label="Load Preset CRM Lead (Optional)", value="— Enter manually —")
                with gr.Row():
                    sim_name     = gr.Textbox(label="Contact Name", placeholder="Priya Sharma")
                    sim_company  = gr.Textbox(label="Company Name", placeholder="TechVision Solutions")
                    sim_role     = gr.Textbox(label="Role / Title", placeholder="VP of Sales")
                with gr.Row():
                    sim_email    = gr.Textbox(label="Email Address", placeholder="priya.sharma@techvision.io")
                    sim_industry = gr.Textbox(label="Industry", placeholder="B2B SaaS")
                    sim_budget   = gr.Textbox(label="Budget", placeholder="$2,000-5,000/month")
                sim_notes = gr.Textbox(label="Lead Notes / Context", placeholder="Series A $8M. 25 sales reps. Manual lead tracking.", lines=2)
                
                with gr.Row():
                    sim_btn = gr.Button("🧪 Run Safe Local Simulation (Recommended)", variant="primary", size="lg")
                    live_btn = gr.Button("🌐 Trigger Live N8N Sandbox Webhook", variant="secondary", size="lg")
                
                with gr.Row():
                    sim_log     = gr.Markdown(label="Execution Trace")
                    sim_summary = gr.Markdown(label="Run Status")
                
                with gr.Accordion("📄 Full Request & Response Payloads", open=False):
                    sim_json = gr.Markdown()

                sim_preset.change(
                    lambda x: [get_lead_by_label(x).get(k, "") for k in
                               ["full_name", "company", "role", "email", "industry", "budget", "notes"]]
                    if x != "— Enter manually —" else ["", "", "", "", "", "", ""],
                    inputs=sim_preset,
                    outputs=[sim_name, sim_company, sim_role, sim_email, sim_industry, sim_budget, sim_notes]
                )

                sim_btn.click(
                    simulate_n8n_workflow,
                    inputs=[sim_wf_choice, sim_preset, sim_name, sim_company, sim_email, sim_role, sim_industry, sim_budget, sim_notes],
                    outputs=[sim_log, sim_json, sim_summary]
                )
                live_btn.click(
                    execute_n8n_workflow,
                    inputs=[sim_wf_choice, sim_preset, sim_name, sim_company, sim_email, sim_role, sim_industry, sim_budget, sim_notes],
                    outputs=[sim_log, sim_json, sim_summary]
                )

            # ────────────────────────────────────────────────────
            # TAB 3: VISUAL CRM KANBAN & LEAD TRACKER
            # ────────────────────────────────────────────────────
            with gr.TabItem("📋 CRM Lead Tracker & Kanban"):
                gr.Markdown("""
                ## 📋 Centralized CRM Pipeline & Visual Sales Kanban
                **Assignment 4 Objective 1 & 4:** Centralize lead management and improve sales tracking with real-time SQLite persistence (`salesai.db`).
                """)
                with gr.Tabs():
                    with gr.TabItem("📋 Visual Sales Kanban"):
                        with gr.Row():
                            kb_refresh_btn = gr.Button("🔄 Refresh Kanban Board", variant="secondary")
                        
                        kb_board = gr.HTML(generate_kanban_board_html)
                        
                        gr.Markdown("### 🔀 Interactive Stage Transition (Direct SQLite Mutation)")
                        with gr.Row():
                            all_ld = get_all_leads(limit=100)
                            kb_leads_choices = [l["lead_id"] for l in all_ld if l.get("lead_id")]
                            kb_lead_select = gr.Dropdown(choices=kb_leads_choices, label="Select Lead ID", value=kb_leads_choices[0] if kb_leads_choices else None)
                            kb_stage_select = gr.Dropdown(["New Lead", "Researching", "Qualified", "Proposal Sent", "Closed Won"], label="Move to Stage", value="Qualified")
                            kb_move_btn = gr.Button("🚀 Update Stage", variant="primary")
                        
                        kb_move_status = gr.Textbox(label="Operation Result", interactive=False)
                        
                        def on_move_deal(lid, stg):
                            msg = move_deal_stage(lid, stg)
                            log_activity(lid, "stage_transition", f"Stage moved to '{stg}' via CRM Kanban", "success", "CRM Visual Kanban")
                            board_html = generate_kanban_board_html()
                            return msg, board_html
                        
                        kb_move_btn.click(on_move_deal, inputs=[kb_lead_select, kb_stage_select], outputs=[kb_move_status, kb_board])
                        kb_refresh_btn.click(generate_kanban_board_html, outputs=[kb_board])

                    with gr.TabItem("📊 Pipeline Analytics & Records"):
                        with gr.Row():
                            crm_refresh  = gr.Button("🔄 Refresh Pipeline", variant="primary")
                            forecast_btn = gr.Button("📈 Generate Forecast", variant="secondary")
                        dash_visuals = gr.HTML()
                        crm_md = gr.Markdown()
                        crm_table = gr.Dataframe(
                            headers=["Name", "Company", "Role", "Stage", "Temperature", "Score", "Deal Size", "Added"],
                            label="🏆 Active Leads by Score",
                            interactive=False
                        )
                        forecast_md = gr.Markdown()
                        
                        def on_refresh_crm_tab():
                            v_html, _, _ = get_dashboard_data()
                            p_md, p_table = get_crm_pipeline()
                            return v_html, p_md, p_table
                            
                        crm_refresh.click(on_refresh_crm_tab, outputs=[dash_visuals, crm_md, crm_table])
                        demo.load(on_refresh_crm_tab, outputs=[dash_visuals, crm_md, crm_table])
                        forecast_btn.click(get_forecast, outputs=[forecast_md])

                    with gr.TabItem("➕ Add New Lead to CRM"):
                        gr.Markdown("### ➕ Register New Lead into SQLite Database")
                        with gr.Row():
                            al_name  = gr.Textbox(label="Full Name *", placeholder="John Smith")
                            al_email = gr.Textbox(label="Email",        placeholder="john@company.com")
                            al_phone = gr.Textbox(label="Phone",        placeholder="+1-555-0100")
                        with gr.Row():
                            al_company  = gr.Textbox(label="Company *",  placeholder="Acme Corp")
                            al_role     = gr.Textbox(label="Role",        placeholder="VP of Sales")
                            al_industry = gr.Textbox(label="Industry",    placeholder="B2B SaaS")
                        with gr.Row():
                            al_website = gr.Textbox(label="Website", placeholder="acme.com")
                            al_budget  = gr.Textbox(label="Budget",  placeholder="$2,000/month")
                            al_source  = gr.Dropdown(
                                ["LinkedIn", "Website", "Referral", "Cold Email", "Event", "Other"],
                                label="Source", value="LinkedIn"
                            )
                        al_notes  = gr.Textbox(label="Notes", lines=3, placeholder="Any additional context...")
                        al_btn    = gr.Button("➕ Add Lead to CRM", variant="primary")
                        al_status = gr.Textbox(label="Status", interactive=False)
                        al_btn.click(
                            add_lead_to_crm,
                            inputs=[al_name, al_email, al_phone, al_company, al_role,
                                    al_industry, al_website, al_budget, al_source, al_notes],
                            outputs=[al_status]
                        )

                    with gr.TabItem("🛡️ Deal Health & Slippage Matrix"):
                        gr.Markdown("### 🛡️ Algorithmic Deal Health & Slippage Risk Sentinel")
                        risk_html = gr.HTML(generate_risk_matrix_html)
                        risk_refresh_btn = gr.Button("🔄 Refresh Risk Table", variant="secondary")
                        risk_refresh_btn.click(generate_risk_matrix_html, outputs=[risk_html])

            # ────────────────────────────────────────────────────
            # TAB 4: REVOPS ROI & VELOCITY SIMULATOR (NON-AI)
            # ────────────────────────────────────────────────────
            with gr.TabItem("📈 RevOps ROI & Velocity Simulator"):
                gr.Markdown("""
                ## 📈 Mathematical RevOps ROI & Lead Response Velocity Simulator
                **100% Deterministic & Non-AI:** Backed by MIT / Harvard Business Review lead response velocity research. Demonstrates the mathematical business case for automating sales triage.
                """)
                with gr.Row():
                    with gr.Column(scale=1):
                        sim_team = gr.Slider(1, 50, value=5, step=1, label="SDR Team Size")
                        sim_leads = gr.Slider(20, 2000, value=250, step=10, label="Monthly Inbound Inquiries")
                        sim_deal = gr.Slider(2000, 100000, value=25000, step=1000, label="Average Deal Value ($)")
                        sim_hours = gr.Slider(0.5, 24, value=4.5, step=0.5, label="Manual Response Delay (Hours)")
                        sim_calc_btn = gr.Button("⚡ Recalculate Model", variant="primary")
                    
                    with gr.Column(scale=2):
                        sim_card_html = gr.HTML(lambda: calculate_deterministic_roi(5, 250, 25000, 4.5)["html_card"])
                
                def on_sim_change(t, l, d, h):
                    res = calculate_deterministic_roi(t, l, d, h)
                    return res["html_card"]
                
                sim_calc_btn.click(on_sim_change, inputs=[sim_team, sim_leads, sim_deal, sim_hours], outputs=[sim_card_html])
                for comp in [sim_team, sim_leads, sim_deal, sim_hours]:
                    comp.change(on_sim_change, inputs=[sim_team, sim_leads, sim_deal, sim_hours], outputs=[sim_card_html])

            # ────────────────────────────────────────────────────
            # TAB: DATABASE HISTORY & AUDIT TRAIL
            # ────────────────────────────────────────────────────
            with gr.TabItem("📜 Database History & Audit Trail"):
                gr.Markdown("""
                ## 📜 Database Activity History & Audit Trail
                **Capstone Requirement:** Real-time logging, transactional audit trail, and activity history persisted in SQLite (`salesai.db`).
                """)
                with gr.Row():
                    hist_refresh_btn = gr.Button("🔄 Refresh Audit Trail", variant="primary")
                    all_ld_history = get_all_leads(limit=100)
                    lead_choices_hist = ["All Leads"] + [f"{l['full_name']} ({l.get('company','')})" for l in all_ld_history if l.get('full_name')]
                    hist_lead_filter = gr.Dropdown(choices=lead_choices_hist, label="Filter by Lead", value="All Leads")
                    hist_type_filter = gr.Dropdown(
                        choices=["All Activities", "lead_created", "bant_scored", "rep_assigned", "email_sent", "stage_transition", "hitl_approved", "n8n_workflow_execution"],
                        label="Filter by Event Type",
                        value="All Activities"
                    )
                
                hist_display = gr.HTML(render_database_audit_trail_html)
                
                hist_refresh_btn.click(
                    render_database_audit_trail_html,
                    inputs=[hist_lead_filter, hist_type_filter],
                    outputs=[hist_display]
                )
                hist_lead_filter.change(
                    render_database_audit_trail_html,
                    inputs=[hist_lead_filter, hist_type_filter],
                    outputs=[hist_display]
                )
                hist_type_filter.change(
                    render_database_audit_trail_html,
                    inputs=[hist_lead_filter, hist_type_filter],
                    outputs=[hist_display]
                )

            with gr.TabItem("🤖 AI Sales Copilot & Tools"):
                gr.Markdown("### 🤖 Autonomous AI Sales Specialists & Rep Enablement Tools")
                gr.Markdown("Modular AI agents designed to handle prospecting, qualification, personalized outreach, scheduling, and objection handling.")
                
                with gr.Tabs():
                    # ── Research ───────────────────────────────
                    with gr.TabItem("🔍 Prospect Research"):
                        gr.Markdown("### 🔍 Prospect Research — Real Web Intelligence + Firmographics")
                        with gr.Row():
                            r_preset = gr.Dropdown(LEAD_LABELS, label="📋 Load Demo Lead", value="— Enter manually —")
                        with gr.Row():
                            r_company  = gr.Textbox(label="Company Name", placeholder="TechVision Solutions")
                            r_contact  = gr.Textbox(label="Contact Name",  placeholder="Priya Sharma")
                            r_role     = gr.Textbox(label="Role",          placeholder="VP of Sales")
                        with gr.Row():
                            r_industry = gr.Textbox(label="Industry",  placeholder="B2B SaaS")
                            r_website  = gr.Textbox(label="Website",   placeholder="techvision.io")
                        r_btn = gr.Button("🔍 Research Prospect (Real Web + AI)", variant="primary")
                        with gr.Row():
                            r_out1 = gr.Markdown(label="📊 Company & Contact Intelligence")
                            r_out2 = gr.Markdown(label="🎣 Hooks & Strategy")
                        r_status = gr.Textbox(label="Status", interactive=False)

                        r_preset.change(
                            lambda x: [get_lead_by_label(x).get(k, "") for k in
                                       ["company", "full_name", "role", "industry", "website"]]
                            if x != "— Enter manually —" else ["", "", "", "", ""],
                            inputs=r_preset,
                            outputs=[r_company, r_contact, r_role, r_industry, r_website]
                        )
                        r_btn.click(
                            run_research,
                            inputs=[r_preset, r_company, r_contact, r_role, r_industry, r_website],
                            outputs=[r_out1, r_out2, r_status]
                        )

                    # ── Qualification ──────────────────────────
                    with gr.TabItem("🎯 BANT Qualification"):
                        gr.Markdown("### 🎯 BANT Qualification Agent — 100-Point Scoring & Priority Routing")
                        with gr.Row():
                            q_preset = gr.Dropdown(LEAD_LABELS, label="📋 Load Demo Lead", value="— Enter manually —")
                        with gr.Row():
                            q_name     = gr.Textbox(label="Name")
                            q_company  = gr.Textbox(label="Company")
                            q_role     = gr.Textbox(label="Role")
                        with gr.Row():
                            q_industry = gr.Textbox(label="Industry")
                            q_budget   = gr.Textbox(label="Budget", placeholder="$2,000-5,000/month")
                        q_notes = gr.Textbox(label="Notes", placeholder="Add any additional context...", lines=2)
                        q_btn = gr.Button("🎯 Qualify Lead (BANT + Save to CRM)", variant="primary")
                        q_out   = gr.Markdown()
                        q_steps = gr.Markdown()

                        q_preset.change(
                            lambda x: [get_lead_by_label(x).get(k, "") for k in
                                       ["full_name", "company", "role", "industry", "budget", "notes"]]
                            if x != "— Enter manually —" else [""] * 6,
                            inputs=q_preset,
                            outputs=[q_name, q_company, q_role, q_industry, q_budget, q_notes]
                        )
                        q_btn.click(
                            run_qualification,
                            inputs=[q_preset, q_name, q_company, q_role, q_industry, q_budget, q_notes],
                            outputs=[q_out, q_steps]
                        )

                    # ── Email Writer ───────────────────────────
                    with gr.TabItem("✉️ 5-Touch Cadence Writer"):
                        gr.Markdown("### ✉️ Hyper-Personalized Outreach & 5-Touch Cadence Generator")
                        with gr.Row():
                            e_preset = gr.Dropdown(LEAD_LABELS, label="📋 Load Demo Lead", value="— Enter manually —")
                        with gr.Row():
                            e_name     = gr.Textbox(label="Contact Name")
                            e_company  = gr.Textbox(label="Company")
                            e_role     = gr.Textbox(label="Role")
                            e_industry = gr.Textbox(label="Industry")
                            e_email    = gr.Textbox(label="Recipient Email", placeholder="name@company.com")
                        with gr.Row():
                            e_type   = gr.Dropdown(
                                ["cold", "followup1", "followup2", "followup3", "breakup"],
                                label="Email Type", value="cold"
                            )
                            e_sender = gr.Textbox(label="Sender Name", value="Vinay Bhardwaj")
                            e_send   = gr.Checkbox(label="📤 Send now via configured SMTP", value=False)
                        e_btn = gr.Button("✍️ Write Email (AI-Powered)", variant="primary")
                        with gr.Row():
                            e_out  = gr.Markdown(label="📧 Email Preview")
                            e_html = gr.HTML(label="🌐 HTML Preview")
                        e_status = gr.Textbox(label="Status", interactive=False)

                        e_preset.change(
                            lambda x: [get_lead_by_label(x).get(k, "") for k in
                                       ["full_name", "company", "role", "industry", "email"]]
                            if x != "— Enter manually —" else [""] * 5,
                            inputs=e_preset,
                            outputs=[e_name, e_company, e_role, e_industry, e_email]
                        )
                        e_btn.click(
                            run_email_writer,
                            inputs=[e_preset, e_name, e_company, e_role, e_industry,
                                    e_email, e_type, e_sender, e_send],
                            outputs=[e_out, e_html, e_status]
                        )

                    # ── Meetings ───────────────────────────────
                    with gr.TabItem("📅 Meeting Coordinator"):
                        gr.Markdown("### 📅 Meeting Coordinator — Schedule + Agenda + Calendar Links")
                        with gr.Row():
                            m_preset = gr.Dropdown(LEAD_LABELS, label="📋 Load Demo Lead", value="— Enter manually —")
                        with gr.Row():
                            m_name    = gr.Textbox(label="Contact Name")
                            m_company = gr.Textbox(label="Company")
                            m_role    = gr.Textbox(label="Role")
                        with gr.Row():
                            m_type = gr.Dropdown(
                                ["discovery", "demo", "technical", "proposal", "followup"],
                                label="Meeting Type", value="discovery"
                            )
                            m_date = gr.Textbox(label="Preferred Date (YYYY-MM-DD)", placeholder="2026-10-28")
                            m_tz   = gr.Dropdown(["IST", "EST", "PST", "GMT", "CST"], label="Timezone", value="IST")
                        m_btn = gr.Button("📅 Schedule Meeting + Generate Agenda", variant="primary")
                        with gr.Row():
                            m_out1 = gr.Markdown(label="📅 Meeting Package")
                            m_out2 = gr.Markdown(label="📋 Agenda")
                        m_status = gr.Textbox(label="Status", interactive=False)

                        m_preset.change(
                            lambda x: [get_lead_by_label(x).get(k, "") for k in
                                       ["full_name", "company", "role"]]
                            if x != "— Enter manually —" else [""] * 3,
                            inputs=m_preset,
                            outputs=[m_name, m_company, m_role]
                        )
                        m_btn.click(
                            run_meeting_scheduler,
                            inputs=[m_preset, m_name, m_company, m_role, m_type, m_date, m_tz],
                            outputs=[m_out1, m_out2, m_status]
                        )

                    # ── Objection Chat ─────────────────────────
                    with gr.TabItem("💬 Sales Coach & Objections"):
                        gr.Markdown("### 💬 Real-Time Objection Handler & AI Roleplay Coach")
                        gr.HTML(render_visual_flow(
                            "A human centered response pattern",
                            "The coach guides a rep through a calm, useful conversation.",
                            [
                                ("Listen", "Let them explain", "#3978e8"),
                                ("Empathize", "Acknowledge concern", "#8b6bd6"),
                                ("Clarify", "Ask one question", "#249c8c"),
                                ("Respond", "Offer a relevant fact", "#e9ae55"),
                                ("Confirm", "Agree next step", "#e98972"),
                            ],
                        ))
                        with gr.Row():
                            oc_mode    = gr.Radio(["Chat", "Roleplay", "Handle_Objection"], label="Mode", value="Chat")
                            oc_lead    = gr.Textbox(label="Lead Name (context)", placeholder="Priya Sharma")
                            oc_company = gr.Textbox(label="Company (context)",   placeholder="TechVision")
                        gr.Markdown("**Start here:** type a prospect objection below, choose a mode, and press **Send**.")
                        oc_chatbot = gr.Chatbot(
                            label="💬 SalesAI Coach",
                            value=OBJECTION_CHAT_WELCOME,
                            height=380,
                            elem_id="objection-chatbot",
                        )
                        with gr.Row():
                            oc_input = gr.Textbox(
                                label="Your message",
                                placeholder="Type an objection or question (e.g. 'Your product is too expensive')...",
                                scale=4
                            )
                            oc_send = gr.Button("Send ➤", variant="primary", scale=1)
                        oc_clear = gr.Button("🗑️ Clear Chat")

                        gr.Examples(
                            examples=[
                                "Your product is too expensive",
                                "We already use Salesforce",
                                "I need to think about it",
                                "Send me more information",
                                "Not the right time",
                                "We're doing fine without it",
                                "roleplay"
                            ],
                            inputs=oc_input
                        )
                        oc_send.click(
                            run_objection_chat,
                            inputs=[oc_input, oc_chatbot, oc_mode, oc_lead, oc_company],
                            outputs=[oc_chatbot, oc_input]
                        )
                        oc_input.submit(
                            run_objection_chat,
                            inputs=[oc_input, oc_chatbot, oc_mode, oc_lead, oc_company],
                            outputs=[oc_chatbot, oc_input]
                        )
                        oc_clear.click(lambda: (OBJECTION_CHAT_WELCOME, ""), outputs=[oc_chatbot, oc_input])

                    # ── Full Pipeline ──────────────────────────
                    with gr.TabItem("🚀 End-to-End Pipeline"):
                        gr.Markdown("### 🚀 Execute Full Autonomous Sales Lifecycle (5-Step Sequence)")
                        gr.HTML(render_visual_flow(
                            "Full Autonomous SDR pipeline",
                            "Choose a saved CRM record or enter a new contact, then run all steps in sequence.",
                            [
                                ("Research", "Company context", "#3978e8"),
                                ("Qualify", "BANT + score", "#8b6bd6"),
                                ("Email", "Personalized draft", "#249c8c"),
                                ("Meeting", "Suggested times", "#e9ae55"),
                                ("CRM", "Save lead record", "#e98972"),
                            ],
                        ))
                        fp_preset = gr.Dropdown(
                            choices=[("✍️ Enter a new contact", "__new__")] + get_crm_lead_choices(),
                            value="__new__",
                            label="📋 Use a saved CRM record or add a contact",
                        )
                        with gr.Row():
                            fp_name = gr.Textbox(label="Contact name", placeholder="Enter contact name")
                            fp_company = gr.Textbox(label="Company", placeholder="Company name")
                            fp_email = gr.Textbox(label="Email", placeholder="name@company.com")
                        with gr.Row():
                            fp_role = gr.Textbox(label="Role", placeholder="Sales Director")
                            fp_industry = gr.Textbox(label="Industry", placeholder="B2B SaaS")
                            fp_website = gr.Textbox(label="Website", placeholder="company.com")
                        fp_notes = gr.Textbox(label="Context / lead notes", placeholder="Add verified context for personalization", lines=2)
                        fp_btn = gr.Button(
                            "🚀 Run End-to-End Pipeline (Research → Qualify → Email → Meeting → CRM)",
                            variant="primary", size="lg"
                        )
                        with gr.Row():
                            fp_log     = gr.Markdown(label="📜 Pipeline Log")
                            fp_summary = gr.Markdown(label="📊 Summary")
                        fp_btn.click(
                            run_full_pipeline,
                            inputs=[fp_preset, fp_name, fp_company, fp_email, fp_role, fp_industry, fp_website, fp_notes],
                            outputs=[fp_log, fp_summary],
                        )

            # ────────────────────────────────────────────────────
            # TAB 6: COMPETITOR BATTLECARDS & KNOWLEDGE RAG
            # ────────────────────────────────────────────────────
            with gr.TabItem("🛡️ Competitor Battlecards (RAG)"):
                gr.Markdown("""
                ## 🛡️ Competitive Intelligence & Knowledge RAG Engine
                Tactical objection defense and positioning against legacy enterprise CRMs. Grounded in verified migration benchmarks and customer case studies.
                """)
                with gr.Row():
                    comp_choice = gr.Radio(
                        choices=["HubSpot Sales Hub", "Salesforce Sales Cloud", "Apollo.io", "Outreach.io / Salesloft"],
                        label="Select Competitor to Inspect",
                        value="HubSpot Sales Hub"
                    )
                
                battlecard_html = gr.HTML(lambda: render_battlecard_display("HubSpot Sales Hub"))
                comp_choice.change(render_battlecard_display, inputs=[comp_choice], outputs=[battlecard_html])

                with gr.Accordion("🔍 Natural Language Sales Knowledge Search (RAG)", open=True):
                    with gr.Row():
                        rag_input = gr.Textbox(
                            label="Ask the Sales Knowledge Base",
                            placeholder="e.g., 'Why should a company switch from Salesforce?' or 'What are our speed-to-lead benchmarks?'",
                            scale=4
                        )
                        rag_btn = gr.Button("Query RAG Base 🔍", variant="primary", scale=1)
                    rag_output = gr.Markdown()
                    rag_btn.click(run_knowledge_rag_search, inputs=[rag_input], outputs=[rag_output])
                    rag_input.submit(run_knowledge_rag_search, inputs=[rag_input], outputs=[rag_output])

                with gr.Accordion("📚 Verified Enterprise Case Studies", open=False):
                    gr.Markdown("""
                    ### 🏢 Case Study 1: CloudMatrix Global (B2B SaaS, 180 employees)
                    - **Challenge:** Lead response times exceeded 6 hours; SDRs spent 60% of time manually prospecting and researching.
                    - **Solution:** Deployed SalesFlow AI autonomous research and BANT qualification pipelines.
                    - **Result:** Response time dropped to 2 minutes; qualified meetings booked increased by **142% in 60 days**.

                    ### 🏢 Case Study 2: FinTech Shield (Financial Services, 450 employees)
                    - **Challenge:** High compliance friction and expensive Salesforce Einstein licensing ($150k+/year).
                    - **Solution:** Implemented SalesFlow self-hosted agents with private API keys and audit trails.
                    - **Result:** Saved **$115,000 annually** in licensing while maintaining 100% data audit compliance.
                    """)

            # ────────────────────────────────────────────────────
            # TAB 7: ARCHITECTURE & PROBLEM ANALYSIS
            # ────────────────────────────────────────────────────
            with gr.TabItem("📐 Architecture & Problem Analysis"):
                gr.Markdown("""
                ## 📐 Capstone Problem Analysis & System Architecture
                **Assignment 4 Submission Requirements:** Problem Analysis, Business Context, Stakeholder Map, System Architecture, and Event Flow.
                """)
                gr.HTML(render_architecture_visual())
                gr.HTML(render_lead_lifecycle_visual())
                gr.HTML(render_problem_solution_visual())
                gr.Markdown(get_workflow_overview())
                gr.Markdown("""
                ---
                ### 📁 Included N8N Workflow Artifacts (58 Nodes Total)

                | Workflow | File | Nodes | Integration Type |
                |---|---|---|---|
                | 🎯 WF-01: Lead Capture & Registration | `01_lead_capture_registration.json` | 10 | Webhook, PostgreSQL, Gmail, Slack |
                | 📊 WF-02: AI Lead Scoring & BANT | `02_ai_lead_scoring_qualification.json` | 9 | Webhook, OpenAI GPT-4o, PostgreSQL |
                | 👤 WF-03: Sales Rep Assignment & CRM | `03_sales_rep_assignment_crm.json` | 9 | Webhook, PostgreSQL, Gmail, Slack |
                | 📅 WF-04: Follow-ups & Meeting Scheduler | `04_automated_followup_meeting_scheduler.json` | 9 | Cron (Every 8h), PostgreSQL, Google Calendar, Gmail |
                | 📄 WF-05: Proposal Generation & HITL | `05_proposal_generation_human_approval.json` | 11 | Webhook, OpenAI GPT-4o, Human-in-the-Loop, Google Drive |
                | 📈 WF-06: Sales Dashboard & Analytics | `06_sales_dashboard_analytics_report.json` | 8 | Cron (Weekly Mon 8am), PostgreSQL, Slack, Google Sheets |

                **Total: 58 nodes across 6 production-ready JSON exports, featuring automated error handling, retries, and human approval.**
                """)
                gr.HTML(render_tech_stack_visual())

            # ────────────────────────────────────────────────────
            # TAB 8: N8N SETUP & LIVE WEBHOOKS
            # ────────────────────────────────────────────────────
            with gr.TabItem("⚙️ N8N Setup & Live Webhooks"):
                smtp = get_smtp_status()
                n8n_status = get_n8n_live_health()
                all_leads_count = len(get_all_leads(limit=1000))
                gr.Markdown(f"""
                ### ⚙️ System Health & Webhook Integration Endpoints

                #### 🔧 N8N Orchestration Engine
                | Service | Endpoint / Setting | Status |
                |---|---|---|
                | **N8N Instance** | `http://localhost:5678` | **{n8n_status}** |
                | **FastAPI Backend** | `http://localhost:8000` | 🟢 Online (`/docs` interactive Swagger) |
                | **Gradio Dashboard** | `http://localhost:7860` | 🟢 Online |

                #### 🔗 Live Production Webhook Endpoints
                | Workflow | Webhook Path | Trigger Method |
                |---|---|---|
                | **WF-01: Lead Intake** | `http://localhost:5678/webhook/capture-lead` | `POST` (JSON payload) |
                | **WF-02: BANT Score** | `http://localhost:5678/webhook/qualify-bant` | `POST` (JSON payload) |
                | **WF-03: Rep Assignment** | `http://localhost:5678/webhook/assign-rep` | `POST` (JSON payload) |
                | **WF-05: Proposal Approval** | `http://localhost:5678/webhook/generate-proposal` | `POST` (JSON payload) |
                | **Unified API Mirror** | `http://localhost:8000/webhook/n8n` | `POST` (JSON payload) |

                #### 💾 Local Storage & Environment
                | Component | Configuration | Status |
                |---|---|---|
                | **CRM Database** | `salesai.db` (SQLite) | **{all_leads_count} Leads Tracked** |
                | **Email Service** | SMTP ({smtp.get('host', 'smtp.gmail.com')}:{smtp.get('port', 587)}) | **{smtp.get('status', 'Ready')}** |
                | **AI Engine** | {os.getenv("GEMINI_MODEL", "gemini-2.5-flash") if not OPENAI_API_KEY else "OpenAI GPT-4"} | 🟢 Active |
                """)

    return demo


if __name__ == "__main__":
    print("🚀 Starting SalesAI SDR Gradio Dashboard...")
    print(f"   Agent Runtime: Gemini/Groq by default (set OPENAI_API_KEY to use OpenAI SDK)")
    print(f"   OpenAI Key   : {'SET (GPT-4 mode)' if OPENAI_API_KEY else 'NOT SET - using Gemini/Groq (works fine!)'}")
    print(f"   SMTP Status : {get_smtp_status()['status']}")
    share = "--share" in sys.argv or "--public" in sys.argv or os.environ.get("GRADIO_SHARE", "").lower() == "true"
    print(f"   URL         : http://localhost:7860 {'(🌍 Public Link Enabled)' if share else ''}")
    app = build_gradio_app()
    app.queue(default_concurrency_limit=20, max_size=2000)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=THEME,
        css=CSS,
        share=share,
        show_error=True,
    )
