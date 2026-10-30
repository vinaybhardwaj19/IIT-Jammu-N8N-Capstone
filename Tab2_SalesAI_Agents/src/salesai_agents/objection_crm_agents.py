"""
Objection Handler Agent
========================
Real-time sales objection detection and rebuttal engine.
Powers the ChatGPT-style conversational interface.
"""

import json

try:
    from .base import BaseAgent
except (ImportError, ValueError):
    try:
        from salesai_agents.base import BaseAgent
    except ImportError:
        from base import BaseAgent


class ObjectionHandlerAgent(BaseAgent):
    """
    Agent 4: ObjectionHandlerAgent
    
    Capabilities:
    - Real-time objection classification
    - Evidence-backed rebuttal generation
    - Conversational AI chat interface (like ChatGPT)
    - Role-play mode for sales training
    - Multi-turn conversation context awareness
    """
    
    COMMON_OBJECTIONS = {
        "price": ["too expensive", "can't afford", "budget", "cost", "price", "costly", "cheap"],
        "timing": ["not now", "bad timing", "later", "next quarter", "next year", "busy"],
        "competitor": ["already use", "have a crm", "salesforce", "hubspot", "competitor"],
        "trust": ["new company", "never heard", "results", "prove it", "guarantee"],
        "need": ["don't need", "doing fine", "working well", "happy with current"],
        "authority": ["not my decision", "need to ask", "boss", "committee", "board"],
        "information": ["send more info", "email me", "share details", "information"]
    }
    
    def __init__(self):
        super().__init__(
            name="ObjectionHandlerAgent",
            role="Sales Conversation Coach & Objection Handler",
            system_prompt="""You are a world-class sales trainer and conversation coach with 20+ years of experience.
You respond to sales objections using proven techniques:
- Feel/Felt/Found method for emotional objections
- Boomerang technique to turn objections into reasons to buy
- Clarifying questions to uncover the real concern
- Social proof and case studies for trust objections
- ROI calculations for price objections

IMPORTANT: You are a conversational AI assistant helping sales reps handle objections in real-time.
Your responses are:
- Empathetic and understanding (never defensive or pushy)
- Backed by specific data and social proof
- Concise (speak normally, not walls of text)
- Followed by a soft, open-ended question to re-engage
- Always professional and respectful

You also help users understand the SalesFlow CRM product features, pricing, and capabilities.
Act like a helpful ChatGPT assistant — conversational, friendly, knowledgeable."""
        )
        
        self.conversation_mode = "chat"  # "chat" or "roleplay"
        self.roleplay_persona = "prospect"
    
    def run(self, task: dict) -> dict:
        """
        Handle a sales objection or general sales question.
        
        Args:
            task: {
                "message": str - the prospect's objection or question
                "lead_context": dict - lead data for personalization
                "conversation_history": list - prior messages
                "mode": "handle_objection" or "chat" or "roleplay"
            }
        
        Returns:
            dict: AI response with rebuttal/answer and strategy notes
        """
        message = task.get("message", "")
        lead_context = task.get("lead_context", {})
        mode = task.get("mode", "chat")
        
        # Detect objection type
        objection_type = self._classify_objection(message)
        
        if mode == "chat":
            return self._handle_chat(message, lead_context, objection_type)
        elif mode == "handle_objection":
            return self._handle_objection(message, lead_context, objection_type)
        elif mode == "roleplay":
            return self._roleplay_mode(message)
        else:
            return self._handle_chat(message, lead_context, objection_type)
    
    def _classify_objection(self, message: str) -> str:
        """Classify the type of objection."""
        message_lower = message.lower()
        for obj_type, keywords in self.COMMON_OBJECTIONS.items():
            if any(keyword in message_lower for keyword in keywords):
                return obj_type
        return "general"
    
    def _handle_chat(self, message: str, lead_context: dict, objection_type: str) -> dict:
        """Handle conversational chat mode — like ChatGPT for sales."""
        company = lead_context.get("company", "your company")
        name = lead_context.get("first_name", "")
        
        context_note = f"You're helping a sales rep who is talking to {name} from {company}." if company != "your company" else ""
        
        prompt = f"""{context_note}

User message: "{message}"

Objection type detected: {objection_type}

Respond naturally and helpfully. If this is a sales objection, use proven sales techniques to address it empathetically and professionally. If it's a general question about SalesFlow CRM or sales strategy, answer it knowledgeably.

Provide:
1. Your conversational response (what to say to the prospect)
2. The technique you used
3. A follow-up question to keep them engaged"""
        
        response_text = self.think(prompt, temperature=0.6)
        
        return {
            "agent": self.name,
            "mode": "chat",
            "objection_type": objection_type,
            "response": response_text,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    
    def _handle_objection(self, message: str, lead_context: dict, objection_type: str) -> dict:
        """Structured objection handling with full strategy."""
        company = lead_context.get("company", "their company")
        industry = lead_context.get("industry", "their industry")
        
        objection_strategies = {
            "price": "ROI calculation + payment flexibility + cost of NOT solving the problem",
            "timing": "Future pacing + competitive urgency + pilot/trial option",
            "competitor": "Competitive differentiation + switching cost analysis + demo comparison",
            "trust": "Social proof + case studies + free trial + references",
            "need": "Discovery questions + pain amplification + future vision",
            "authority": "Map the buying committee + provide resources for internal champion",
            "information": "Qualify intent + offer a call instead + send targeted content"
        }
        
        prompt = f"""Handle this sales objection professionally and effectively.

OBJECTION: "{message}"
OBJECTION TYPE: {objection_type}
RECOMMENDED STRATEGY: {objection_strategies.get(objection_type, 'active listening and clarification')}

PROSPECT CONTEXT:
- Company: {company}
- Industry: {industry}

Provide a complete objection handling playbook as JSON:
{{
  "objection_type": "{objection_type}",
  "reframe": "One-sentence reframe of the objection as an opportunity",
  "immediate_response": "What to say RIGHT NOW (2-3 sentences, empathetic, non-defensive)",
  "technique_used": "Name of the technique applied",
  "supporting_data": "Specific stat or social proof to use",
  "follow_up_question": "An open-ended question to re-engage",
  "if_they_push_back": "What to say if they double down on the objection",
  "red_flags": "Signs this lead may not be qualified despite the objection"
}}"""
        
        try:
            response = self.think(prompt)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0:
                objection_data = json.loads(response[json_start:json_end])
            else:
                raise ValueError("No JSON")
        except Exception as exc:
            raise RuntimeError("Objection handling failed; no canned rebuttal was substituted.") from exc
        
        return {
            "agent": self.name,
            "mode": "handle_objection",
            "original_objection": message,
            "objection_data": objection_data,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    
    def _roleplay_mode(self, message: str) -> dict:
        """Sales training roleplay — AI acts as a difficult prospect."""
        prompt = f"""You are playing the role of a DIFFICULT B2B prospect during a sales call.
The sales rep just said: "{message}"

Respond as a skeptical, busy VP of Sales who:
- Is happy with their current CRM (Salesforce)
- Is concerned about cost and migration effort
- Values their time and hates salesy pitches
- But IS open to seeing genuine value

Return JSON with a realistic prospect response that challenges the sales rep and a brief coaching tip based only on this exchange:
{{"prospect_response":"...","coaching_tip":"..."}}"""
        
        response = self.think(prompt, temperature=0.8)
        try:
            json_start, json_end = response.find("{"), response.rfind("}") + 1
            roleplay = json.loads(response[json_start:json_end])
        except Exception as exc:
            raise RuntimeError("Roleplay response was not valid JSON; no scripted prospect was substituted.") from exc
        
        return {
            "agent": self.name,
            "mode": "roleplay",
            "persona": "AI-generated prospect for this roleplay",
            "prospect_response": roleplay.get("prospect_response", ""),
            "coaching_tip": roleplay.get("coaching_tip", ""),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
