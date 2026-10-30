"""
SalesAI SDR — Full Gradio Dashboard (IIT Jammu Capstone 2026)
=============================================================
Author  : Vinay Bhardwaj
Course  : IIT Jammu Summer School 2026

Tab 1 — SalesFlow N8N  : 6 automated sales workflows (N8N + GPT-4o)
Tab 2 — SalesAI Agents : 6 OpenAI Agents SDK specialists
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
from tools.crm_database import get_all_leads, get_pipeline_stats, upsert_lead, get_lead, init_database, mark_email_sent, estimate_deal_amount
from tools.email_sender import send_cold_email, get_smtp_status

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
        "nodes": 9,
        "icon": "🎯",
        "desc": "Instant AI-powered lead intake. GPT-4o scores lead on arrival, saves to PostgreSQL, sends branded welcome email via Gmail, emits Slack alert for Hot Leads.",
        "steps": [
            "1. Webhook receives lead (name, email, company, industry, notes)",
            "2. Set Node normalises & validates payload fields",
            "3. GPT-4o Scoring — structured JSON schema prompt → 0-100 score",
            "4. PostgreSQL INSERT into `leads` table with generated lead_id",
            "5. Gmail API — branded HTML welcome email to prospect",
            "6. IF Node — temperature gate (Hot / Warm / Cold)",
            "7. Slack webhook → #hot-leads-alert channel for Hot leads",
            "8. HTTP Response Node — returns JSON 200 {lead_id, score}",
        ],
        "color": "#6366f1",
    },
    {
        "id": "WF-02",
        "file": "02_ai_lead_scoring_qualification.json",
        "name": "AI Lead Scoring & BANT Qualification",
        "trigger": "Webhook POST /qualify-lead",
        "nodes": 8,
        "icon": "📊",
        "desc": "Full BANT matrix evaluation. GPT-4o analyses Budget, Authority, Need, Timeline against ICP criteria and routes Qualified leads forward, Nurture leads to Google Sheets.",
        "steps": [
            "1. Webhook receives lead_id for qualification",
            "2. PostgreSQL SELECT — fetch lead history & activity log",
            "3. GPT-4o BANT prompt — returns structured JSON scores (0-25 each)",
            "4. Composite score calculation (Budget+Authority+Need+Timeline)",
            "5. Switch Router — ≥70 → Qualified, 40-69 → Warm Nurture, <40 → Cold",
            "6. PostgreSQL UPDATE lead status + bant_score + qualification_at",
            "7. Google Sheets append — cold/warm leads to nurture pipeline sheet",
            "8. HTTP Response — returns qualification result with next steps",
        ],
        "color": "#ec4899",
    },
    {
        "id": "WF-03",
        "file": "03_sales_rep_assignment_crm.json",
        "name": "Sales Rep Assignment & CRM Update",
        "trigger": "Webhook POST /assign-rep",
        "nodes": 8,
        "icon": "👤",
        "desc": "Smart round-robin + skill-matched rep assignment. Balances workload, matches industry expertise, emails assigned rep with an AI-crafted outreach script.",
        "steps": [
            "1. Webhook receives qualified lead_id",
            "2. PostgreSQL SELECT reps — fetch all active reps + open deal counts",
            "3. Matching matrix — workload balance + industry match + tier bonus",
            "4. Assign lowest-load rep with best industry fit",
            "5. PostgreSQL UPDATE lead record — assigned_rep, assigned_at",
            "6. GPT-4o — craft personalised outreach script for the rep",
            "7. Gmail → assigned rep with lead brief + AI-written intro script",
            "8. Slack → #sales-assignments with assignment notification",
        ],
        "color": "#06b6d4",
    },
    {
        "id": "WF-04",
        "file": "04_automated_followup_meeting_scheduler.json",
        "name": "Automated Follow-ups & Meeting Scheduler",
        "trigger": "⏰ Cron — Every 8 hours",
        "nodes": 8,
        "icon": "📅",
        "desc": "5-touch cadence engine runs every 8h. GPT-4o crafts touch-specific copy (Intro → Value-Add → Social Proof → Urgency → Breakup). Touch #1 auto-books a discovery slot via Google Calendar.",
        "steps": [
            "1. Cron trigger — fires every 8 hours, 24/7",
            "2. PostgreSQL SELECT — leads due for next touch (hours_since_assign > threshold AND touch_count < 5)",
            "3. Split In Batches — process leads in groups of 10",
            "4. GPT-4o copywriting — Intro / Value-Add / Social Proof / Urgency / Breakup email",
            "5. Gmail API — send personalised email for each lead",
            "6. IF touch_count == 1 → Google Calendar API auto-book discovery slot",
            "7. PostgreSQL UPDATE — increment touch_count, set last_contact_at",
            "8. Log activity in PostgreSQL activities table",
        ],
        "color": "#10b981",
    },
    {
        "id": "WF-05",
        "file": "05_proposal_generation_human_approval.json",
        "name": "AI Proposal Generation & HITL Approval",
        "trigger": "Webhook POST /generate-proposal",
        "nodes": 10,
        "icon": "📄",
        "desc": "GPT-4o generates a full responsive HTML proposal, saves to Google Drive, then PAUSES — waits for human manager approval via a clickable token link. Approved = email sent. Rejected = flagged for revision.",
        "steps": [
            "1. Webhook — receives lead_id for proposal generation",
            "2. PostgreSQL SELECT — fetch company data, financials, BANT scores",
            "3. GPT-4o — render full responsive HTML proposal with pricing table",
            "4. Google Drive — save proposal file with versioning",
            "5. Gmail → Sales Manager — send email with Approve / Reject token links",
            "6. n8n Wait Node — workflow PAUSES until manager clicks a token",
            "7. IF Approved → Gmail → prospect with proposal PDF link",
            "8. IF Rejected → PostgreSQL flag for revision, Slack notify rep",
            "9. PostgreSQL UPDATE — proposal_status, approved_at / rejected_at",
            "10. HTTP Response — return final status to calling system",
        ],
        "color": "#f59e0b",
    },
    {
        "id": "WF-06",
        "file": "06_sales_dashboard_analytics_report.json",
        "name": "Sales Dashboard & Weekly Analytics",
        "trigger": "⏰ Cron — Every Monday 08:00 AM",
        "nodes": 7,
        "icon": "📈",
        "desc": "Weekly executive briefing engine. Aggregates 7-day SQL metrics, GPT-4o synthesizes insights, updates Google Sheets KPI dashboard, delivers HTML report via Gmail + Slack.",
        "steps": [
            "1. Cron trigger — every Monday 08:00 AM",
            "2. PostgreSQL aggregations — Leads captured, Win rates, Rep leaderboard, Pipeline value",
            "3. GPT-4o — executive synthesis (wins, risks, recommendations, forecast)",
            "4. Google Sheets UPDATE — KPI metrics to weekly dashboard tab",
            "5. Build HTML email report with charts and data tables",
            "6. Gmail → leadership team with branded executive report",
            "7. Slack → #sales-leadership with summary and Google Sheets link",
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
            ("6 N8N flows", "50 exported nodes", "#8b6bd6"),
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
    provider = "OPENAI AGENTS SDK" if OPENAI_API_KEY else "OPENAI KEY REQUIRED"
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
| 🔧 Total Workflow Nodes | **56 Nodes** |
| 🤖 AI node in exports | **OpenAI / GPT-4o node configuration** |
| 💾 Database node in exports | **PostgreSQL** |
| 📧 Other configured services | **Gmail, Google APIs, Slack** |

The running Python dashboard is a separate part of the project: its six SalesAI specialists use the OpenAI Agents SDK and local SQLite CRM. The dashboard simulator does not execute the external n8n integrations.
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
    """Render a local, read-only trace from the exported JSON; never calls n8n or external services."""
    wf_id = wf_choice.split(":")[0].strip() if ":" in wf_choice else wf_choice.strip()
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
        node_type = node.get("type", "unknown").split(".")[-1]
        lowered = node_type.lower()
        if any(service in lowered for service in ("gmail", "slack", "googlesheets", "googlecalendar", "googledrive")):
            detail = "External action represented only; nothing was sent, scheduled, or stored remotely."
        elif "postgres" in lowered or "database" in lowered:
            detail = "Database action represented only; no database was read or changed."
        elif "openai" in lowered or "httprequest" in lowered:
            detail = "Provider/API step represented only; no model or external API was called."
        elif "webhook" in lowered or "schedule" in lowered:
            detail = "Trigger represented locally; no webhook or schedule was started."
        elif "wait" in lowered:
            detail = "Approval pause represented only; no approval request was sent."
        else:
            detail = "Logic step represented from the exported workflow definition."
        trace.append({
            "step": index,
            "node": node.get("name", f"Node {index}"),
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
    return (
        f"### {wf_id} local simulation trace\n\nThis trace is derived from the exported JSON. It does not represent a live n8n execution.\n\n```json\n{details}\n```",
        f"```json\n{json.dumps(telemetry, indent=2, ensure_ascii=False)}\n```",
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
    """Send a live n8n webhook only after explicit opt-in and synthetic-recipient validation."""
    if os.getenv("N8N_ALLOW_LIVE_EXECUTION", "false").strip().lower() not in {"1", "true", "yes"}:
        return (
            "### Live n8n execution is disabled\n\nSet `N8N_ALLOW_LIVE_EXECUTION=true` only for a configured sandbox instance. The local simulation is available without it.",
            "",
            "**Live execution:** not sent — explicit sandbox opt-in is required.",
        )

    import requests

    webhook_paths = {
        "WF-01": "capture-lead",
        "WF-02": "qualify-lead",
        "WF-03": "assign-rep",
        "WF-05": "generate-proposal",
    }
    if wf_id in {"WF-04", "WF-06"}:
        return (
            f"### {wf_id} uses a schedule trigger\n\nNo live request was sent. Inspect scheduled runs from a sandbox n8n instance.",
            "",
            "**Live execution:** not sent — schedule-triggered workflow.",
        )
    if wf_id not in webhook_paths:
        return "### Unsupported workflow trigger", "", "**Live execution:** not sent."
    if wf_id == "WF-01" and os.getenv("N8N_WF01_DUPLICATE_PATH_RESOLVED", "false").strip().lower() not in {"1", "true", "yes"}:
        return (
            "### WF-01 live request blocked\n\nThe active n8n instance currently has another workflow using the same `capture-lead` webhook path. Resolve the duplicate path and verify the route before enabling WF-01 live execution.",
            "",
            "**Live execution:** not sent — webhook path is ambiguous.",
        )

    lead = _workflow_lead(
        lead_label, custom_name, custom_company, custom_email, custom_role,
        custom_industry, custom_budget, custom_notes,
    )
    email = str(lead.get("email") or "").strip().lower()
    if not email.endswith("@example.com"):
        return (
            "### Live sandbox test blocked\n\nUse a synthetic recipient ending in `@example.com`. Saved CRM contacts outside that domain are never submitted by this runner.",
            "",
            "**Live execution:** not sent — recipient must be synthetic.",
        )

    base_url = os.getenv("N8N_WEBHOOK_URL", "").strip().rstrip("/")
    if not base_url:
        return "### N8N is not connected", "", "**Live execution:** not sent — webhook URL is not configured."

    lead_id = lead.get("lead_id") or f"LEAD-TEST-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    payload = {
        "lead_id": lead_id,
        "name": lead.get("full_name"),
        "full_name": lead.get("full_name"),
        "email": email,
        "company": lead.get("company"),
        "role": lead.get("role", ""),
        "industry": lead.get("industry", ""),
        "budget": lead.get("budget", ""),
        "notes": lead.get("notes", ""),
        "message": lead.get("notes", "") or "Synthetic sandbox test inquiry",
        "source": "Synthetic sandbox test",
    }
    headers = {"Content-Type": "application/json", "ngrok-skip-browser-warning": "1", "User-Agent": "SalesAI-Capstone/1.0"}
    url = f"{base_url}/{webhook_paths[wf_id]}"
    last_response = None
    last_error = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        last_response = (response, url)
    except requests.RequestException as exc:
        last_error = str(exc)

    if last_response is None:
        return (
            "### Live n8n request failed\n\nNo endpoint returned an HTTP response. Check the sandbox URL and n8n logs.",
            "",
            f"**Live execution:** failed before HTTP response ({escape(last_error or 'connection error')}).",
        )

    response, url = last_response
    try:
        body = response.json()
    except ValueError:
        body = {"response_text": response.text[:4000]}
    telemetry = {
        "http_status": response.status_code,
        "endpoint": url,
        "workflow": wf_id,
        "mode": "LIVE_SANDBOX_WEBHOOK",
        "recipient_domain": "example.com",
        "response": body,
    }
    status = "completed" if response.ok else "failed"
    return (
        f"### {wf_id} live sandbox webhook response\n```json\n{json.dumps(body, indent=2, ensure_ascii=False)[:8000]}\n```",
        f"```json\n{json.dumps(telemetry, indent=2, ensure_ascii=False)[:8000]}\n```",
        f"**Live sandbox execution:** HTTP `{response.status_code}` · **{status.upper()}** · `{escape(url)}`",
    )


# ══════════════════════════════════════════════════════════════
# ██████████  TAB 2 — AI AGENTS — HANDLER FUNCTIONS  █████████
# ══════════════════════════════════════════════════════════════

# ── Dashboard ─────────────────────────────────────────────────
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

> **Agent Runtime:** OpenAI Agents SDK ({os.getenv('OPENAI_AGENT_MODEL', 'gpt-4.1-mini')}) | **DB:** salesai.db | **Refreshed:** {datetime.now().strftime("%H:%M:%S")}
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
.gradio-container { background: linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%) !important; color: #1e293b !important; max-width: 1500px !important; }
body { background: #f3f7fc !important; }
footer { display: none !important; }
.tab-nav { background: rgba(255,255,255,.92) !important; border: 1px solid #dce6f2 !important; border-radius: 14px !important; box-shadow: 0 5px 18px rgba(31,67,115,.06) !important; padding: 5px !important; }
.tab-nav button { color: #52647d !important; font-weight: 650 !important; font-size: 13px !important; border-radius: 10px !important; }
.tab-nav button.selected { color: #174ea6 !important; background: #eaf2ff !important; box-shadow: inset 0 -2px #3978e8 !important; }
.gradio-container .prose { color: #334155 !important; }
.gradio-container .prose h1, .gradio-container .prose h2, .gradio-container .prose h3 { color: #14243b !important; }
.gradio-container .prose a { color: #2563eb !important; }
.gradio-container input, .gradio-container textarea, .gradio-container select { background: #fff !important; color: #1e293b !important; border-color: #d4dfed !important; }
.gradio-container input:focus, .gradio-container textarea:focus { border-color: #4b83eb !important; box-shadow: 0 0 0 3px rgba(59,130,246,.12) !important; }
.gradio-container button.primary { border: 0 !important; box-shadow: 0 5px 12px rgba(37,99,235,.18) !important; }
.gradio-container button.secondary { background: #eaf2ff !important; color: #1e4f91 !important; border-color: #d6e4f7 !important; }
.gradio-container .block { border-radius: 14px !important; }
.salesai-hero { position: relative; overflow: hidden; isolation: isolate; background: linear-gradient(115deg,#fff 0%,#f1f7ff 52%,#eefaf8 100%); border: 1px solid #d7e5f3; border-radius: 22px; padding: 28px 32px; margin: 4px 0 20px; box-shadow: 0 12px 32px rgba(41,72,112,.08); }
.salesai-hero:after { content: ""; position: absolute; width: 260px; height: 260px; border-radius: 50%; right: -80px; top: -150px; z-index: -1; background: radial-gradient(circle,rgba(56,189,178,.18),rgba(96,165,250,.04) 70%,transparent 72%); }
.salesai-hero h1 { font-size: clamp(25px,3vw,34px); font-weight: 800; color: #14243b; letter-spacing: -.035em; margin: 0 0 7px; }
.hero-accent { color: #2563eb; }
.hero-subtitle { color: #63758e; margin: 0; font-size: 14px; }
.metric-chip {
  display: inline-flex; align-items: center; background: rgba(255,255,255,.84); border: 1px solid #dce6f2;
  border-radius: 999px; padding: 7px 13px; margin: 4px; color: #425670; font-size: 12px; font-weight: 600;
}
.wf-card {
  background: #fff; border: 1px solid #dce6f2; border-radius: 14px;
  padding: 16px; margin: 8px 0; cursor: pointer; transition: border-color .2s, transform .2s, box-shadow .2s;
}
.wf-card:hover { border-color: #8cb4f2; transform: translateY(-2px); box-shadow: 0 9px 22px rgba(35,75,125,.09); }
.dashboard-visuals { display: grid; gap: 14px; margin: 10px 0 18px; }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(145px,1fr)); gap: 12px; }
.metric-card, .distribution-card { background: #fff; border: 1px solid #dce6f2; border-radius: 16px; box-shadow: 0 5px 16px rgba(31,67,115,.05); }
.metric-card { min-height: 115px; padding: 15px 17px; position: relative; overflow: hidden; }
.metric-card:after { content: ""; position: absolute; width: 70px; height: 70px; right: -24px; top: -25px; border-radius: 50%; opacity: .55; }
.metric-card.blue:after { background: #dbeafe; } .metric-card.coral:after { background: #ffe4df; }
.metric-card.amber:after { background: #fef3c7; } .metric-card.teal:after { background: #ccfbf1; }
.metric-card.violet:after { background: #ede9fe; }
.metric-card-icon { font-size: 19px; margin-bottom: 9px; }
.metric-card-label { color: #6b7c93; font-size: 12px; font-weight: 650; }
.metric-card-value { color: #172b4d; font-size: 23px; font-weight: 800; letter-spacing: -.03em; margin-top: 3px; }
.distribution-card { padding: 18px 20px; }
.process-visual, .problem-visual { margin: 12px 0 22px; padding: 16px; background: #fff; border: 1px solid #dce6f2; border-radius: 18px; box-shadow: 0 6px 18px rgba(31,67,115,.055); }
.process-visual figcaption, .problem-visual figcaption { display: flex; flex-direction: column; gap: 4px; margin: 0 0 12px; color: #172b4d; }
.process-visual figcaption strong, .problem-visual figcaption strong { font-size: 16px; }
.process-visual figcaption span, .problem-visual figcaption span { color: #63758e; font-size: 13px; }
.process-visual-scroll, .problem-visual-scroll { overflow-x: auto; }
.process-visual svg, .problem-visual svg { display: block; width: 100%; height: auto; min-width: 760px; }
.gradio-container [data-testid="chatbot"], .gradio-container .chatbot { background: #f4f8fd !important; color: #172b4d !important; border: 1px solid #dce6f2 !important; }
.gradio-container [data-testid="chatbot"] *, .gradio-container .chatbot * { color: #172b4d; }
.gradio-container [data-testid="chatbot"] .message.user, .gradio-container .chatbot .message.user { background: #e8f1ff !important; }
.gradio-container [data-testid="chatbot"] .message.bot, .gradio-container .chatbot .message.bot { background: #ffffff !important; }
.gradio-container [data-testid="chatbot"] p, .gradio-container .chatbot p { color: #172b4d !important; }
#objection-chatbot { --background-fill-primary: #f4f8fd !important; --background-fill-secondary: #e5f8f4 !important; --block-background-fill: #ffffff !important; --color-accent-soft: #dbeafe !important; --body-text-color: #172b4d !important; --body-text-color-subdued: #52647d !important; --border-color-primary: #cbd9e9 !important; --border-color-accent-subdued: #91b4e8 !important; --shadow-drop: 0 5px 14px rgba(31,67,115,.12) !important; background: #f4f8fd !important; color: #172b4d !important; border: 1px solid #cbd9e9 !important; }
#objection-chatbot .user { background: #dbeafe !important; color: #163d73 !important; border-color: #91b4e8 !important; }
#objection-chatbot .bot { background: #e5f8f4 !important; color: #145b53 !important; border-color: #81cfc2 !important; }
#objection-chatbot .message, #objection-chatbot .message .prose, #objection-chatbot .message .prose * { color: #172b4d !important; }
.distribution-heading { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.distribution-heading h3 { margin: 3px 0 0; color: #172b4d; font-size: 16px; }
.eyebrow { color: #8292a8; font-size: 10px; font-weight: 800; letter-spacing: .12em; }
.distribution-total { color: #6b7c93; font-size: 12px; }
.stacked-bar { display: flex; height: 12px; overflow: hidden; border-radius: 999px; background: #edf2f8; margin: 16px 0 12px; gap: 2px; }
.stacked-bar span { min-width: 0; border-radius: 999px; transition: width .4s ease; }
.bar-hot { background: #f07865; } .bar-warm { background: #e8ae43; } .bar-cold { background: #6da8e8; }
.distribution-legend { display: flex; flex-wrap: wrap; gap: 18px; color: #52647d; font-size: 12px; }
.distribution-legend span { display: inline-flex; align-items: center; gap: 6px; }
.distribution-legend b { color: #172b4d; margin-left: 2px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot.hot { background: #f07865; } .dot.warm { background: #e8ae43; } .dot.cold { background: #6da8e8; }
.workflow-map-card { background:#fff; border:1px solid #dce6f2; border-radius:16px; padding:18px; box-shadow:0 5px 16px rgba(31,67,115,.05); margin:8px 0 16px; }
.workflow-map-heading { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.workflow-map-heading h3 { color:#172b4d; font-size:16px; margin:3px 0 0; }
.workflow-node-count { color:#315b90; background:#edf4ff; border:1px solid #d9e8fb; border-radius:999px; padding:6px 10px; font-size:11px; font-weight:700; white-space:nowrap; }
.workflow-map-note { color:#6b7c93; font-size:12px; margin:8px 0 12px; }
.workflow-map-scroll { overflow-x:auto; overflow-y:hidden; border:1px solid #e4ebf3; border-radius:12px; background:linear-gradient(180deg,#fbfdff,#f6f9fd); padding:8px; }
.workflow-map-scroll svg { display:block; max-width:none; }
.workflow-map-empty { background:#fff8e8; color:#795d25; border:1px solid #f2dfb1; border-radius:12px; padding:14px; }
@media (max-width: 640px) { .salesai-hero { padding: 21px 18px; } .distribution-card { padding: 15px; } .distribution-legend { gap: 11px; } }
"""


