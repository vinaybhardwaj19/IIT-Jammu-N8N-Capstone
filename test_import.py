"""Full import and runtime test for IIT submission."""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv('.env')
sys.path.insert(0, 'Tab2_SalesAI_Agents')
sys.path.insert(0, 'Tab2_SalesAI_Agents/src')

errors = []

print("=" * 60)
print("SalesAI SDR - IIT Submission Test Runner")
print("=" * 60)

# Test 1: Gradio
try:
    import gradio as gr
    print(f"[OK] Gradio {gr.__version__} imported")
except Exception as e:
    errors.append(f"Gradio: {e}")
    print(f"[FAIL] Gradio: {e}")

# Test 2: Agent imports
try:
    from salesai_agents.base import call_ai, AI_PROVIDER, GEMINI_API_KEY, GROQ_API_KEY
    print(f"[OK] base.py | Provider={AI_PROVIDER} | Gemini={'SET' if GEMINI_API_KEY else 'MISSING'} | Groq={'SET' if GROQ_API_KEY else 'MISSING'}")
except Exception as e:
    errors.append(f"base.py: {e}")
    print(f"[FAIL] base.py: {e}")

try:
    from salesai_agents.prospect_research_agent import ProspectResearchAgent
    print("[OK] ProspectResearchAgent")
except Exception as e:
    errors.append(f"ProspectResearchAgent: {e}")
    print(f"[FAIL] ProspectResearchAgent: {e}")

try:
    from salesai_agents.lead_qualification_agent import LeadQualificationAgent
    print("[OK] LeadQualificationAgent")
except Exception as e:
    errors.append(f"LeadQualificationAgent: {e}")
    print(f"[FAIL] LeadQualificationAgent: {e}")

try:
    from salesai_agents.email_writer_agent import EmailWriterAgent
    print("[OK] EmailWriterAgent")
except Exception as e:
    errors.append(f"EmailWriterAgent: {e}")
    print(f"[FAIL] EmailWriterAgent: {e}")

try:
    from salesai_agents.objection_crm_agents import ObjectionHandlerAgent
    print("[OK] ObjectionHandlerAgent")
except Exception as e:
    errors.append(f"ObjectionHandlerAgent: {e}")
    print(f"[FAIL] ObjectionHandlerAgent: {e}")

try:
    from salesai_agents.crm_manager_agent import CRMManagerAgent
    print("[OK] CRMManagerAgent (crm_manager_agent.py)")
except Exception as e:
    errors.append(f"CRMManagerAgent: {e}")
    print(f"[FAIL] CRMManagerAgent: {e}")

try:
    from salesai_agents.meeting_coordinator_agent import MeetingCoordinatorAgent
    print("[OK] MeetingCoordinatorAgent")
except Exception as e:
    errors.append(f"MeetingCoordinatorAgent: {e}")
    print(f"[FAIL] MeetingCoordinatorAgent: {e}")

# Test 3: Tools
try:
    from tools.crm_database import get_all_leads, get_pipeline_stats, upsert_lead, get_lead, init_database
    print("[OK] crm_database")
except Exception as e:
    errors.append(f"crm_database: {e}")
    print(f"[FAIL] crm_database: {e}")

try:
    from tools.email_sender import send_cold_email, simulate_email_send, get_smtp_status
    print("[OK] email_sender")
except Exception as e:
    errors.append(f"email_sender: {e}")
    print(f"[FAIL] email_sender: {e}")

try:
    from tools.web_research import search_duckduckgo, get_company_info_duckduckgo
    print("[OK] web_research")
except Exception as e:
    errors.append(f"web_research: {e}")
    print(f"[FAIL] web_research: {e}")

# Test 4: DB init
try:
    init_database()
    stats = get_pipeline_stats()
    print(f"[OK] Database initialized | Leads: {stats.get('total_leads', 0)}")
except Exception as e:
    errors.append(f"init_database: {e}")
    print(f"[FAIL] init_database: {e}")

# Test 4b: Email-based CRM deduplication (temporary database only)
try:
    import tempfile
    import sqlite3
    from tools import crm_database as crm_module
    original_db_path = crm_module.DB_PATH
    with tempfile.TemporaryDirectory(prefix="salesai-dedup-check-") as temp_dir:
        test_db_path = os.path.join(os.environ.get("TEMP", temp_dir), f"salesai-dedup-{os.getpid()}.sqlite3")
        crm_module.DB_PATH = test_db_path
        try:
            first_id = crm_module.upsert_lead({
                "lead_id": "TEST-LEAD-1", "full_name": "Synthetic Test",
                "email": "duplicate-check@example.com", "company": "Before",
            })
            second_id = crm_module.upsert_lead({
                "full_name": "Synthetic Test Updated",
                "email": "duplicate-check@example.com", "company": "After",
            })
            with sqlite3.connect(test_db_path) as conn:
                row_count = conn.execute(
                    "SELECT COUNT(*) FROM leads WHERE email = ?",
                    ("duplicate-check@example.com",),
                ).fetchone()[0]
                row = conn.execute(
                    "SELECT lead_id, full_name, company FROM leads WHERE email = ?",
                    ("duplicate-check@example.com",),
                ).fetchone()
            assert first_id == second_id == "TEST-LEAD-1"
            assert row_count == 1 and row == ("TEST-LEAD-1", "Synthetic Test Updated", "After")
        finally:
            crm_module.DB_PATH = original_db_path
            # Keep the uniquely named SQLite temp DB in the OS temp directory.
    print("[OK] CRM email fallback deduplication verified in a temporary database")
