"""
Platform Test Suite for SalesAI SDR & SalesFlow N8N Platform.
Run with: pytest tests/ -v
"""

import os
import sys
import json
import sqlite3
import tempfile
import pytest

# Ensure project directories are in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

TAB2_PATH = os.path.join(PROJECT_ROOT, "Tab2_SalesAI_Agents")
TAB2_SRC = os.path.join(TAB2_PATH, "src")
if TAB2_PATH not in sys.path:
    sys.path.insert(0, TAB2_PATH)
if TAB2_SRC not in sys.path:
    sys.path.insert(0, TAB2_SRC)


def test_framework_and_library_imports():
    """Verify that core full-stack libraries are correctly importable."""
    import gradio as gr
    import fastapi
    import pydantic
    assert gr.__version__ is not None
    assert fastapi.__version__ is not None
    assert pydantic.__version__ is not None


def test_base_provider_and_environment():
    """Verify provider helper and API keys presence."""
    from salesai_agents.base import AI_PROVIDER, GEMINI_API_KEY, GROQ_API_KEY
    assert AI_PROVIDER in ("gemini", "groq", "openai")
    # Check that client factory function is callable
    from salesai_agents.base import get_ai_client
    assert callable(get_ai_client)


def test_all_six_agents_instantiation():
    """Verify that all six autonomous agents instantiate cleanly."""
    from salesai_agents.prospect_research_agent import ProspectResearchAgent
    from salesai_agents.lead_qualification_agent import LeadQualificationAgent
    from salesai_agents.email_writer_agent import EmailWriterAgent
    from salesai_agents.objection_crm_agents import ObjectionHandlerAgent
    from salesai_agents.crm_manager_agent import CRMManagerAgent
    from salesai_agents.meeting_coordinator_agent import MeetingCoordinatorAgent

    agents = {
        "research": ProspectResearchAgent(),
        "qualify": LeadQualificationAgent(),
        "email": EmailWriterAgent(),
        "objection": ObjectionHandlerAgent(),
        "crm": CRMManagerAgent(),
        "meeting": MeetingCoordinatorAgent(),
    }
    assert len(agents) == 6
    assert agents["research"].name == "ProspectResearchAgent"
    assert agents["qualify"].name == "LeadQualificationAgent"
    assert agents["meeting"].name == "MeetingCoordinatorAgent"


def test_crm_database_initialization_and_deduplication():
    """Verify SQLite CRM initialization and email-based lead deduplication."""
    from tools import crm_database as crm_module

    original_db_path = crm_module.DB_PATH
    test_db_path = os.path.join(tempfile.gettempdir(), f"salesai-test-{os.getpid()}.sqlite3")
    crm_module.DB_PATH = test_db_path

    try:
        crm_module.init_database()
        stats = crm_module.get_pipeline_stats()
        assert isinstance(stats, dict)

        # Insert first lead
        lead_id_1 = crm_module.upsert_lead({
            "lead_id": "TEST-001",
            "full_name": "Alice Tester",
            "email": "alice@example.com",
            "company": "Initial Corp",
        })

        # Update same lead by email
        lead_id_2 = crm_module.upsert_lead({
            "full_name": "Alice Tester Updated",
            "email": "alice@example.com",
            "company": "Updated Corp",
        })

        # Verify deduplication
        assert lead_id_1 == lead_id_2 == "TEST-001"

        with sqlite3.connect(test_db_path) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE email = ?",
                ("alice@example.com",)
            ).fetchone()[0]
            row = conn.execute(
                "SELECT lead_id, full_name, company FROM leads WHERE email = ?",
                ("alice@example.com",)
            ).fetchone()

        assert count == 1
        assert row == ("TEST-001", "Alice Tester Updated", "Updated Corp")
    finally:
        crm_module.DB_PATH = original_db_path
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
        except OSError:
            pass


def test_tab1_n8n_workflow_definitions():
    """Verify that all six N8N workflow JSON files exist, have valid syntax and edges."""
    wf_dir = os.path.join(PROJECT_ROOT, "Tab1_SalesFlow_N8N", "workflows")
    expected_wfs = [
        "01_lead_capture_registration.json",
        "02_ai_lead_scoring_qualification.json",
        "03_sales_rep_assignment_crm.json",
        "04_automated_followup_meeting_scheduler.json",
        "05_proposal_generation_human_approval.json",
        "06_sales_dashboard_analytics_report.json"
    ]
    total_nodes = 0
    workflows = {}

    for wf_file in expected_wfs:
        wf_path = os.path.join(wf_dir, wf_file)
        assert os.path.exists(wf_path), f"Workflow file missing: {wf_file}"
        with open(wf_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "nodes" in data and len(data["nodes"]) > 0
        assert "connections" in data
        workflows[data["name"]] = data
        total_nodes += len(data["nodes"])

        node_names = {node["name"] for node in data["nodes"]}
        for outputs in data.get("connections", {}).values():
            for branches in outputs.values():
                for branch in branches:
                    assert all(edge.get("node") in node_names for edge in branch)

    assert total_nodes in (50, 56)


def test_tab1_local_json_simulation():
    """Verify deterministic, zero-network local simulation of all 6 workflows."""
    from gradio_app import simulate_n8n_workflow

    synthetic_lead = {
        "lead_preset": "— Enter manually —",
        "custom_name": "Evaluator Test",
        "custom_company": "Acme Global",
        "custom_email": "eval@example.com",
        "custom_role": "VP Engineering",
        "custom_industry": "Software",
        "custom_budget": "$25,000",
        "custom_notes": "Evaluating workflow deterministic execution",
    }

    simulated_nodes = 0
    for wf_id in ("WF-01", "WF-02", "WF-03", "WF-04", "WF-05", "WF-06"):
        log, j_trace, summary = simulate_n8n_workflow(wf_choice=wf_id, **synthetic_lead)
        assert "LOCAL_JSON_SIMULATION" in log
        assert "eval@example.com" in log
        assert "no external side effects occurred" in summary

        trace_json = log.split("```json\n", 1)[1].split("\n```", 1)[0]
        result = json.loads(trace_json)
        assert result["side_effects"]["n8n_webhook_called"] is False
        simulated_nodes += result["nodes_simulated"]

    assert simulated_nodes in (50, 56)


def test_meeting_coordinator_calendar_invites():
    """Verify 1-click Google Calendar & Outlook invite URLs generated by meeting tooling."""
    from salesai_agents.sdk_runtime import prepare_meeting

    sample_lead = json.dumps({
        "full_name": "Samantha Reed",
        "company": "CloudMatrix Inc",
        "email": "samantha@cloudmatrix.com"
    })
    res_str = prepare_meeting(sample_lead, "discovery")
    res = json.loads(res_str)

    assert res["status"] == "ready"
    assert "calendar.google.com" in res["google_calendar_invite"]
    assert "outlook.live.com" in res["outlook_calendar_invite"]
    assert "CloudMatrix" in res["google_calendar_invite"] or "CloudMatrix" in res["company"]


def test_fastapi_rest_backend():
    """Verify FastAPI backend metadata and routes."""
    from api_server import app
    assert app.title == "SalesAI SDR API"
    routes = [route.path for route in app.routes]
    assert "/health" in routes
    assert "/webhook/n8n" in routes
