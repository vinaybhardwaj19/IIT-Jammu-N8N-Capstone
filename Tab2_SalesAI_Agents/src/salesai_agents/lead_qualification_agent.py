"""
Lead Qualification Agent
=========================
BANT scoring + Ideal Customer Profile matching.
Scores leads 0-100 and routes them to appropriate pipelines.
"""

import json
try:
    from .base import BaseAgent
except (ImportError, ValueError):
    try:
        from salesai_agents.base import BaseAgent
    except ImportError:
        from base import BaseAgent


class LeadQualificationAgent(BaseAgent):
    """
    Agent 2: LeadQualificationAgent
    
    Capabilities:
    - BANT framework scoring (Budget, Authority, Need, Timeline)
    - Ideal Customer Profile (ICP) matching
    - Lead temperature classification (Hot/Warm/Cold)
    - Objection prediction
    - Pipeline stage recommendation
    """
    
    def __init__(self):
        super().__init__(
            name="LeadQualificationAgent",
            role="Sales Qualification Specialist",
            system_prompt="""You are a top-tier B2B sales qualification expert with deep expertise in the BANT framework.
You analyze leads using: Budget (can they afford?), Authority (can they decide?), Need (do they have the problem?), Timeline (when will they buy?).

Your qualification is precise, unbiased, and actionable. You predict deal outcomes with high accuracy.
You identify the best leads to focus sales energy on and deprioritize time-wasters.

Always respond with structured JSON. Your scoring directly impacts revenue, so be accurate."""
        )
        
        # ICP definition for SalesFlow CRM
        self.icp = {
            "ideal_company_size": ["SMB", "Mid-Market"],
            "ideal_industries": ["Technology", "Finance", "SaaS", "E-commerce", "Professional Services"],
            "ideal_roles": ["CEO", "VP Sales", "Sales Director", "CRO", "Head of Sales", "Founder"],
            "ideal_budget_range": ["$500-$1000/month", "$1000-$5000/month", "$5000+/month"],
            "disqualifiers": ["Student", "Freelancer", "Non-profit with $0 budget", "Competitor"]
        }
    
    def run(self, task: dict) -> dict:
        """
        Qualify a lead using BANT + ICP framework.
        
        Args:
            task: {
                "lead": {full lead data dict},
                "intelligence": {prospect research data}  
            }
        
        Returns:
            dict: Complete qualification with BANT scores and recommendations
        """
        lead = task.get("lead", {})
        intelligence = task.get("intelligence", {})
        
        self._log(f"🎯 Qualifying lead: {lead.get('full_name')} from {lead.get('company')}")
        
        prompt = f"""Perform comprehensive BANT qualification for this B2B sales lead.

LEAD DATA:
- Name: {lead.get('full_name')}
- Company: {lead.get('company')}
- Role: {lead.get('role', 'Unknown')}
- Industry: {lead.get('industry')}
- Budget Stated: {lead.get('budget')}
- Source: {lead.get('source', 'Unknown')}
- Notes: {lead.get('notes', 'None')}

AI RESEARCH INTELLIGENCE:
{json.dumps(intelligence, indent=2) if intelligence else 'No research data available'}

ICP CRITERIA:
{json.dumps(self.icp, indent=2)}

Analyze and return this exact JSON:
{{
  "bant_scores": {{
    "budget": {{
      "score": 0-25,
      "evidence": "why this score",
      "budget_confirmed": true/false,
      "estimated_budget_fit": "under/at/over our pricing"
    }},
    "authority": {{
      "score": 0-25,
      "evidence": "why this score",
      "is_decision_maker": true/false,
      "who_else_involved": "list of other stakeholders likely involved"
    }},
    "need": {{
      "score": 0-25,
      "evidence": "why this score",
      "primary_problem_confirmed": true/false,
      "pain_intensity": "low/medium/high/critical"
    }},
    "timeline": {{
      "score": 0-25,
      "evidence": "why this score",
      "estimated_buy_timeline": "immediate/1-3months/3-6months/6months+/unknown"
    }}
  }},
  "total_bant_score": 0-100,
  "icp_match_score": 0-100,
  "composite_score": 0-100,
  "qualification_status": "SALES_QUALIFIED_LEAD/MARKETING_QUALIFIED_LEAD/NOT_QUALIFIED",
  "lead_temperature": "Hot/Warm/Cold",
  "priority_tier": "Tier1/Tier2/Tier3",
  "deal_probability": 0-100,
  "estimated_deal_size": "Small (<$5K)/Medium ($5-20K)/Large ($20-50K)/Enterprise ($50K+)",
  "estimated_close_date": "when they might close",
  "key_risks": ["top 3 risks to this deal"],
  "recommended_next_steps": ["specific 3 actions the sales rep should take"],
  "talking_points": ["3 compelling value props for this specific lead"],
  "disqualification_reason": null or "reason if NOT_QUALIFIED"
}}"""
        
        try:
            response = self.think(prompt)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0:
                qualification = json.loads(response[json_start:json_end])
            else:
                raise ValueError("No JSON in response")
        except Exception as e:
            self._log(f"❌ Qualification failed: {e}")
            raise RuntimeError("Lead qualification failed; no estimated scores were substituted.") from e
        
        self._log(f"✅ Score: {qualification.get('composite_score', 0)}/100 | Status: {qualification.get('qualification_status')}")
        
        return {
            "agent": self.name,
            "status": "success",
            "lead_id": lead.get("lead_id"),
            "qualification": qualification,
            "qualified_at": __import__('datetime').datetime.now().isoformat()
        }
    