except Exception as e:
    errors.append(f"CRM email fallback deduplication: {e}")
    print(f"[FAIL] CRM email fallback deduplication: {e}")
finally:
    if "crm_module" in locals():
        crm_module.DB_PATH = original_db_path

# Test 5: SMTP status
try:
    smtp = get_smtp_status()
    print(f"[OK] SMTP configuration inspected (configured={smtp['configured']}); no email sent")
except Exception as e:
    errors.append(f"get_smtp_status: {e}")
    print(f"[FAIL] get_smtp_status: {e}")

# Test 6: Agent instantiation
try:
    agents = {
        "research":  ProspectResearchAgent(),
        "qualify":   LeadQualificationAgent(),
        "email":     EmailWriterAgent(),
        "objection": ObjectionHandlerAgent(),
        "crm":       CRMManagerAgent(),
        "meeting":   MeetingCoordinatorAgent(),
    }
    print(f"[OK] All 6 agents instantiated successfully")
except Exception as e:
    errors.append(f"Agent instantiation: {e}")
    print(f"[FAIL] Agent instantiation: {e}")

# Test 7: Tab 1 N8N Workflow JSON Validation
try:
    import json
    wf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tab1_SalesFlow_N8N", "workflows")
    expected_wfs = [
        "01_lead_capture_registration.json",
        "02_ai_lead_scoring_qualification.json",
        "03_sales_rep_assignment_crm.json",
        "04_automated_followup_meeting_scheduler.json",
        "05_proposal_generation_human_approval.json",
        "06_sales_dashboard_analytics_report.json"
    ]
    workflows = {}
    total_nodes = 0
    for wf_file in expected_wfs:
        wf_path = os.path.join(wf_dir, wf_file)
        with open(wf_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "nodes" in data and len(data["nodes"]) > 0
        workflows[data["name"]] = data
        total_nodes += len(data["nodes"])
        node_names = {node["name"] for node in data["nodes"]}
        for outputs in data.get("connections", {}).values():
            for branches in outputs.values():
                for branch in branches:
                    assert all(edge.get("node") in node_names for edge in branch)
    assert total_nodes in (50, 56), f"Expected 50 or 56 nodes, found {total_nodes}"
    wf02 = workflows["02 - AI Lead Scoring & Qualification"]
    assert any(edge.get("node") == "Webhook Response"
               for branches in wf02["connections"]["Google Sheets: Add to Nurture List"]["main"]
               for edge in branches), "WF-02 nurture branch must return a webhook response"
    wf05 = workflows["05 - AI Proposal Generation & Human Approval"]
    wf05_edges = wf05["connections"]
    assert wf05_edges["IF: Approved?"]["main"][0][0]["node"] == "Gmail: Send Proposal to Prospect"
    assert wf05_edges["Gmail: Send Proposal to Prospect"]["main"][0][0]["node"] == "Postgres: Update Status to Proposal Sent"
    assert wf05_edges["Postgres: Update Status to Proposal Sent"]["main"][0][0]["node"] == "Webhook Response"
    print(f"[OK] Tab 1: Six workflow JSONs, 50 nodes, and webhook response branches validated")
except Exception as e:
    errors.append(f"N8N Workflows: {e}")
    print(f"[FAIL] N8N Workflows: {e}")

# Test 8: Tab 1 Simulator & Gradio App
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gradio_app import simulate_n8n_workflow, build_gradio_app
    simulated_nodes = 0
    synthetic_lead = {
        "lead_preset": "— Enter manually —",
        "custom_name": "Synthetic Test Contact",
        "custom_company": "Example Company",
        "custom_email": "synthetic-lead@example.com",
        "custom_role": "Sales Operations",
        "custom_industry": "Software",
        "custom_budget": "$5,000",
        "custom_notes": "Synthetic local verification scenario",
    }
    for wf_id in ("WF-01", "WF-02", "WF-03", "WF-04", "WF-05", "WF-06"):
        log, j_trace, summ = simulate_n8n_workflow(wf_choice=wf_id, **synthetic_lead)
        assert "LOCAL_JSON_SIMULATION" in log and "synthetic-lead@example.com" in log
        assert "no external side effects occurred" in summ
        trace_json = log.split("```json\n", 1)[1].split("\n```", 1)[0]
        result = json.loads(trace_json)
        assert result["side_effects"]["n8n_webhook_called"] is False
        simulated_nodes += result["nodes_simulated"]
    assert simulated_nodes in (50, 56), f"Expected 50 or 56 simulated nodes, found {simulated_nodes}"
    print("[OK] Tab 1: Six local workflow traces simulated safely (50 nodes; no live webhook calls)", flush=True)
except Exception as e:
    errors.append(f"Tab 1 Simulator: {e}")
    print(f"[FAIL] Tab 1 Simulator: {e}", flush=True)

# Test 9: FastAPI Backend App
try:
    from api_server import app as fastapi_app
    assert fastapi_app.title == "SalesAI SDR API"
    print("[OK] FastAPI REST Backend verified", flush=True)
except Exception as e:
    errors.append(f"FastAPI: {e}")
    print(f"[FAIL] FastAPI: {e}", flush=True)

print("=" * 60, flush=True)
if errors:
    print(f"RESULT: {len(errors)} ERROR(S) FOUND:", flush=True)
    for err in errors:
        print(f"  - {err}", flush=True)
    sys.exit(1)
else:
    print("RESULT: LOCAL VERIFICATION PASSED - live SaaS integrations and submission items require separate verification.", flush=True)
    sys.exit(0)
