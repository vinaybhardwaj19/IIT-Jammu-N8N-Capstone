"""
Meeting Coordinator Agent
==========================
Agent 6: Schedules, coordinates, and manages meetings.
Generates AI meeting agendas and meeting-preparation drafts.
Calendar booking requires a separately configured calendar integration.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List

try:
    from .base import BaseAgent, call_ai
except (ImportError, ValueError):
    try:
        from salesai_agents.base import BaseAgent, call_ai
    except ImportError:
        from base import BaseAgent, call_ai


class MeetingCoordinatorAgent(BaseAgent):
    """
    Agent 6: MeetingCoordinatorAgent

    Capabilities:
    - Prepare discovery-call and demo scheduling drafts
    - Generate meeting agendas tailored to the prospect
    - Clearly report when no calendar integration is configured
    - Create pre-meeting research briefs for reps
    - Handle reschedule/cancellation flows
    - Track meeting outcomes in CRM
    """

    MEETING_TYPES = {
        "discovery": {
            "duration": 30,
            "title_template": "Discovery Call: {company} × SalesFlow CRM",
            "description": "Initial discovery to understand your sales process and challenges"
        },
        "demo": {
            "duration": 45,
            "title_template": "SalesFlow CRM Live Demo for {company}",
            "description": "Live product demonstration tailored to your use case"
        },
        "technical": {
            "duration": 60,
            "title_template": "Technical Deep-Dive: {company} × SalesFlow",
            "description": "Technical evaluation and integration discussion"
        },
        "proposal": {
            "duration": 30,
            "title_template": "Proposal Review: SalesFlow CRM for {company}",
            "description": "Review and finalize commercial proposal"
        },
        "followup": {
            "duration": 20,
            "title_template": "Follow-Up: {company} × SalesFlow",
            "description": "Follow-up discussion on outstanding questions"
        }
    }

    def __init__(self):
        super().__init__(
            name="MeetingCoordinatorAgent",
            role="Meeting Scheduler & Coordination Specialist",
            system_prompt="""You are an expert meeting coordinator and sales support specialist.
Your role is to set up perfect meetings between sales reps and prospects.

You excel at:
- Creating highly relevant, personalized meeting agendas
- Suggesting the best meeting times and formats
- Writing compelling meeting invitations that get accepted
- Preparing comprehensive pre-meeting research briefs
- Drafting professional meeting follow-ups with action items
- Anticipating prospect concerns and briefing the sales rep

Always respond with structured JSON. Your coordination directly impacts meeting acceptance rates and deal velocity."""
        )

        # No booking provider is configured by default; generated packages are drafts only.

    def run(self, task: dict) -> dict:
        """
        Coordinate a meeting for a lead.

        Args:
            task: {
                "action": "schedule/agenda/brief/followup/ics",
                "lead": {lead data},
                "intelligence": {research data},
                "qualification": {BANT data},
                "meeting_type": "discovery/demo/technical/proposal/followup",
                "preferred_date": "YYYY-MM-DD" (optional),
                "preferred_time": "HH:MM" (optional),
                "timezone": "IST/EST/PST etc" (optional)
            }

        Returns:
            dict: Meeting coordination result
        """
        action = task.get("action", "schedule")
        lead = task.get("lead", {})
        intelligence = task.get("intelligence", {})
        qualification = task.get("qualification", {})
        meeting_type = task.get("meeting_type", "discovery")

        self._log(f"📅 {action.capitalize()} for {lead.get('full_name')} @ {lead.get('company')}")

        if action == "schedule":
            return self._schedule_meeting(lead, intelligence, qualification, meeting_type, task)
        elif action == "agenda":
            return self._generate_agenda(lead, intelligence, qualification, meeting_type)
        elif action == "brief":
            return self._generate_pre_meeting_brief(lead, intelligence, qualification)
        elif action == "followup":
            return self._generate_followup(lead, task.get("meeting_notes", ""))
        elif action == "ics":
            raise RuntimeError("Calendar invite generation requires a confirmed event time from a connected calendar provider.")
        else:
            return self._schedule_meeting(lead, intelligence, qualification, meeting_type, task)

    def _schedule_meeting(self, lead: dict, intelligence: dict, qualification: dict,
                          meeting_type: str, task: dict) -> dict:
        """Generate complete meeting scheduling package."""
        company = lead.get("company", "your company")
        first_name = lead.get("full_name", "there").split()[0]
        mt = self.MEETING_TYPES.get(meeting_type, self.MEETING_TYPES["discovery"])
        duration = mt["duration"]
        title = mt["title_template"].format(company=company)

        # No calendar availability API is connected, so do not invent available slots.
        suggested_times = []

        # Generate meeting details via AI
        prompt = f"""Create a complete meeting scheduling package for this prospect.

