"""
Prospect Research Agent — Upgraded with Real Web Data
======================================================
Deep company and contact intelligence gathering.
Now combines REAL web research (DuckDuckGo, website scraping, news)
with AI-generated insights for maximum accuracy.
"""

import json
try:
    from .base import BaseAgent
    from ..tools.web_research import enrich_lead
except (ImportError, ValueError):
    try:
        from salesai_agents.base import BaseAgent
        from tools.web_research import enrich_lead
    except ImportError:
        from base import BaseAgent
        def enrich_lead(*args, **kwargs): return {}



class ProspectResearchAgent(BaseAgent):
    """
    Agent 1: ProspectResearchAgent
    
    Capabilities:
    - Company intelligence (industry, size, tech stack, news)
    - Contact profiling (role, seniority, likely pain points)
    - Competitive intelligence (what competitors they use)
    - Personalization hooks (recent events, achievements)
    - LinkedIn-style profile synthesis
    """
    
    def __init__(self):
        super().__init__(
            name="ProspectResearchAgent",
            role="B2B Sales Intelligence Analyst",
            system_prompt="""You are an elite B2B sales intelligence analyst with 15 years of experience.
You research companies and prospects with laser precision to enable highly personalized outreach.

Your research covers:
- Company profile: size, revenue, industry, growth stage, tech stack
- Contact profile: seniority, decision-making power, LinkedIn presence, career history
- Business challenges: current pain points based on industry trends
- Recent triggers: funding, hiring sprees, product launches, awards
- Personalization hooks: specific angles to open a conversation naturally
- Competitive landscape: what solutions they currently use and why they might switch

Always structure your response as a valid JSON object with clear sections.
Your intelligence is used by sales reps to book meetings and close deals.
Be specific, data-rich, and always focus on information useful for sales outreach."""
        )
    
    def run(self, task: dict) -> dict:
        """
        Research a prospect company and contact.
        
        Args:
            task: {
                "company_name": str,
                "contact_name": str,
                "contact_role": str,
                "industry": str,
                "website": str (optional)
            }
        
        Returns:
            dict: Complete prospect intelligence profile
        """
        self._log(f"🔍 Researching {task.get('contact_name')} at {task.get('company_name')}...")
        
        # ── STEP 0: Real web enrichment (live data) ───────────────
        self._log("🌐 Fetching real web data...")
        real_data = {}
        try:
            real_data = enrich_lead(
                company_name=task.get("company_name", ""),
                contact_name=task.get("contact_name", ""),
                website=task.get("website", ""),
                industry=task.get("industry", "")
            )
            sources = real_data.get("data_sources", [])
            self._log(f"✅ Web data fetched | Sources: {', '.join(sources) if sources else 'none'}")
        except Exception as e:
            self._log(f"⚠️ Web fetch failed (using AI only): {e}")
        
        # Build enrichment context for AI
        enrichment_context = ""
        if real_data:
            summary = real_data.get("summary", {})
            tech_stack = real_data.get("tech_stack_detected", [])
            news = real_data.get("recent_news", [])
            website_desc = real_data.get("website_data", {}).get("description", "")
            web_text = real_data.get("company_web_info", {}).get("raw_text", "")
            
            enrichment_context = f"""
REAL WEB DATA (live, verified):
- Website live: {real_data.get('website_data', {}).get('live', 'Unknown')}
- Website description: {website_desc[:200] if website_desc else 'N/A'}
- Web intel: {web_text[:300] if web_text else 'N/A'}
- Detected tech stack: {', '.join(tech_stack) if tech_stack else 'Not detected'}
- Recent news: {'; '.join([n.get('headline', '')[:100] for n in news[:3]]) if news else 'No news found'}
- Business triggers: {'; '.join(summary.get('business_triggers', [])[:2]) if summary else 'N/A'}
- Current CRM tools detected: {', '.join(summary.get('current_crm_tools', [])) if summary else 'N/A'}
- Data quality: {summary.get('data_quality', 'low') if summary else 'low'}
"""

        prompt = f"""Research this B2B prospect and return a comprehensive intelligence profile as JSON.
Use the REAL WEB DATA provided below to make the profile accurate and specific.
{enrichment_context}

Now, analyze and return a comprehensive intelligence profile as JSON:

Company: {task.get('company_name', 'Unknown')}
Contact: {task.get('contact_name', 'Unknown')}
Role: {task.get('contact_role', 'Unknown')}
Industry: {task.get('industry', 'Unknown')}
Website: {task.get('website', 'Not provided')}

Return a JSON object with exactly these fields:
{{
  "company_profile": {{
    "estimated_size": "startup/smb/mid-market/enterprise",
    "estimated_revenue": "revenue range",
    "growth_stage": "early/growth/mature",
    "tech_stack_likely": ["list of technologies they likely use"],
    "business_model": "B2B/B2C/marketplace etc",
    "key_challenges": ["3-4 specific challenges for this industry"],
    "recent_triggers": ["funding/hiring/product news that creates sales opportunity"]
  }},
  "contact_profile": {{
    "seniority_level": "C-Suite/VP/Director/Manager/IC",
    "decision_making_power": "high/medium/low",
    "likely_kpis": ["what metrics they are judged on"],
    "communication_style": "data-driven/relationship-focused/executive-brief",
    "linkedin_headline_guess": "likely LinkedIn headline",
    "personality_type": "analytical/driver/expressive/amiable"
  }},
  "pain_points": {{
    "primary_pain": "The #1 business problem they likely face",
    "secondary_pains": ["2-3 other significant challenges"],
    "emotional_drivers": ["fear of/desire for what drives decisions"],
    "urgency_indicators": "what makes this urgent NOW"
  }},
  "personalization_hooks": [
    "Hook 1: specific angle to open conversation",
    "Hook 2: industry trend they care about",
    "Hook 3: company achievement to reference",
    "Hook 4: challenge relevant to their role"
  ],
  "competitive_intel": {{
    "likely_current_solution": "what they probably use now",
    "switching_barriers": ["what makes them NOT switch"],
    "switching_triggers": ["what would make them switch"],
    "our_differentiators": ["why SalesFlow wins against their current solution"]
  }},
  "outreach_strategy": {{
    "best_channel": "email/linkedin/phone/warm-intro",
    "best_time": "when to reach out",
    "opening_line": "the perfect conversation starter",
    "value_prop_focus": "which benefit to lead with for this prospect"
  }}
}}"""
        
        try:
            response = self.think(prompt)
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                intelligence = json.loads(response[json_start:json_end])
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            self._log(f"❌ Research response was not valid JSON: {e}")
            raise RuntimeError("Research failed because the AI response was not valid JSON; no synthetic profile was substituted.") from e
        
        self._log(f"✅ Research complete for {task.get('company_name')}")
        
        return {
            "agent": self.name,
            "status": "success",
            "company": task.get("company_name"),
            "contact": task.get("contact_name"),
            "intelligence": intelligence,
            "real_web_data": real_data.get("summary", {}) if real_data else {},
            "data_sources": real_data.get("data_sources", ["ai_generated"]) if real_data else ["ai_generated"],
            "tech_stack_detected": real_data.get("tech_stack_detected", []) if real_data else [],
            "recent_news": real_data.get("recent_news", []) if real_data else [],
            "research_timestamp": __import__('datetime').datetime.now().isoformat()
        }
    

