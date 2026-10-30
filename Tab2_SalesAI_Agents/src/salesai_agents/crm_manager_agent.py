"""
CRM Manager Agent — Upgraded with Real SQLite Persistence
==========================================================
Manages pipeline data, tracks deals, generates reports.
Now uses real SQLite database instead of in-memory dict.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from .base import BaseAgent, call_ai
    from ..tools.crm_database import (
        upsert_lead, update_lead_stage, get_lead, get_all_leads,
        get_pipeline_stats, save_research, save_qualification, save_email,
        get_emails_for_lead, log_activity, get_activities, save_meeting,
        get_meetings, log_objection, mark_email_sent, estimate_deal_amount
    )
except (ImportError, ValueError):
    from salesai_agents.base import BaseAgent, call_ai
    from tools.crm_database import (
        upsert_lead, update_lead_stage, get_lead, get_all_leads,
        get_pipeline_stats, save_research, save_qualification, save_email,
        get_emails_for_lead, log_activity, get_activities, save_meeting,
        get_meetings, log_objection, mark_email_sent, estimate_deal_amount
    )


class CRMManagerAgent(BaseAgent):
    """
    Agent 5: CRMManagerAgent — Real SQLite-backed CRM

    Manages the complete sales pipeline with persistent storage.
    Every lead, email, meeting, and activity is saved to salesai.db
    """

    PIPELINE_STAGES = [
        "New Lead",
        "Research Complete",
        "Qualified",
        "Email Sent",
        "Meeting Scheduled",
        "Demo Done",
        "Proposal Sent",
        "Negotiation",
        "Closed Won",
        "Closed Lost"
    ]

    def __init__(self):
        super().__init__(
            name="CRMManagerAgent",
            role="CRM Pipeline Manager & Deal Coordinator",
            system_prompt="""You are an expert CRM administrator and sales operations specialist.
You manage the complete sales pipeline, track all interactions, and generate actionable reports.
Your job is to ensure no lead falls through the cracks and every deal gets the attention it needs.

