"""
SalesAI SDR — Main Orchestrator
================================
The central brain that coordinates all 6 AI agents.
Runs the complete SDR pipeline and provides the ChatGPT-style
interactive chat interface.

Usage:
  python main.py              → Interactive chat mode
  python main.py --demo       → Full demo with sample lead
  python main.py --pipeline   → Run complete SDR pipeline
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Fix Windows terminal encoding (handles emoji/Unicode)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from salesai_agents.prospect_research_agent import ProspectResearchAgent
from salesai_agents.lead_qualification_agent import LeadQualificationAgent
from salesai_agents.email_writer_agent import EmailWriterAgent
from salesai_agents.objection_crm_agents import ObjectionHandlerAgent
from salesai_agents.crm_manager_agent import CRMManagerAgent
from salesai_agents.meeting_coordinator_agent import MeetingCoordinatorAgent

OPENAI_AGENT_MODEL = os.getenv("OPENAI_AGENT_MODEL", "gpt-4.1-mini")


# ============================================================
# COLOR TERMINAL OUTPUT
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def cprint(text, color=Colors.END):
    print(f"{color}{text}{Colors.END}")

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║          🚀 SalesAI SDR — Multi-Agent Sales Automation          ║
║          IIT Summer School '26 | OpenAI Agents SDK Capstone     ║
╠══════════════════════════════════════════════════════════════════╣
║  Agents: Research → Qualify → Write → Handle → Manage → Close  ║
║  Agents SDK: {OPENAI_AGENT_MODEL:<51}║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}"""
    print(banner)

def print_section(title: str):
    cprint(f"\n{'='*65}", Colors.BLUE)
    cprint(f"  {title}", Colors.BOLD)
    cprint(f"{'='*65}", Colors.BLUE)


# ============================================================
# ORCHESTRATOR CLASS
# ============================================================