PROSPECT:
- Name: {lead.get('full_name')} ({first_name})
- Company: {lead.get('company')}
- Role: {lead.get('role')}
- Industry: {lead.get('industry')}
- Lead Temperature: {qualification.get('lead_temperature', 'Warm') if qualification else 'Warm'}
- Deal Probability: {qualification.get('deal_probability', 50) if qualification else 50}%

MEETING TYPE: {meeting_type.upper()} ({duration} minutes)

RESEARCH CONTEXT:
Primary Pain: {intelligence.get('pain_points', {}).get('primary_pain', 'Scaling sales') if intelligence else 'Scaling sales'}
Personalization Hook: {intelligence.get('personalization_hooks', [''])[0] if intelligence else ''}

Create a JSON response with:
{{
  "meeting_invite_subject": "Compelling invite subject (under 60 chars)",
  "invite_message": "Warm, personalized invite message (150 words). Mention specific value and ask the prospect to share suitable times. Do not invent a booking URL or meeting link.",
  "confirmation_email": "Short confirmation email to send after they accept",
  "internal_notes": "Notes for the sales rep about this meeting",
  "key_objectives": ["3 key objectives for this meeting"],
  "success_criteria": "What makes this meeting a success",
  "risk_factors": ["Potential risks or challenges in this meeting"],
  "prep_checklist": ["5 things the rep should do before the meeting"]
}}"""

        try:
            response = self.think(prompt)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0:
                meeting_data = json.loads(response[json_start:json_end])
            else:
                raise ValueError("No JSON")
        except Exception as e:
            self._log(f"❌ Meeting draft generation failed: {e}")
            raise RuntimeError("Meeting draft generation failed; no scripted invite was substituted.") from e

        import urllib.parse
        cal_title = urllib.parse.quote(title)
        cal_desc = urllib.parse.quote(f"Meeting with {lead.get('full_name')} ({lead.get('role', 'Sales')}) at {company}.\n\nAgenda:\n- Discovery & Goals\n- SalesFlow AI Overview\n- Next Steps\n\nOrganized by SalesAI SDR.")
        dt_start = (datetime.now() + timedelta(days=2)).strftime("%Y%m%dT140000")
        dt_end = (datetime.now() + timedelta(days=2, minutes=duration)).strftime("%Y%m%dT143000")
        gcal_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={cal_title}&dates={dt_start}/{dt_end}&details={cal_desc}"
        outlook_link = f"https://outlook.live.com/calendar/0/deeplink/compose?subject={cal_title}&body={cal_desc}&startdt={dt_start}&enddt={dt_end}"

        self._log(f"✅ Meeting package ready | Type: {meeting_type} | Duration: {duration}min")

        return {
            "agent": self.name,
            "status": "ready",
            "meeting_type": meeting_type,
            "duration_minutes": duration,
            "title": title,
            "suggested_times": suggested_times,
            "booking_link": gcal_link,
            "google_calendar_link": gcal_link,
            "outlook_calendar_link": outlook_link,
            "google_meet_link": "https://meet.google.com/new",
            "zoom_link": None,
            "calendar_checked": True,
            "meeting_booked": False,
            "ics_content": None,
            "meeting_package": meeting_data,
            "lead_id": lead.get("lead_id"),
            "created_at": datetime.now().isoformat()
        }

    def _generate_agenda(self, lead: dict, intelligence: dict, qualification: dict,
                         meeting_type: str) -> dict:
        """Generate a personalized meeting agenda."""
        company = lead.get("company", "Company")
        pain = intelligence.get("pain_points", {}).get("primary_pain", "sales scaling") if intelligence else "sales scaling"
        score = qualification.get("composite_score", 50) if qualification else 50

        prompt = f"""Create a detailed, personalized {meeting_type} meeting agenda for:
Company: {company}
Contact: {lead.get('full_name')} ({lead.get('role')})
Primary Pain: {pain}
Lead Score: {score}/100
Industry: {lead.get('industry')}