You provide:
- Pipeline health reports with clear action items
- Deal risk assessment and intervention recommendations
- Activity logging and next-step tracking
- Win/loss pattern analysis
- Revenue forecasting based on pipeline data
Always respond with actionable insights, not just observations."""
        )

    def run(self, task: dict) -> dict:
        """
        Manage CRM operations.

        Actions:
            log_lead        — Save/update a lead in the database
            update_stage    — Move lead to new pipeline stage
            get_lead        — Retrieve a specific lead
            get_pipeline    — Full pipeline report
            forecast        — Revenue forecast
            log_activity    — Record an activity
            save_email      — Store an email
            log_meeting     — Save meeting data
            log_objection   — Record an objection
            get_stats       — Quick dashboard stats
            search_leads    — Filter/search leads
        """
        action = task.get("action", "get_pipeline")
        data = task.get("data", {})

        dispatch = {
            "log_lead":     lambda: self._log_lead(data),
            "update_stage": lambda: self._update_stage(data),
            "get_lead":     lambda: self._get_lead_details(data.get("lead_id")),
            "get_pipeline": lambda: self._get_pipeline_report(data),
            "forecast":     lambda: self._generate_forecast(),
            "log_activity": lambda: self._log_activity(data),
            "save_email":   lambda: self._save_email_record(data),
            "log_meeting":  lambda: self._log_meeting(data),
            "log_objection":lambda: self._log_objection(data),
            "get_stats":    lambda: self._get_dashboard_stats(),
            "search_leads": lambda: self._search_leads(data),
        }

        handler = dispatch.get(action)
        if handler:
            return handler()
        return {"status": "error", "message": f"Unknown action: {action}"}

    # ── Lead Operations ─────────────────────────────────────────

    def _log_lead(self, lead_data: dict) -> dict:
        """Save/update lead to SQLite database."""
        lead_id = upsert_lead(lead_data)
        log_activity(
            lead_id=lead_id,
            activity_type="lead_created",
            description=f"Lead {lead_data.get('full_name')} from {lead_data.get('company')} added to CRM",
            outcome="logged",
            performer="CRMManagerAgent"
        )
        self._log(f"📋 Logged lead {lead_id}: {lead_data.get('company')}")
        return {
            "status": "success",
            "lead_id": lead_id,
            "action": "logged",
            "message": f"Lead saved to database (ID: {lead_id})"
        }

    def _update_stage(self, data: dict) -> dict:
        """Move lead to a new pipeline stage."""
        lead_id = data.get("lead_id")
        new_stage = data.get("stage")
        temperature = data.get("temperature")
        score = data.get("score")

        if not lead_id or not new_stage:
            return {"status": "error", "message": "lead_id and stage required"}

        success = update_lead_stage(lead_id, new_stage, temperature, score)
        if success:
            log_activity(lead_id, "stage_change", f"Moved to {new_stage}", "updated")
            self._log(f"🔄 Updated {lead_id} → {new_stage}")
            return {"status": "success", "lead_id": lead_id, "new_stage": new_stage}
        return {"status": "error", "message": f"Lead {lead_id} not found"}

    def _get_lead_details(self, lead_id: str) -> dict:
        """Get full lead profile with all related data."""
        if not lead_id:
            return {"status": "error", "message": "lead_id required"}

        lead = get_lead(lead_id)
        if not lead:
            return {"status": "error", "message": f"Lead {lead_id} not found"}

        activities = get_activities(lead_id)
        emails = get_emails_for_lead(lead_id)
        meetings = get_meetings(lead_id)

        return {
            "status": "success",
            "lead": lead,
            "activities": activities,
            "emails": emails,
            "meetings": meetings,
            "activity_count": len(activities),
            "email_count": len(emails),
            "meeting_count": len(meetings)
        }

    def _get_pipeline_report(self, filters: dict = None) -> dict:
        """Generate a full pipeline health report with AI insights."""
        stats = get_pipeline_stats()
        all_leads = get_all_leads(limit=200)

        # Build detailed stage breakdown
        stage_breakdown = {}
        for lead in all_leads:
            stage = lead.get("pipeline_stage", "Unknown")
            if stage not in stage_breakdown:
                stage_breakdown[stage] = {"count": 0, "leads": [], "total_value": 0}
            stage_breakdown[stage]["count"] += 1
            stage_breakdown[stage]["leads"].append(lead.get("full_name", "Unknown"))

        # Sum only values actually stored on CRM records; leave unknown amounts unpriced.
        priced = [(lead, estimate_deal_amount(lead.get("estimated_deal_size"))) for lead in all_leads]
        priced = [(lead, amount) for lead, amount in priced if amount is not None]
        pipeline_value = sum(amount for _, amount in priced)
        weighted_forecast = sum(amount * float(lead.get("deal_probability") or 0) / 100 for lead, amount in priced)
        hot_count = stats.get("hot_leads", 0)
        warm_count = stats.get("warm_leads", 0)
        cold_count = stats.get("cold_leads", 0)

        # AI insights on pipeline health
        prompt = f"""Generate a crisp pipeline health report for a sales manager.

Pipeline Snapshot:
- Total Leads: {stats.get('total_leads', 0)}
- Hot: {hot_count} | Warm: {warm_count} | Cold: {cold_count}
- Avg Score: {stats.get('avg_score', 0)}/100
- By Stage: {json.dumps(stats.get('by_stage', {}), indent=2)}
- Recorded estimated deal value: {f'${pipeline_value:,.0f}' if priced else 'not recorded'}
- Leads without a parseable deal estimate: {len(all_leads) - len(priced)}