class SalesAIOrchestrator:
    """
    The master orchestrator that runs all agents in sequence.
    Like an AI-powered SDR team that never sleeps.
    """
    
    def __init__(self):
        cprint("🤖 Initializing SalesAI SDR Agents...", Colors.CYAN)
        
        self.research_agent = ProspectResearchAgent()
        self.qualification_agent = LeadQualificationAgent()
        self.email_agent = EmailWriterAgent()
        self.objection_agent = ObjectionHandlerAgent()
        self.crm_agent = CRMManagerAgent()
        self.meeting_agent = MeetingCoordinatorAgent()
        
        cprint("✅ All 6 agents initialized successfully!\n", Colors.GREEN)
        
        self.session_results = []
    
    def run_full_pipeline(self, lead: dict) -> dict:
        """
        Run the complete SDR pipeline for a single lead.
        
        Pipeline: Research → Qualify → Write Email → Coordinate Meeting → Log to CRM
        """
        print_section(f"🎯 RUNNING FULL SDR PIPELINE FOR: {lead.get('full_name')} @ {lead.get('company')}")
        
        results = {"lead": lead, "pipeline_start": datetime.now().isoformat()}
        
        # ── Step 1: Research ──────────────────────────────────────
        print_section("STEP 1/5: 🔍 Prospect Research Agent")
        research_result = self.research_agent.run({
            "company_name": lead.get("company"),
            "contact_name": lead.get("full_name"),
            "contact_role": lead.get("role"),
            "industry": lead.get("industry"),
            "website": lead.get("website", "")
        })
        results["research"] = research_result
        
        intelligence = research_result.get("intelligence", {})
        cprint(f"\n  📊 Key Finding: {intelligence.get('pain_points', {}).get('primary_pain', 'Researched')}", Colors.YELLOW)
        cprint(f"  💡 Best Hook: {intelligence.get('personalization_hooks', [''])[0]}", Colors.YELLOW)
        
        # ── Step 2: Qualify ───────────────────────────────────────
        print_section("STEP 2/5: 🎯 Lead Qualification Agent")
        qual_result = self.qualification_agent.run({
            "lead": lead,
            "intelligence": intelligence
        })
        results["qualification"] = qual_result
        
        qual = qual_result.get("qualification", {})
        score = qual.get("composite_score", 0)
        status = qual.get("qualification_status", "UNKNOWN")
        temp = qual.get("lead_temperature", "Unknown")
        
        color = Colors.GREEN if score >= 70 else Colors.YELLOW if score >= 50 else Colors.RED
        cprint(f"\n  📈 BANT Score: {score}/100", color)
        cprint(f"  🌡️  Temperature: {temp} | Status: {status}", color)
        cprint(f"  💰 Deal Size: {qual.get('estimated_deal_size', 'Unknown')}", Colors.YELLOW)
        
        # ── Step 3: Write Email ───────────────────────────────────
        print_section("STEP 3/5: ✍️  Email Writer Agent")
        email_result = self.email_agent.run({
            "lead": lead,
            "intelligence": intelligence,
            "qualification": qual,
            "email_type": "cold",
            "sender_name": "Vinay Bhardwaj",
            "sender_title": "Account Executive, SalesFlow CRM"
        })
        results["email"] = email_result
        
        email = email_result.get("email", {})
        cprint(f"\n  📧 Subject A: {email.get('subject_line_a', 'N/A')}", Colors.CYAN)
        cprint(f"  📧 Subject B: {email.get('subject_line_b', 'N/A')}", Colors.CYAN)
        cprint(f"  📊 Est. Reply Rate: {email.get('estimated_reply_rate', 'N/A')}", Colors.YELLOW)
        
        # ── Step 4: Meeting Coordination ──────────────────────────
        print_section("STEP 4/5: 📅 Meeting Coordinator Agent")
        meeting_result = self.meeting_agent.run({
            "action": "schedule",
            "lead": lead,
            "intelligence": intelligence,
            "qualification": qual,
            "meeting_type": "discovery"
        })
        results["meeting"] = meeting_result
        meeting_package = meeting_result.get("meeting_package", {})
        proposed_times = meeting_result.get("suggested_times", [])
        cprint(f"  ✉️  Invite Draft: {meeting_package.get('meeting_invite_subject', 'Prepared for review')}", Colors.CYAN)
        cprint(f"\n  📅 Proposed Time: {proposed_times[0] if proposed_times else 'Ask the prospect for suitable times'}", Colors.CYAN)
        cprint(f"  🔗 Booking Link: {meeting_result.get('booking_link') or 'No calendar booking provider configured'}", Colors.CYAN)

        # ── Step 5: Log to CRM ────────────────────────────────────
        print_section("STEP 5/5: 📋 CRM Manager Agent")
        crm_result = self.crm_agent.run({
            "action": "log_lead",
            "data": {
                **lead,
                **qual,
                "lead_id": lead.get("lead_id", f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                "pipeline_stage": "Qualified - Meeting Proposed",
                "email_drafted": True,
                "meeting_proposed": True
            }
        })
        results["crm"] = crm_result
        cprint(f"\n  ✅ Lead logged to CRM: {crm_result.get('lead_id')}", Colors.GREEN)
        
        # ── Summary ───────────────────────────────────────────────
        results["pipeline_end"] = datetime.now().isoformat()
        
        print_section("📊 PIPELINE COMPLETE — SUMMARY")
        print(f"""
  Lead:         {lead.get('full_name')} ({lead.get('company')})
  Score:        {score}/100 ({temp})
  Status:       {status}
  Deal Size:    {qual.get('estimated_deal_size', 'Unknown')}
  Win Prob:     {qual.get('deal_probability', 0)}%
  Next Action:  {qual.get('recommended_next_steps', ['Send email'])[0]}
  Email Ready:  ✅ (Subject: {email.get('subject_line_a', 'N/A')[:40]}...)
  CRM ID:       {crm_result.get('lead_id')}
        """)
        
        self.session_results.append(results)
        return results
    
    def interactive_chat(self):
        """
        ChatGPT-style conversational interface.
        Powered by the ObjectionHandlerAgent.
        """
        print_section("💬 INTERACTIVE CHAT MODE — SalesAI Assistant")
        cprint("""
  I can help you with:
  • Handle sales objections (type the objection you're getting)
  • Write emails (say "write email for [company]")
  • Qualify a lead (say "qualify [company name]")
  • Sales strategy advice
  • Product questions about SalesFlow CRM
  • Practice with roleplay mode (say "roleplay")
  
  Type 'exit' or 'quit' to stop.
        """, Colors.CYAN)
        
        lead_context = {}
        mode = "chat"
        
        while True:
            try:
                user_input = input(f"\n{Colors.BOLD}You: {Colors.END}").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    cprint("\n👋 Thanks for using SalesAI SDR! Good selling! 🚀", Colors.GREEN)
                    break
                
                # Mode detection
                if "roleplay" in user_input.lower():
                    mode = "roleplay"
                    cprint("\n🎭 Roleplay mode activated! I'll act as a difficult prospect.", Colors.YELLOW)
                    cprint("   Try to pitch SalesFlow CRM to me. I'm a skeptical VP of Sales.\n", Colors.YELLOW)
                
                elif "chat mode" in user_input.lower() or "normal mode" in user_input.lower():
                    mode = "chat"
                    cprint("\n💬 Switched back to chat mode!", Colors.GREEN)
                
                # Run through objection handler
                result = self.objection_agent.run({
                    "message": user_input,
                    "lead_context": lead_context,
                    "mode": mode
                })
                
                # Display response
                cprint(f"\n{Colors.BOLD}SalesAI: {Colors.END}", end="")
                
                if mode == "roleplay":
                    print(result.get("prospect_response", ""))
                    cprint(f"\n  [Coach Tip: {result.get('coaching_tip', '')}]", Colors.YELLOW)
                else:
                    print(result.get("response", "I'm here to help! What sales challenge are you facing?"))
                
            except KeyboardInterrupt:
                cprint("\n\n👋 Session interrupted. Goodbye!", Colors.YELLOW)
                break
            except Exception as e:
                cprint(f"\n⚠️  Error: {e}. Please try again.", Colors.RED)


# ============================================================
# DEMO MODE
# ============================================================

DEMO_LEADS = [
    {
        "lead_id": "LEAD-2026-001",
        "full_name": "Priya Sharma",
        "role": "VP of Sales",
        "email": "priya.sharma@techvision.io",
        "phone": "+91-98765-43210",
        "company": "TechVision Solutions",
        "industry": "B2B SaaS",
        "website": "techvision.io",
        "budget": "$2,000-5,000/month",
        "source": "LinkedIn",
        "notes": "Company raised Series A of $8M recently. Team of 25 sales reps."
    },
    {
        "lead_id": "LEAD-2026-002",
        "full_name": "Rahul Gupta",
        "role": "Co-Founder & CEO",
        "email": "rahul@finedge.co",
        "phone": "+91-99123-45678",
        "company": "FinEdge Capital",
        "industry": "Fintech",
        "website": "finedge.co",
        "budget": "$1,000-2,000/month",
        "source": "Website",
        "notes": "Fintech startup, 15 person team, struggling with manual lead tracking."
    }
]


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="SalesAI SDR Multi-Agent System")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample leads")
    parser.add_argument("--pipeline", action="store_true", help="Run full pipeline")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat")
    args = parser.parse_args()
    
    print_banner()
    
    orchestrator = SalesAIOrchestrator()
    
    if args.demo or (not args.pipeline and not args.chat):
        # Default: run demo with first sample lead then open chat
        cprint("🎯 Running DEMO mode with sample leads...\n", Colors.CYAN)
        
        # Process first demo lead
        orchestrator.run_full_pipeline(DEMO_LEADS[0])
        
        # Ask if they want to continue
        cprint("\n" + "="*65, Colors.BLUE)
        cprint("  Demo complete! Starting interactive chat mode...", Colors.BOLD)
        cprint("="*65 + "\n", Colors.BLUE)
        
        orchestrator.interactive_chat()
    
    elif args.pipeline:
        cprint("📊 Running full pipeline for all demo leads...\n", Colors.CYAN)
        for lead in DEMO_LEADS:
            orchestrator.run_full_pipeline(lead)
            print("\n")
    
    elif args.chat:
        orchestrator.interactive_chat()


if __name__ == "__main__":
    main()
