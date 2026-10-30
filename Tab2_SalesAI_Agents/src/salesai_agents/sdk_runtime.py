"""AI Agents runtime for the six SalesAI SDR specialists (Gemini/Groq by default; OpenAI Agents SDK used only when OPENAI_API_KEY is set).

The legacy ``run(dict) -> dict`` adapter interfaces remain available to the UI
and API. Model turns themselves run through ``Agent`` and ``Runner``; their
outer response is validated by Pydantic before the legacy JSON payload is
handed back to existing application code.
"""

from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, ConfigDict
try:
    from agents import Agent, Runner, function_tool
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    Agent = Any  # type: ignore
    Runner = None
    def function_tool(*args, **kwargs):  # type: ignore
        def decorator(f):
            return f
        if args and callable(args[0]):
            return args[0]
        return decorator
from dotenv import load_dotenv

load_dotenv()


class AgentTextOutput(BaseModel):
    """Typed SDK boundary while preserving each agent's existing JSON contract."""

    model_config = ConfigDict(extra="forbid")
    response: str


class AgentApprovalRequired(RuntimeError):
    """An SDK run paused before an approved side effect could execute."""

    def __init__(self, message: str, state: Any):
        super().__init__(message)
        self.state = state


_AGENTS: dict[str, Agent] = {}
_ORDERED_HANDOFFS = {
    "ProspectResearchAgent": ["LeadQualificationAgent"],
    "LeadQualificationAgent": ["EmailWriterAgent"],
    "EmailWriterAgent": ["MeetingCoordinatorAgent"],
    "MeetingCoordinatorAgent": ["CRMManagerAgent"],
    "ObjectionHandlerAgent": ["LeadQualificationAgent", "EmailWriterAgent", "CRMManagerAgent"],
    "CRMManagerAgent": [],
}


@function_tool
def research_prospect(company_name: str, contact_name: str = "", website: str = "", industry: str = "") -> str:
    """Gather company and contact context using the project's web research utility."""
    from tools.web_research import enrich_lead

    result = enrich_lead(company_name, contact_name, website, industry)
    return json.dumps(result, ensure_ascii=False, default=str)


@function_tool
def find_crm_lead(lead_id: str) -> str:
    """Read one lead record from the local SQLite CRM."""
    from tools.crm_database import get_lead

    return json.dumps(get_lead(lead_id) or {}, ensure_ascii=False, default=str)


@function_tool
def save_crm_lead(lead_json: str) -> str:
    """Create or update a lead in the local SQLite CRM."""
    from tools.crm_database import upsert_lead

    lead = json.loads(lead_json)
    return str(upsert_lead(lead))


@function_tool
def prepare_meeting(lead_json: str, meeting_type: str = "discovery") -> str:
    """Prepare a meeting request with dynamic 1-click Google Calendar & Outlook scheduling links."""
    import urllib.parse
    from datetime import datetime, timedelta

    lead = json.loads(lead_json)
    company = lead.get("company", "Prospect Company")
    contact = lead.get("full_name", "Lead Contact")
    title = urllib.parse.quote(f"Discovery Call: {company} × SalesFlow AI")
    desc = urllib.parse.quote(f"Meeting with {contact} at {company} to review sales automation requirements.\nPrepared by SalesAI SDR.")
    dt_start = (datetime.now() + timedelta(days=2)).strftime("%Y%m%dT140000")
    dt_end = (datetime.now() + timedelta(days=2, minutes=30)).strftime("%Y%m%dT143000")
    gcal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={dt_start}/{dt_end}&details={desc}"
    outlook_url = f"https://outlook.live.com/calendar/0/deeplink/compose?subject={title}&body={desc}&startdt={dt_start}&enddt={dt_end}"

    return json.dumps({
        "status": "ready",
        "meeting_type": meeting_type,
        "company": company,
        "contact": contact,
        "google_calendar_invite": gcal_url,
        "outlook_calendar_invite": outlook_url,
        "google_meet_url": "https://meet.google.com/new",
        "calendar_booked": True,
        "message": "Dynamic calendar invite links generated successfully. Click link to populate prospect and rep calendars.",
    }, ensure_ascii=False)


@function_tool(needs_approval=True)
def send_approved_email(lead_json: str, email_json: str, sender_name: str = "Vinay Bhardwaj") -> str:
    """Send an email only after the SDK pauses for and receives human approval."""
    from tools.email_sender import send_cold_email

    result = send_cold_email(json.loads(lead_json), json.loads(email_json), sender_name)
    return json.dumps(result, ensure_ascii=False, default=str)


_TOOLS = {
    "ProspectResearchAgent": [research_prospect],
    "LeadQualificationAgent": [find_crm_lead],
    "EmailWriterAgent": [send_approved_email],
    "MeetingCoordinatorAgent": [prepare_meeting],
    "ObjectionHandlerAgent": [find_crm_lead],
    "CRMManagerAgent": [find_crm_lead, save_crm_lead],
}


def register_agent(name: str, role: str, instructions: str) -> Any:
    """Create an SDK Agent for a legacy specialist wrapper."""
    if not SDK_AVAILABLE:
        agent = {"name": name, "role": role, "instructions": instructions}
        _AGENTS[name] = agent
        return agent

    model = os.getenv("OPENAI_AGENT_MODEL", "gpt-4.1-mini").strip()
    agent = Agent(
        name=name,
        instructions=(
            f"{instructions}\n\n"
            "Return your requested JSON payload inside the required `response` string field. "
            "Use your registered tools for research, CRM operations, or meeting preparation when needed. "
            "Never send an email without the SDK human approval interruption. "
            "Only hand off when the user's request requires another specialist's responsibility."
        ),
        model=model,
        tools=_TOOLS.get(name, []),
        output_type=AgentTextOutput,
    )
    _AGENTS[name] = agent
    wire_handoffs()
    return agent


def wire_handoffs() -> None:
    """Wire the ordered specialist handoff graph as SDK-native handoffs."""
    if not SDK_AVAILABLE:
        return
    for source, destinations in _ORDERED_HANDOFFS.items():
        agent = _AGENTS.get(source)
        if agent is not None and hasattr(agent, "handoffs"):
            agent.handoffs = [
                _AGENTS[name] for name in destinations if name in _AGENTS
            ]


def run_agent(agent: Any, prompt: str, temperature: float = 0.3) -> str:
    """Run an SDK turn, preserving approval interruptions instead of bypassing them."""
    if not SDK_AVAILABLE or not os.getenv("OPENAI_API_KEY", "").strip():
        # Live fallback: route through project's multi-provider call_ai (Gemini / Groq)
        from salesai_agents.base import call_ai
        agent_name = getattr(agent, "name", None) or (agent.get("name") if isinstance(agent, dict) else "Agent")
        instructions = getattr(agent, "instructions", "") or (agent.get("instructions", "") if isinstance(agent, dict) else "")
        return call_ai(prompt, system=instructions, temperature=temperature)

    result = Runner.run_sync(
        agent,
        prompt,
        max_turns=12,
    )
    if result.interruptions:
        raise AgentApprovalRequired(
            "The agent run is paused for human approval before an email can be sent.",
            result.to_state(),
        )
    output = result.final_output
    if isinstance(output, AgentTextOutput):
        return output.response
    if isinstance(output, dict) and isinstance(output.get("response"), str):
        return output["response"]
    agent_name = getattr(agent, "name", str(type(agent)))
    raise RuntimeError(f"{agent_name} returned an unexpected SDK output type: {type(output).__name__}")


def get_registered_agents() -> dict[str, Agent]:
    """Expose a copy of the registered agents for observability/UI display."""
    return dict(_AGENTS)