# ══════════════════════════════════════════════════════════════
# GRADIO UI BUILDER
# ══════════════════════════════════════════════════════════════

def build_gradio_app():
    with gr.Blocks(
        title="🚀 SalesAI SDR — IIT Capstone Dashboard"
    ) as demo:

        # ── Global Header ──────────────────────────────────────
        gr.HTML(f"""
        <div class="salesai-hero">
          <h1>🚀 SalesAI SDR <span class="hero-accent">Multi-Agent Dashboard</span></h1>
          <p class="hero-subtitle">
            IIT Jammu Summer School 2026 | Vinay Bhardwaj |
            Tab 1: N8N Workflows &nbsp;•&nbsp; Tab 2: AI Agents
          </p>
          <div style="margin-top:14px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
            <span class="metric-chip">🔧 6 N8N Workflows</span>
            <span class="metric-chip">🤖 6 OpenAI Agents SDK Agents</span>
            <span class="metric-chip">💾 SQLite CRM</span>
            <span class="metric-chip">🌐 Real Web Research</span>
            <span class="metric-chip">📧 SMTP Email</span>
          </div>
        </div>
        """)

        with gr.Tabs():

            # ════════════════════════════════════════════════════
            # ██████  TAB GROUP 1: SALESFLOW N8N  ██████████████
            # ════════════════════════════════════════════════════

            with gr.TabItem("🔧 Tab 1: N8N Workflows"):
                with gr.Tabs():

                    # Put the visual workflow gallery first so visitors immediately see
                    # the actual node maps instead of an overview wall of text.
                    with gr.TabItem("🧭 Workflow Gallery"):
                        gr.Markdown("### Explore the SalesFlow automations")
                        gr.Markdown("Choose a workflow to see its connected nodes. The diagram is generated from the included n8n export.")

                        wf_choice = gr.Radio(
                            choices=[f"{w['icon']} {w['id']}: {w['name']}" for w in N8N_WORKFLOWS],
                            label="Select Workflow",
                            value=f"{N8N_WORKFLOWS[0]['icon']} {N8N_WORKFLOWS[0]['id']}: {N8N_WORKFLOWS[0]['name']}"
                        )

                        wf_graph_html = gr.HTML()
                        with gr.Accordion("📖 Workflow steps and raw JSON", open=False):
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

                        # Load first workflow on startup
                        demo.load(
                            lambda: get_workflow_detail("WF-01"),
                            outputs=[wf_detail_md, wf_graph_html, wf_json_md]
                        )

                    # ── Project overview and importable workflow files ──
                    with gr.TabItem("📐 Project Overview"):
                        gr.Markdown("""
### 🔧 SalesFlow AI — N8N Automation Platform
**Six connected workflows** cover lead capture, qualification, assignment, follow-up, proposal approval, and reporting.
""")
                        gr.HTML(render_architecture_visual())
                        gr.HTML(render_lead_lifecycle_visual())
                        overview_md = gr.Markdown(get_workflow_overview())

                        gr.Markdown("""
---
### 📁 Importable N8N workflow files

| Workflow | File | Nodes |
|----------|------|-------|
| 🎯 Lead Capture & Registration | `01_lead_capture_registration.json` | 10 |
| 📊 AI Lead Scoring & BANT | `02_ai_lead_scoring_qualification.json` | 9 |
| 👤 Sales Rep Assignment & CRM | `03_sales_rep_assignment_crm.json` | 9 |
| 📅 Follow-ups & Meeting Scheduler | `04_automated_followup_meeting_scheduler.json` | 9 |
| 📄 Proposal Generation & HITL | `05_proposal_generation_human_approval.json` | 11 |
| 📈 Sales Dashboard & Analytics | `06_sales_dashboard_analytics_report.json` | 8 |

**56 nodes across 6 workflow exports, including retry and error-stop handling.**
""")

                    # ── Sub-Tab 1.3: Live Workflow Runner ─────
                    with gr.TabItem("⚡ Live Workflow Runner"):
                        gr.Markdown("### Safe Local Simulation and Optional Live Sandbox Run")
                        gr.Markdown("The local simulation reads the exported workflow JSON and makes no webhook, API, database, email, calendar, Drive, or Sheets calls. The separate live button requires explicit opt-in and a synthetic `@example.com` recipient; use only with a sandbox n8n instance. WF-01 is blocked until its duplicate active webhook path is resolved.")
                        with gr.Row():
                            sim_wf_choice = gr.Dropdown(
                                choices=[
                                    ("WF-01 · Lead Capture", "WF-01"),
                                    ("WF-02 · BANT Qualification", "WF-02"),
                                    ("WF-03 · Rep Assignment", "WF-03"),
                                    ("WF-04 · Scheduled Follow-ups (run in n8n)", "WF-04"),
                                    ("WF-05 · Proposal Generation", "WF-05"),
                                    ("WF-06 · Scheduled Analytics (run in n8n)", "WF-06"),
                                ],
                                label="Select workflow",
                                value="WF-01",
                            )
                        with gr.Row():
                            sim_preset = gr.Dropdown(LEAD_LABELS, label="Use saved CRM lead (optional)", value="— Enter manually —")
                        with gr.Row():
                            sim_name     = gr.Textbox(label="Contact Name", placeholder="Priya Sharma")
                            sim_company  = gr.Textbox(label="Company Name", placeholder="TechVision Solutions")
                            sim_role     = gr.Textbox(label="Role", placeholder="VP of Sales")
                        with gr.Row():
                            sim_email    = gr.Textbox(label="Email Address", placeholder="priya.sharma@techvision.io")
                            sim_industry = gr.Textbox(label="Industry", placeholder="B2B SaaS")
                            sim_budget   = gr.Textbox(label="Budget", placeholder="$2,000-5,000/month")
                        sim_notes = gr.Textbox(label="Lead Notes / Context", placeholder="Series A $8M. 25 sales reps. Manual lead tracking.", lines=2)
                        
                        with gr.Row():
                            sim_btn = gr.Button("🧪 Run Local JSON Simulation", variant="primary", size="lg")
                            live_btn = gr.Button("🌐 Send to Active n8n Sandbox (Opt-in)", variant="secondary", size="lg")
                        
                        with gr.Row():
                            sim_log     = gr.Markdown(label="Workflow trace")
                            sim_summary = gr.Markdown(label="Run mode and status")
                        
                        with gr.Accordion("📄 Request and response JSON", open=False):
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

                    # ── Sub-Tab 1.4: Problem Analysis ──────────
                    with gr.TabItem("🔍 Problem & Solution"):
                        gr.HTML(render_problem_solution_visual())
                        gr.Markdown("""
## 🎯 Problem Analysis — Why SalesFlow AI?

### 5 Core Problems in B2B Sales

| # | Problem | Impact |
|---|---------|--------|
| 1 | **Slow Lead Response** — avg 4-8 hours | Leads 100x less likely to convert vs 5-min response |
| 2 | **Manual Lead Qualification** | Sales reps spend 60% on admin, 40% selling |
| 3 | **Inconsistent Follow-ups** | Avg 8 touchpoints needed, reps give up after 2-3 |
| 4 | **No Pipeline Visibility** | Managers can't intervene before deals stall |
| 5 | **Proposal Bottlenecks** | 2-6h manual creation + days waiting for approval |

### 💡 Solution Architecture (N8N + GPT-4o)

| Problem | Workflow | How Solved |
|---------|----------|-----------|
| Slow Response | WF-01 | Webhook → GPT-4o score → instant email in <5 seconds |
| Manual Qual | WF-02 | BANT matrix auto-scored by GPT-4o, no human needed |
| Follow-up Gaps | WF-04 | 5-touch cadence runs every 8h automatically, 24/7 |
| No Visibility | WF-06 | Weekly AI-generated KPI report to leadership |
| Proposal Delay | WF-05 | GPT-4o renders full HTML proposal + manager HITL |

### 📊 Market Context

| Metric | Value |
|--------|-------|
| Global CRM market (2026) | **$89.5 billion** |
| Companies using spreadsheets for CRM | **43%** |
| Revenue lost to poor follow-up | **$1.4 trillion/year** |
| Avg ROI from CRM automation | **245%** |

---

### 🏗️ Technical Stack
The application dashboard runs six agents through the OpenAI Agents SDK and stores CRM records in SQLite. The separate n8n JSON exports describe OpenAI, PostgreSQL, Google, and Slack integrations; those services need credentials in an n8n instance before they can run live.
""")
                        gr.HTML(render_tech_stack_visual())

            # ════════════════════════════════════════════════════
            # ██████  TAB GROUP 2: SALESAI AGENTS  ██████████████
            # ════════════════════════════════════════════════════

            with gr.TabItem("🤖 Tab 2: AI Agents"):
                with gr.Tabs():

                    # ── Sub-Tab 2.1: Dashboard ─────────────────
                    with gr.TabItem("📊 Dashboard"):
                        with gr.Row():
                            refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary", scale=1)
                        dash_visuals = gr.HTML()
                        dash_md = gr.Markdown("*Click Refresh to load live dashboard*")
                        dash_table = gr.Dataframe(
                            headers=["Name", "Company", "Stage", "Temperature", "Score", "Added"],
                            label="📋 Recent Leads (Top 10)",
                            interactive=False
                        )
                        refresh_btn.click(get_dashboard_data, outputs=[dash_visuals, dash_md, dash_table])
                        demo.load(get_dashboard_data, outputs=[dash_visuals, dash_md, dash_table])

                    # ── Sub-Tab 2.2: Research ──────────────────
                    with gr.TabItem("🔍 Research Agent"):
                        gr.Markdown("### 🔍 Agent 1: Prospect Research — Real Web Data + AI Intelligence")
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

                    # ── Sub-Tab 2.3: Qualification ─────────────
                    with gr.TabItem("🎯 Qualification Agent"):
                        gr.Markdown("### 🎯 Agent 2: Lead Qualification — BANT Scoring + ICP Matching")
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

                    # ── Sub-Tab 2.4: Email Writer ──────────────
                    with gr.TabItem("✉️ Email Writer"):
                        gr.Markdown("### ✉️ Agent 3: AI Email Writer — Hyper-Personalized 5-Touch Cadence")
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

                    # ── Sub-Tab 2.5: Meetings ──────────────────
                    with gr.TabItem("📅 Meeting Coordinator"):
                        gr.Markdown("### 📅 Agent 6: Meeting Coordinator — Schedule + Agenda + Links")
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

                    # ── Sub-Tab 2.6: Objection Chat ────────────
                    with gr.TabItem("💬 Objection Handler"):
                        gr.Markdown("### 💬 Agent 4 & 5: AI Sales Coach — Handle Objections + Roleplay Mode")
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
                        gr.Markdown("**Start here:** type a prospect objection below, choose a mode, and press **Send**. Your conversation appears in the panel.")
                        oc_chatbot = gr.Chatbot(
                            label="💬 SalesAI Coach",
                            value=OBJECTION_CHAT_WELCOME,
                            height=420,
                            elem_id="objection-chatbot",
                        )
                        with gr.Row():
                            oc_input = gr.Textbox(
                                label="Your message",
                                placeholder="Type an objection or question...",
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

                    # ── Sub-Tab 2.7: Full Pipeline ─────────────
                    with gr.TabItem("🚀 Full Pipeline"):
                        gr.Markdown("### 🚀 Run Complete 5-Step SDR Pipeline (All 6 Agents)")
                        gr.HTML(render_visual_flow(
                            "Full SDR pipeline",
                            "Choose a saved CRM record or enter a new contact, then run the agents in sequence.",
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
                            info="Saved records may include sample data; verify contact details and source before outreach.",
                        )
                        with gr.Row():
                            fp_name = gr.Textbox(label="Contact name", placeholder="Enter a real contact")
                            fp_company = gr.Textbox(label="Company", placeholder="Company name")
                            fp_email = gr.Textbox(label="Email", placeholder="name@company.com")
                        with gr.Row():
                            fp_role = gr.Textbox(label="Role", placeholder="Sales Director")
                            fp_industry = gr.Textbox(label="Industry", placeholder="B2B SaaS")
                            fp_website = gr.Textbox(label="Website", placeholder="company.com")
                        fp_notes = gr.Textbox(label="Context / lead notes", placeholder="Add only verified context for personalization", lines=2)
                        fp_btn = gr.Button(
                            "🚀 Run SDR Pipeline (Research → Qualify → Email → Meeting → CRM)",
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

                    # ── Sub-Tab 2.8: CRM Pipeline ──────────────
                    with gr.TabItem("📋 CRM Pipeline"):
                        with gr.Row():
                            crm_refresh  = gr.Button("🔄 Refresh Pipeline", variant="primary")
                            forecast_btn = gr.Button("📈 Generate Forecast", variant="secondary")
                        crm_md = gr.Markdown()
                        crm_table = gr.Dataframe(
                            headers=["Name", "Company", "Role", "Stage", "Temperature", "Score", "Deal Size", "Added"],
                            label="🏆 Top Leads by Score",
                            interactive=False
                        )
                        forecast_md = gr.Markdown()
                        crm_refresh.click(get_crm_pipeline, outputs=[crm_md, crm_table])
                        forecast_btn.click(get_forecast, outputs=[forecast_md])

                    # ── Sub-Tab 2.9: Add Lead ──────────────────
                    with gr.TabItem("➕ Add Lead"):
                        gr.Markdown("### ➕ Add New Lead to CRM Database")
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

                    # ── Sub-Tab 2.10: Settings ─────────────────
                    with gr.TabItem("⚙️ Settings"):
                        smtp = get_smtp_status()
                        gr.Markdown(f"""### ⚙️ System Configuration

#### 🤖 AI Provider
| Field | Value |
|-------|-------|
| Agent Runtime | **OpenAI Agents SDK** |
| Agent Model | **{os.getenv('OPENAI_AGENT_MODEL', 'gpt-4.1-mini')}** |
| OpenAI Key | {'✅ Set' if OPENAI_API_KEY else '❌ Not set'} |

#### 📧 Email (SMTP)
| Field | Value |
|-------|-------|
| Status | {smtp.get('status')} |
| Host | {smtp.get('host')} |
| Port | {smtp.get('port')} |
| User | {smtp.get('user')} |

#### 💾 Database
| Field | Value |
|-------|-------|
| DB Path | `salesai.db` |
| Type | SQLite |

#### 🔑 How to Configure SMTP
Add to your `.env` file:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Your Name
```
> For Gmail: Use an **App Password** (not your main password).
> Go to: Google Account → Security → 2-Step Verification → App Passwords.
""")

    return demo


# ══════════════════════════════════════════════════════════════
# LAUNCH
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀 Starting SalesAI SDR Gradio Dashboard...")
    print(f"   Agent Runtime: OpenAI Agents SDK ({os.getenv('OPENAI_AGENT_MODEL', 'gpt-4.1-mini')})")
    print(f"   OpenAI Key   : {'SET' if OPENAI_API_KEY else 'MISSING'}")
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