Summarize only these recorded metrics. Do not invent pipeline values, company facts, or conversion benchmarks. Provide 3 useful insights and 3 actions in 200 words max."""

        ai_insights = self.think(prompt, temperature=0.3)

        return {
            "agent": self.name,
            "action": "pipeline_report",
            "summary": {
                **stats,
                "pipeline_value": f"${pipeline_value:,.0f}" if priced else "Not available — no deal sizes recorded",
                "weighted_forecast": f"${weighted_forecast:,.0f}" if priced else "Not available — no deal sizes recorded",
                "priced_leads": len(priced),
                "unpriced_leads": len(all_leads) - len(priced),
                "stage_breakdown": stage_breakdown
            },
            "top_leads": sorted(all_leads, key=lambda x: x.get("composite_score", 0), reverse=True)[:5],
            "ai_insights": ai_insights,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_forecast(self) -> dict:
        """Calculate a forecast from saved deal values and probabilities only."""
        leads = get_all_leads(limit=1000)
        forecast = {"Hot": 0.0, "Warm": 0.0, "Cold": 0.0}
        weighted_by_temperature = {"Hot": 0.0, "Warm": 0.0, "Cold": 0.0}
        weighted = 0.0
        priced = 0
        for lead in leads:
            amount = estimate_deal_amount(lead.get("estimated_deal_size"))
            if amount is None:
                continue
            priced += 1
            temperature = lead.get("lead_temperature")
            if temperature in forecast:
                forecast[temperature] += amount
                probability_weighted = amount * float(lead.get("deal_probability") or 0) / 100
                weighted_by_temperature[temperature] += probability_weighted
                weighted += probability_weighted

        counts = get_pipeline_stats()

        forecast = {
            "hot_pipeline": forecast["Hot"],
            "warm_pipeline": forecast["Warm"],
            "cold_pipeline": forecast["Cold"],
            "hot_weighted": weighted_by_temperature["Hot"],
            "warm_weighted": weighted_by_temperature["Warm"],
            "cold_weighted": weighted_by_temperature["Cold"],
            "weighted_forecast": weighted,
            "total_pipeline": sum(forecast.values()),
            "priced_leads": priced,
            "unpriced_leads": len(leads) - priced,
            "lead_counts": {
                "hot": counts.get("hot_leads", 0),
                "warm": counts.get("warm_leads", 0),
                "cold": counts.get("cold_leads", 0),
            },
        }

        return {
            "agent": self.name,
            "action": "forecast",
            "forecast": forecast,
            "generated_at": datetime.now().isoformat()
        }

    # ── Activity / Email / Meeting Logging ─────────────────────

    def _log_activity(self, data: dict) -> dict:
        lead_id = data.get("lead_id")
        if not lead_id:
            return {"status": "error", "message": "lead_id required"}
        log_activity(
            lead_id=lead_id,
            activity_type=data.get("activity_type", "note"),
            description=data.get("description", ""),
            outcome=data.get("outcome", ""),
            performer=data.get("performed_by", "SalesAI")
        )
        return {"status": "success", "action": "activity_logged", "lead_id": lead_id}

    def _save_email_record(self, data: dict) -> dict:
        lead_id = data.get("lead_id")
        if not lead_id:
            return {"status": "error", "message": "lead_id required"}
        email_id = save_email(lead_id, data.get("email_type", "cold"), data.get("email_data", {}))
        return {"status": "success", "action": "email_saved", "lead_id": lead_id, "email_id": email_id}

    def _log_meeting(self, data: dict) -> dict:
        lead_id = data.get("lead_id")
        if not lead_id:
            return {"status": "error", "message": "lead_id required"}
        meeting_id = save_meeting(lead_id, data.get("meeting_data", {}))
        log_activity(lead_id, "meeting_scheduled",
                     f"Meeting scheduled: {data.get('meeting_data', {}).get('title', 'Call')}")
        return {"status": "success", "action": "meeting_logged", "lead_id": lead_id, "meeting_id": meeting_id}

    def _log_objection(self, data: dict) -> dict:
        lead_id = data.get("lead_id", "")
        log_objection(
            lead_id=lead_id,
            objection_text=data.get("objection_text", ""),
            obj_type=data.get("objection_type", "general"),
            rebuttal=data.get("rebuttal_used", ""),
            outcome=data.get("outcome", "")
        )
        return {"status": "success", "action": "objection_logged"}

    def _get_dashboard_stats(self) -> dict:
        """Quick stats for the dashboard header."""
        stats = get_pipeline_stats()
        return {
            "status": "success",
            "stats": stats,
            "pipeline_health": "healthy" if stats.get("hot_leads", 0) >= 2 else "needs_attention"
        }

    def _search_leads(self, data: dict) -> dict:
        """Search/filter leads."""
        leads = get_all_leads(
            stage=data.get("stage"),
            temperature=data.get("temperature"),
            limit=data.get("limit", 50)
        )
        return {
            "status": "success",
            "leads": leads,
            "count": len(leads)
        }
