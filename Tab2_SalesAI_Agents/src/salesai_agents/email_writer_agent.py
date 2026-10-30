"""
Email Writer Agent
==================
Hyper-personalized outreach email sequences that convert.
Writes emails that sound genuinely human — warm, specific, concise.
"""

import json
try:
    from .base import BaseAgent
except (ImportError, ValueError):
    try:
        from salesai_agents.base import BaseAgent
    except ImportError:
        from base import BaseAgent


class EmailWriterAgent(BaseAgent):
    """
    Agent 3: EmailWriterAgent
    
    Capabilities:
    - Personalized cold email sequences (5-touch cadence)
    - Subject line A/B variants
    - Follow-up emails with progressive value
    - Breakup email that re-engages ghosted prospects
    - LinkedIn connection message variants
    """
    
    def __init__(self):
        super().__init__(
            name="EmailWriterAgent",
            role="B2B Sales Copywriter",
            system_prompt="""You are an elite B2B sales copywriter who has written emails that generated $50M+ in pipeline.
Your emails:
- Are concise (100-200 words for cold, 80-120 for follow-ups)
- Feel genuinely human — never robotic or template-like
- Always reference something specific about the prospect
- Use the PAS framework (Problem → Agitate → Solution) or AIDA
- Include ONE clear, low-friction call to action
- Subject lines are under 50 chars and create genuine curiosity
- NEVER use buzzwords like "synergy", "leverage", "circle back", "touching base"
- Always write from the perspective of helping, not selling

Format: Return the email as a JSON object with subject and body fields."""
        )
    
    def run(self, task: dict) -> dict:
        """
        Write a personalized email for a prospect.
        
        Args:
            task: {
                "lead": {lead data},
                "intelligence": {research data},
                "qualification": {BANT data},
                "email_type": "cold/followup1/followup2/followup3/breakup",
                "sender_name": str,
                "sender_title": str
            }
        
        Returns:
            dict: Email with subject, body, linkedin_message
        """
        lead = task.get("lead", {})
        intelligence = task.get("intelligence", {})
        qualification = task.get("qualification", {})
        email_type = task.get("email_type", "cold")
        sender = task.get("sender_name", "Alex Chen")
        sender_title = task.get("sender_title", "Account Executive, SalesFlow CRM")
        
        self._log(f"✍️  Writing {email_type} email for {lead.get('full_name')} at {lead.get('company')}")
        
        # Get personalization hooks from research
        hooks = []
        if intelligence:
            hooks = intelligence.get("personalization_hooks", [])
        
        pain_points = []
        if intelligence:
            pain_points = intelligence.get("pain_points", {}).get("secondary_pains", [])
        
        primary_pain = intelligence.get("pain_points", {}).get("primary_pain", "scaling sales efficiently") if intelligence else "scaling sales efficiently"
        
        email_types_context = {
            "cold": "First ever contact. Must stand out in a crowded inbox. Reference a specific insight about their company.",
            "followup1": "Second touch. Add new value — share a relevant insight or mini-case study. Reference their specific industry.",
            "followup2": "Third touch. Create urgency. Mention limited availability or expiring offer. Keep it short.",
            "followup3": "Fourth touch. Go different angle — ask a genuine question about their challenges.",
            "breakup": "Final email. Breakup email that is genuinely respectful and leaves door open. Short and human."
        }
        
        prompt = f"""Write a {email_type} sales email for this specific prospect.

PROSPECT:
- Name: {lead.get('full_name', 'there')} (First name: {lead.get('full_name', '').split()[0] if lead.get('full_name') else 'there'})
- Company: {lead.get('company')}
- Role: {lead.get('role', lead.get('contact_role', 'Sales Leader'))}
- Industry: {lead.get('industry')}
- Primary Pain: {primary_pain}

PERSONALIZATION HOOKS:
{chr(10).join(f'- {h}' for h in hooks[:3])}

QUALIFICATION CONTEXT:
- Lead Temperature: {qualification.get('lead_temperature', 'Warm') if qualification else 'Warm'}
- Deal Probability: {qualification.get('deal_probability', 50) if qualification else 50}%
- Best Talking Points: {', '.join(qualification.get('talking_points', [])[:2]) if qualification else 'AI automation, revenue growth'}

EMAIL TYPE CONTEXT: {email_types_context.get(email_type, email_types_context['cold'])}

SENDER: {sender}, {sender_title}

OUR PRODUCT: SalesFlow CRM — AI-Powered Sales Automation
Key benefits: 3x lead conversion, 80% less manual work, real-time AI coaching, instant ROI

Write the email and return JSON:
{{
  "subject_line_a": "Primary subject line (max 50 chars, create curiosity)",
  "subject_line_b": "A/B variant subject line (different angle)",
  "email_body": "Full email body in HTML (concise, warm, human, one CTA)",
  "plain_text_version": "Plain text version (150-200 words max)",
  "linkedin_message": "Companion LinkedIn connection message (300 chars max)",
  "cta": "The specific call-to-action used",
  "personalization_used": "Which specific hook you used"
}}"""
        
        try:
            response = self.think(prompt, temperature=0.7)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0:
                email_data = json.loads(response[json_start:json_end])
            else:
                raise ValueError("No JSON in response")
        except Exception as e:
            self._log(f"❌ Email generation failed: {e}")
            raise RuntimeError("Email generation failed; no template response was substituted.") from e
        
        self._log("✅ AI email draft generated")
        
        return {
            "agent": self.name,
            "status": "success",
            "email_type": email_type,
            "recipient": lead.get("email"),
            "email": email_data,
            "written_at": __import__('datetime').datetime.now().isoformat()
        }
    