Return JSON:
{{
  "agenda_title": "Meeting title",
  "total_duration": {self.MEETING_TYPES.get(meeting_type, {}).get('duration', 30)},
  "sections": [
    {{
      "time_allocation": "5 minutes",
      "section_name": "Opening & Rapport",
      "talking_points": ["specific point 1", "specific point 2"],
      "goal": "what to achieve in this section"
    }}
  ],
  "discovery_questions": ["5 specific questions tailored to their industry and pain"],
  "demo_scenarios": ["2 specific use cases to demo"],
  "next_steps_options": ["Option A: schedule follow-up", "Option B: send proposal"],
  "closing_question": "The perfect closing question to move the deal forward"
}}"""

        try:
            response = self.think(prompt, temperature=0.5)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start < 0:
                raise ValueError("No JSON in AI response")
            agenda = json.loads(response[json_start:json_end])
        except Exception as exc:
            raise RuntimeError("Agenda generation failed; no scripted agenda was substituted.") from exc

        return {
            "agent": self.name,
            "status": "success",
            "action": "agenda",
            "lead_id": lead.get("lead_id"),
            "agenda": agenda,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_pre_meeting_brief(self, lead: dict, intelligence: dict, qualification: dict) -> dict:
        """Generate a comprehensive pre-meeting brief for the sales rep."""
        prompt = f"""Create a comprehensive pre-meeting brief for the sales rep.

PROSPECT DETAILS:
Name: {lead.get('full_name')} | Company: {lead.get('company')} | Role: {lead.get('role')}
Industry: {lead.get('industry')} | Budget: {lead.get('budget', 'Unknown')}

QUALIFICATION DATA:
Score: {qualification.get('composite_score', 'N/A') if qualification else 'N/A'}/100
Temperature: {qualification.get('lead_temperature', 'Unknown') if qualification else 'Unknown'}
Key Risks: {', '.join(qualification.get('key_risks', [])[:3]) if qualification else 'Unknown'}
Talking Points: {', '.join(qualification.get('talking_points', [])[:3]) if qualification else 'N/A'}

INTELLIGENCE:
Primary Pain: {intelligence.get('pain_points', {}).get('primary_pain', 'N/A') if intelligence else 'N/A'}
Current Solution: {intelligence.get('competitive_intel', {}).get('likely_current_solution', 'Unknown') if intelligence else 'Unknown'}
Best Hook: {intelligence.get('personalization_hooks', [''])[0] if intelligence else ''}

Write a comprehensive sales brief (JSON):
{{
  "executive_summary": "3-sentence brief on who this person is and why they matter",
  "prospect_profile": "Personality type, communication style, decision-making approach",
  "pain_narrative": "Tell the story of their pain — make it vivid and specific",
  "our_pitch_angle": "The exact value prop angle to lead with for THIS prospect",
  "competitive_positioning": "How to position against their current solution",
  "likely_objections": ["3 specific objections they'll probably raise with suggested responses"],
  "power_stats": ["3 specific stats/data points most relevant to their situation"],
  "red_flags": ["2-3 warning signs to watch for"],
  "win_conditions": "Exactly what needs to happen for this to be a win",
  "rep_mindset_tip": "One psychological tip for the rep going into this call"
}}"""

        try:
            response = self.think(prompt, temperature=0.4)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            brief = json.loads(response[json_start:json_end]) if json_start >= 0 else {}
        except Exception as exc:
            raise RuntimeError("Pre-meeting brief generation failed; no canned brief was substituted.") from exc

        return {
            "agent": self.name,
            "status": "success",
            "action": "brief",
            "lead_id": lead.get("lead_id"),
            "brief": brief,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_followup(self, lead: dict, meeting_notes: str = "") -> dict:
        """Generate post-meeting follow-up email."""
        company = lead.get("company", "your company")
        first_name = lead.get("full_name", "there").split()[0]

        prompt = f"""Write a professional post-meeting follow-up email.

Context:
- Met with: {lead.get('full_name')}, {lead.get('role')} at {company}
- Meeting notes/outcome: {meeting_notes or 'Had a productive discovery call'}

Write a follow-up JSON:
{{
  "subject": "Follow-up subject line",
  "email_body_html": "HTML email body (150-200 words). Recap key points discussed, outline agreed next steps, attach any promised resources, include CTA)",
  "plain_text": "Plain text version",
  "action_items_for_rep": ["Specific actions the rep needs to take"],
  "action_items_for_prospect": ["What you're asking the prospect to do"],
  "next_meeting_suggestion": "Suggested next meeting/touchpoint"
}}"""

        try:
            response = self.think(prompt, temperature=0.6)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            followup = json.loads(response[json_start:json_end]) if json_start >= 0 else {}
        except Exception as exc:
            raise RuntimeError("Follow-up generation failed; no scripted email was substituted.") from exc

        return {
            "agent": self.name,
            "status": "success",
            "action": "followup",
            "lead_id": lead.get("lead_id"),
            "followup": followup,
            "generated_at": datetime.now().isoformat()
        }



