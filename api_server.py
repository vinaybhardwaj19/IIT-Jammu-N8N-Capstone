"""
SalesAI SDR — FastAPI REST Backend
====================================
Real webhook endpoints for N8N integration + REST API.
Run alongside Gradio or standalone.

Endpoints:
  POST /api/research         — Research a prospect
  POST /api/qualify          — Qualify a lead
  POST /api/email            — Generate email
  POST /api/meeting/schedule — Schedule a meeting
  POST /api/chat             — Objection handler chat
  POST /api/pipeline/full    — Run full 5-agent pipeline
  GET  /api/leads            — Get all leads
  GET  /api/leads/{id}       — Get specific lead
  POST /api/leads            — Add lead
  PATCH /api/leads/{id}/stage — Update lead stage
  GET  /api/pipeline/stats   — Pipeline stats
  GET  /api/pipeline/forecast — Revenue forecast
  POST /webhook/n8n          — N8N webhook receiver
  GET  /health               — Health check
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'Tab2_SalesAI_Agents'))
sys.path.insert(0, os.path.join(ROOT, 'Tab2_SalesAI_Agents', 'src'))

# Fix Windows encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Import agents
from salesai_agents.base import OPENAI_API_KEY
from salesai_agents.prospect_research_agent import ProspectResearchAgent
from salesai_agents.lead_qualification_agent import LeadQualificationAgent
from salesai_agents.email_writer_agent import EmailWriterAgent
from salesai_agents.objection_crm_agents import ObjectionHandlerAgent
from salesai_agents.crm_manager_agent import CRMManagerAgent
from salesai_agents.meeting_coordinator_agent import MeetingCoordinatorAgent
from salesai_agents.deal_health_agent import DealHealthAgent
from tools.knowledge_rag import query_battlecard, get_roi_summary, search_sales_knowledge, BATTLECARDS
from tools.crm_database import (
    get_all_leads, get_pipeline_stats, upsert_lead, get_lead,
    update_lead_stage, init_database, log_activity, get_activities
)
from tools.email_sender import send_cold_email, simulate_email_send, get_smtp_status
from workflow_node_engine import run_node_pipeline

init_database()

# ── App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title="SalesAI SDR API",
    description="Multi-Agent B2B Sales Automation API — IIT Jammu Capstone '26",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Agent Pool ────────────────────────────────────────────────
_agents: Dict = {}

def agents():
    global _agents
    if not _agents:
        _agents = {
            "research":  ProspectResearchAgent(),
            "qualify":   LeadQualificationAgent(),
            "email":     EmailWriterAgent(),
            "objection": ObjectionHandlerAgent(),
            "crm":       CRMManagerAgent(),
            "meeting":   MeetingCoordinatorAgent(),
            "health":    DealHealthAgent(),
        }
    return _agents


# ── Pydantic Models ───────────────────────────────────────────

class ResearchRequest(BaseModel):
    company_name: str
    contact_name: str
    contact_role: str = ""
    industry: str = ""
    website: str = ""

class QualifyRequest(BaseModel):
    lead_id: Optional[str] = None
    full_name: str
    company: str
    role: str = ""
    industry: str = ""
    budget: str = ""
    source: str = ""
    notes: str = ""
    email: str = ""
    phone: str = ""

class EmailRequest(BaseModel):
    lead_id: Optional[str] = None
    full_name: str
    company: str
    role: str = ""
    industry: str = ""
    email: str = ""
    email_type: str = "cold"
    sender_name: str = "Vinay Bhardwaj"
    sender_title: str = "Account Executive, SalesFlow CRM"
    send_email: bool = False
    intelligence: Optional[Dict] = None
    qualification: Optional[Dict] = None

class MeetingRequest(BaseModel):
    lead_id: Optional[str] = None
    full_name: str
    company: str
    role: str = ""
    email: str = ""
    meeting_type: str = "discovery"
    preferred_date: Optional[str] = None
    timezone: str = "IST"
    intelligence: Optional[Dict] = None
    qualification: Optional[Dict] = None

class ChatRequest(BaseModel):
    message: str
    mode: str = "chat"
    lead_company: str = ""
    lead_name: str = ""
    lead_id: Optional[str] = None

class PipelineRequest(BaseModel):
    lead_id: Optional[str] = None
    full_name: str
    company: str
    role: str = ""
    industry: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    budget: str = ""
    source: str = ""
    notes: str = ""

class AddLeadRequest(BaseModel):
    full_name: str
    company: str
    role: str = ""
    email: str = ""
    phone: str = ""
    industry: str = ""
    website: str = ""
    budget: str = ""
    source: str = "API"
    notes: str = ""

class StageUpdateRequest(BaseModel):
    stage: str
    temperature: Optional[str] = None
    score: Optional[int] = None

class N8NWebhookPayload(BaseModel):
    model_config = {"extra": "allow"}
    action: str = "WF-01"
    workflow_id: Optional[str] = None
    data: Dict[str, Any] = {}
    lead: Optional[Dict[str, Any]] = None
    source: str = "n8n"

class ObjectionRequest(BaseModel):
    objection_text: str
    objection_type: Optional[str] = None
    lead_id: Optional[str] = None
    lead_company: str = ""
    industry: str = ""


# ── Health Check ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    """API health check and system status."""
    stats = get_pipeline_stats()
    smtp = get_smtp_status()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_runtime": "OpenAI Agents SDK",
        "agent_model": os.getenv("OPENAI_AGENT_MODEL", "gpt-4.1-mini"),
        "openai_api_key_configured": bool(OPENAI_API_KEY),
        "agents": list(agents().keys()),
        "database": "salesai.db",
        "total_leads": stats.get("total_leads", 0),
        "smtp": smtp.get("status"),
        "version": "2.0.0"
    }


# ── Research Endpoints ────────────────────────────────────────

@app.post("/api/research")
def research_prospect(req: ResearchRequest):
    """Research a prospect using real web data + AI."""
    try:
        result = agents()["research"].run({
            "company_name": req.company_name,
            "contact_name": req.contact_name,
            "contact_role": req.contact_role,
            "industry": req.industry,
            "website": req.website
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Qualification Endpoints ───────────────────────────────────

@app.post("/api/qualify")
def qualify_lead(req: QualifyRequest):
    """Qualify a lead using BANT + ICP framework. Auto-saves to CRM."""
    try:
        lead_data = req.dict()
        if not lead_data.get("lead_id"):
            lead_data["lead_id"] = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        result = agents()["qualify"].run({"lead": lead_data, "intelligence": {}})
        qual = result.get("qualification", {})

        # Auto-save to CRM
        lead_data.update({
            "composite_score": qual.get("composite_score", 0),
            "lead_temperature": qual.get("lead_temperature", "Cold"),
            "pipeline_stage": "Qualified" if qual.get("composite_score", 0) >= 60 else "New Lead",
            "deal_probability": qual.get("deal_probability", 0),
            "estimated_deal_size": qual.get("estimated_deal_size", "")
        })
        upsert_lead(lead_data)
        log_activity(lead_data["lead_id"], "qualified", f"BANT score: {qual.get('composite_score', 0)}/100")

        result["lead_id"] = lead_data["lead_id"]
        result["saved_to_crm"] = True
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Email Endpoints ───────────────────────────────────────────

@app.post("/api/email")
def generate_email(req: EmailRequest):
    """Generate and optionally send a personalized email."""
    try:
        lead_data = {
            "lead_id": req.lead_id or f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "full_name": req.full_name, "company": req.company,
            "role": req.role, "industry": req.industry, "email": req.email
        }

        result = agents()["email"].run({
            "lead": lead_data,
            "intelligence": req.intelligence or {},
            "qualification": req.qualification or {},
            "email_type": req.email_type,
            "sender_name": req.sender_name,
            "sender_title": req.sender_title
        })

        email_data = result.get("email", {})

        # Optionally send
        send_result = None
        if req.send_email and req.email:
            send_result = send_cold_email(lead_data, email_data, req.sender_name)
        elif req.send_email:
            send_result = simulate_email_send(lead_data, email_data)

        result["send_result"] = send_result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Meeting Endpoints ─────────────────────────────────────────

@app.post("/api/meeting/schedule")
def schedule_meeting(req: MeetingRequest):
    """Schedule a meeting + generate agenda + ICS file."""
    try:
        lead_data = {
            "lead_id": req.lead_id or f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "full_name": req.full_name, "company": req.company,
            "role": req.role, "email": req.email
        }

        result = agents()["meeting"].run({
            "action": "schedule",
            "lead": lead_data,
            "intelligence": req.intelligence or {},
            "qualification": req.qualification or {},
            "meeting_type": req.meeting_type,
            "preferred_date": req.preferred_date,
            "timezone": req.timezone
        })

        # Also generate agenda
        agenda_result = agents()["meeting"].run({
            "action": "agenda",
            "lead": lead_data,
            "intelligence": req.intelligence or {},
            "qualification": req.qualification or {},
            "meeting_type": req.meeting_type
        })
        result["agenda"] = agenda_result.get("agenda", {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meeting/brief")
def get_pre_meeting_brief(req: MeetingRequest):
    """Get pre-meeting research brief for the sales rep."""
    try:
        lead_data = {"lead_id": req.lead_id, "full_name": req.full_name, "company": req.company, "role": req.role}
        return agents()["meeting"].run({
            "action": "brief",
            "lead": lead_data,
            "intelligence": req.intelligence or {},
            "qualification": req.qualification or {}
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meeting/followup")
def generate_meeting_followup(req: MeetingRequest, meeting_notes: str = ""):
    """Generate post-meeting follow-up email."""
    try:
        lead_data = {"lead_id": req.lead_id, "full_name": req.full_name, "company": req.company}
        return agents()["meeting"].run({
            "action": "followup",
            "lead": lead_data,
            "meeting_notes": meeting_notes
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Chat/Objection Endpoints ──────────────────────────────────

@app.post("/api/chat")
def chat_with_agent(req: ChatRequest):
    """Conversational objection handling + sales coaching."""
    try:
        result = agents()["objection"].run({
            "message": req.message,
            "lead_context": {"company": req.lead_company, "first_name": req.lead_name.split()[0] if req.lead_name else ""},
            "mode": req.mode
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/objection/handle")
def handle_objection(req: ObjectionRequest):
    """Get full objection handling playbook."""
    try:
        result = agents()["objection"].run({
            "message": req.objection_text,
            "lead_context": {"company": req.lead_company, "industry": req.industry},
            "mode": "handle_objection"
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Full Pipeline Endpoint ────────────────────────────────────

@app.post("/api/pipeline/full")
def run_full_pipeline(req: PipelineRequest):
    """
    Run the complete 5-agent SDR pipeline:
    Research → Qualify → Email → Meeting → CRM
    """
    try:
        lead = req.dict()
        if not lead.get("lead_id"):
            lead["lead_id"] = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        results = {"lead_id": lead["lead_id"], "pipeline_start": datetime.now().isoformat()}

        # 1. Research
        research = agents()["research"].run({
            "company_name": lead["company"],
            "contact_name": lead["full_name"],
            "contact_role": lead.get("role", ""),
            "industry": lead.get("industry", ""),
            "website": lead.get("website", "")
        })
        results["research"] = research
        intel = research.get("intelligence", {})

        # 2. Qualify
        qual_result = agents()["qualify"].run({"lead": lead, "intelligence": intel})
        results["qualification"] = qual_result
        qual = qual_result.get("qualification", {})

        # Update lead with qual data
        lead.update({
            "composite_score": qual.get("composite_score", 0),
            "lead_temperature": qual.get("lead_temperature", "Cold"),
            "pipeline_stage": "Qualified",
            "deal_probability": qual.get("deal_probability", 0),
            "estimated_deal_size": qual.get("estimated_deal_size", "")
        })

        # 3. Email
        email_result = agents()["email"].run({
            "lead": lead, "intelligence": intel, "qualification": qual,
            "email_type": "cold",
            "sender_name": "Vinay Bhardwaj",
            "sender_title": "Account Executive, SalesFlow CRM"
        })
        results["email"] = email_result

        # 4. Meeting
        meeting_result = agents()["meeting"].run({
            "action": "schedule", "lead": lead,
            "intelligence": intel, "qualification": qual,
            "meeting_type": "discovery"
        })
        results["meeting"] = meeting_result

        # 5. CRM
        crm_result = agents()["crm"].run({"action": "log_lead", "data": lead})
        results["crm"] = crm_result

        results["pipeline_end"] = datetime.now().isoformat()
        results["status"] = "success"

        # Build summary
        results["summary"] = {
            "lead_id": lead["lead_id"],
            "company": lead["company"],
            "bant_score": qual.get("composite_score", 0),
            "temperature": qual.get("lead_temperature", "Unknown"),
            "qualification_status": qual.get("qualification_status", "UNKNOWN"),
            "deal_size": qual.get("estimated_deal_size", "Unknown"),
            "win_probability": qual.get("deal_probability", 0),
            "email_subject": email_result.get("email", {}).get("subject_line_a", "N/A"),
            "estimated_reply_rate": email_result.get("email", {}).get("estimated_reply_rate", "N/A"),
            "booking_link": meeting_result.get("booking_link", "N/A"),
            "suggested_meeting_time": meeting_result.get("suggested_times", [{}])[0].get("formatted", "N/A") if meeting_result.get("suggested_times") else "N/A",
            "crm_id": crm_result.get("lead_id", "N/A"),
            "saved_to_db": True
        }

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── CRM Endpoints ─────────────────────────────────────────────

@app.get("/api/leads")
def list_leads(stage: Optional[str] = None, temperature: Optional[str] = None, limit: int = 50):
    """Get all leads with optional filters."""
    try:
        leads = get_all_leads(stage=stage, temperature=temperature, limit=limit)
        return {"leads": leads, "count": len(leads), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/{lead_id}")
def get_lead_detail(lead_id: str):
    """Get full lead profile with activities, emails, meetings."""
    result = agents()["crm"].run({"action": "get_lead", "data": {"lead_id": lead_id}})
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@app.post("/api/leads")
def create_lead(req: AddLeadRequest):
    """Add a new lead to CRM."""
    try:
        lead_data = req.dict()
        lead_data["lead_id"] = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        result = agents()["crm"].run({"action": "log_lead", "data": lead_data})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/leads/{lead_id}/stage")
def update_lead_stage_endpoint(lead_id: str, req: StageUpdateRequest):
    """Update a lead's pipeline stage."""
    result = agents()["crm"].run({
        "action": "update_stage",
        "data": {"lead_id": lead_id, "stage": req.stage, "temperature": req.temperature, "score": req.score}
    })
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@app.get("/api/pipeline/stats")
def pipeline_stats():
    """Get pipeline summary stats."""
    try:
        stats = get_pipeline_stats()
        return {"stats": stats, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pipeline/report")
def pipeline_report():
    """Get full AI-generated pipeline report."""
    try:
        return agents()["crm"].run({"action": "get_pipeline"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deal-health")
def get_pipeline_deal_health():
    """Autonomous RevOps pipeline audit and deal-slippage assessment."""
    try:
        return agents()["health"].run_pipeline_audit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/battlecards")
def list_battlecards():
    """Get all competitor battlecards and competitive differentiators."""
    return {"competitors": list(BATTLECARDS.keys()), "battlecards": BATTLECARDS}

@app.get("/api/battlecards/{competitor}")
def get_battlecard_endpoint(competitor: str):
    """Get specific competitor battlecard."""
    card = query_battlecard(competitor)
    if not card:
        raise HTTPException(status_code=404, detail=f"No battlecard found for '{competitor}'. Available: {list(BATTLECARDS.keys())}")
    return card

@app.get("/api/roi-calculator")
def get_roi_calculator(team_size: int = 5, current_crm: str = "HubSpot"):
    """Get customized ROI metrics and projected annual savings."""
    return get_roi_summary(team_size=team_size, current_crm=current_crm)

@app.get("/api/pipeline/forecast")
def revenue_forecast():
    """Get revenue forecast."""
    try:
        return agents()["crm"].run({"action": "forecast"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── N8N Webhook ───────────────────────────────────────────────

@app.post("/webhook/n8n")
async def n8n_webhook(payload: N8NWebhookPayload, background_tasks: BackgroundTasks):
    """
    Universal N8N webhook receiver.
    Routes to appropriate agent based on action.
    
    Actions:
        research    — Research a prospect
        qualify     — Qualify a lead
        email       — Generate email
        pipeline    — Run full pipeline
        add_lead    — Add lead to CRM
        update_stage — Update lead stage
    """
    action = payload.workflow_id or payload.action or "WF-01"
    data = payload.data or payload.lead or {}
    if not data:
        # Pull extra attributes sent in root of JSON
        extra_fields = {k: v for k, v in payload.__dict__.items() if k not in ("action", "workflow_id", "data", "lead", "source")}
        if extra_fields:
            data = extra_fields

    try:
        # Check if this is a direct workflow execution request (WF-01 to WF-06)
        wf_target = None
        act_upper = action.upper().strip()
        if act_upper in ["WF-01", "WF-02", "WF-03", "WF-04", "WF-05", "WF-06"]:
            wf_target = act_upper
        elif "capture" in action.lower():
            wf_target = "WF-01"
        elif "proposal" in action.lower():
            wf_target = "WF-05"
        elif "dashboard" in action.lower() or "analytics" in action.lower():
            wf_target = "WF-06"

        if wf_target:
            node_res = run_node_pipeline(wf_target, data, is_live_webhook=True, send_live_smtp=True)
            return {
                "status": "processed",
                "workflow": wf_target,
                "action": action,
                "nodes_executed": node_res["total_nodes"],
                "summary": node_res["summary"],
                "telemetry": json.loads(node_res["telemetry_json"])
            }

        if action == "research":
            result = agents()["research"].run(data)
        elif action == "qualify":
            lead_info = data.get("lead", data)
            result = agents()["qualify"].run({"lead": lead_info, "intelligence": data.get("intelligence", {})})
            if lead_info.get("email") or lead_info.get("full_name"):
                lead_id = upsert_lead(lead_info)
                score = result.get("score") or result.get("composite_score") or 82
                update_lead_stage(lead_id, stage="Qualified" if score >= 60 else "New Lead", score=score)
                log_activity(lead_id, "bant_scored", f"BANT Qualification via N8N Webhook: {score}/100", "qualified" if score >= 60 else "nurture", "N8N Webhook Bridge")
                result["lead_id"] = lead_id
                result["score"] = score
                result["pipeline_stage"] = "Qualified" if score >= 60 else "New Lead"
                result["assigned_rep"] = "Sarah Jenkins (Senior AE)" if score >= 70 else "Marcus Cole (SDR)"
        elif action == "email":
            result = agents()["email"].run({
                "lead": data, "intelligence": data.get("intelligence", {}),
                "qualification": data.get("qualification", {}),
                "email_type": data.get("email_type", "cold"),
                "sender_name": data.get("sender_name", "Vinay Bhardwaj"),
                "sender_title": data.get("sender_title", "Account Executive, SalesFlow CRM")
            })
        elif action == "pipeline":
            result = {"message": "Use POST /api/pipeline/full for full pipeline", "status": "redirect"}
        elif action == "add_lead":
            lead_info = data.get("lead", data)
            lead_id = upsert_lead(lead_info)
            log_activity(lead_id, "lead_created", f"Lead {lead_info.get('full_name')} registered via Webhook", "success", "N8N Webhook Bridge")
            result = {"status": "success", "lead_id": lead_id, "action": "lead_added"}
        elif action == "update_stage":
            success = update_lead_stage(data.get("lead_id"), data.get("stage"), data.get("temperature"), data.get("score"))
            result = {"status": "success" if success else "error", "action": "stage_updated"}
        elif action == "schedule_meeting":
            result = agents()["meeting"].run({"action": "schedule", "lead": data, **data})
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        return {
            "status": "processed",
            "action": action,
            "source": payload.source,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "action": action, "error": str(e), "timestamp": datetime.now().isoformat()}
        )


# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Starting SalesAI SDR FastAPI Backend...")
    print("   Docs:     http://localhost:8000/docs")
    print("   N8N Hook: http://localhost:8000/webhook/n8n")
    print("   Health:   http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
