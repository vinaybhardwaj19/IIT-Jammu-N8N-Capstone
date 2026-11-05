"""
Deal Health Sentinel Agent (RevOps & Slippage Predictor)
=========================================================
Autonomous RevOps specialist that monitors active pipeline deals,
detects deal stagnation, single-threaded risks, and predicts win/loss probability.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

try:
    from .base import BaseAgent
except (ImportError, ValueError):
    try:
        from salesai_agents.base import BaseAgent
    except ImportError:
        from base import BaseAgent

try:
    from tools.crm_database import get_all_leads, get_activities, get_connection
except ImportError:
    from ..tools.crm_database import get_all_leads, get_activities, get_connection


class DealHealthAgent(BaseAgent):
    """
    Agent 7: DealHealthAgent (RevOps & Pipeline Health Sentinel)
    
    Capabilities:
    - Real-time deal velocity tracking
    - Single-threaded risk identification
    - Automated Next Best Action (NBA) recommendations
    - Executive RevOps health audit and slippage prevention
    """

    def __init__(self):
        super().__init__(
            name="DealHealthAgent",
            role="RevOps Pipeline Sentinel & Deal Slippage Predictor",
            system_prompt="""You are a veteran Revenue Operations (RevOps) Director.
You analyze B2B sales pipeline health with strict mathematical discipline.
You assess deal velocity, buyer engagement frequency, decision-maker coverage, and objection severity.
Your goal is to save at-risk enterprise deals before they slip past the quarter close."""
        )

    def analyze_deal(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Compute algorithmic and AI health score for an individual deal."""
        lead_id = lead.get("lead_id", "UNKNOWN")
        company = lead.get("company", "Unknown Company")
        stage = lead.get("pipeline_stage", "New Lead")
        composite_score = int(lead.get("composite_score", 0) or 0)
        lead_temp = lead.get("lead_temperature", "Cold")
        
        # 1. Base Score calculation
        health_score = 65
        risk_factors = []
        positive_signals = []

        # Temperature & qualification impact
        if lead_temp == "Hot":
            health_score += 15
            positive_signals.append("High intent: Lead temperature is HOT")
        elif lead_temp == "Warm":
            health_score += 5
            positive_signals.append("Moderate intent: Warm lead")
        else:
            health_score -= 15
            risk_factors.append("Cold engagement temperature")

        # BANT Score impact
        if composite_score >= 75:
            health_score += 15
            positive_signals.append(f"Strong qualification score ({composite_score}/100)")
        elif composite_score < 40:
            health_score -= 20
            risk_factors.append(f"Weak BANT score ({composite_score}/100)")

        # Stage velocity check
        if stage in ["Proposal Sent", "Negotiation"]:
            if composite_score < 60:
                health_score -= 15
                risk_factors.append("Proposal out with sub-optimal qualification")
            else:
                health_score += 10
                positive_signals.append("Advanced stage with qualified prospect")

        # Single-threaded risk (no alternate contact)
        if not lead.get("phone") or not lead.get("role"):
            health_score -= 10
            risk_factors.append("Single-threaded account: missing secondary stakeholder details")
        else:
            positive_signals.append("Contact identity fully enriched")

        # Normalize score
        health_score = max(10, min(98, health_score))

        # Health status
        if health_score >= 75:
            health_status = "HEALTHY"
            color = "green"
        elif health_score >= 50:
            health_status = "AT RISK"
            color = "amber"
        else:
            health_status = "CRITICAL SLIPPAGE"
            color = "red"

        # Next Best Action prompt
        prompt = f"""Assess pipeline deal health for {company} (Stage: {stage}, Health: {health_score}/100, Status: {health_status}).
Risk factors: {', '.join(risk_factors) if risk_factors else 'None'}
Positive signals: {', '.join(positive_signals)}

Provide a 2-sentence executive action plan:
1. Immediate tactical action for the account executive.
2. Recommended multi-threading or collateral angle."""

        recommendation = self.think(prompt, temperature=0.3)

        return {
            "lead_id": lead_id,
            "company": company,
            "stage": stage,
            "health_score": health_score,
            "health_status": health_status,
            "color": color,
            "risk_factors": risk_factors,
            "positive_signals": positive_signals,
            "next_best_action": recommendation.strip(),
            "analyzed_at": datetime.now().isoformat()
        }

    def run_pipeline_audit(self) -> Dict[str, Any]:
        """Audit all leads in the database and return aggregate pipeline health."""
        leads = get_all_leads(limit=100)
        if not leads:
            return {
                "total_deals_analyzed": 0,
                "healthy_count": 0,
                "at_risk_count": 0,
                "critical_count": 0,
                "deals": []
            }

        deal_audits = [self.analyze_deal(lead) for lead in leads]
        
        healthy = [d for d in deal_audits if d["health_status"] == "HEALTHY"]
        at_risk = [d for d in deal_audits if d["health_status"] == "AT RISK"]
        critical = [d for d in deal_audits if d["health_status"] == "CRITICAL SLIPPAGE"]

        avg_health = sum(d["health_score"] for d in deal_audits) / len(deal_audits)

        return {
            "total_deals_analyzed": len(deal_audits),
            "average_pipeline_health": round(avg_health, 1),
            "healthy_count": len(healthy),
            "at_risk_count": len(at_risk),
            "critical_count": len(critical),
            "deals": deal_audits,
            "audit_timestamp": datetime.now().isoformat()
        }

    def run(self, task: dict) -> dict:
        action = task.get("action", "audit")
        if action == "analyze_deal":
            return self.analyze_deal(task.get("lead", {}))
        return self.run_pipeline_audit()
