"""
SalesAI SDR — Launcher Script
================================
Run this to start the system.
Choose mode: Gradio UI, FastAPI backend, or both.

Usage:
  python launch.py                 → Start Gradio UI (default)
  python launch.py --api           → Start FastAPI only
  python launch.py --both          → Start Gradio + FastAPI
  python launch.py --cli           → Terminal mode (original)
  python launch.py --test          → Quick system test
"""

import os
import sys
import argparse
import subprocess
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
except ImportError:
    pass
sys.path.insert(0, os.path.join(ROOT, 'Tab2_SalesAI_Agents'))
sys.path.insert(0, os.path.join(ROOT, 'Tab2_SalesAI_Agents', 'src'))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

COLORS = {
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "bold":   "\033[1m",
    "end":    "\033[0m"
}
def c(text, color="end"): return f"{COLORS.get(color, '')}{text}{COLORS['end']}"


def print_banner():
    print(f"""
{COLORS['cyan']}{COLORS['bold']}
╔══════════════════════════════════════════════════════════════════╗
║        🚀 SalesAI SDR v2.0 — Real Integration Edition           ║
║        IIT Jammu Summer School '26 | Vinay Bhardwaj             ║
╠══════════════════════════════════════════════════════════════════╣
║  NEW: Gradio UI • FastAPI • SQLite CRM • Real Web Research      ║
║       SMTP Email • Meeting Coordinator • N8N Webhooks            ║
╚══════════════════════════════════════════════════════════════════╝
{COLORS['end']}""")


def run_quick_test():
    """Quick system test to verify all components work."""
    print(c("\n🧪 Running Quick System Test...\n", "cyan"))
    
    errors = []
    
    # Test 1: DB
    try:
        from tools.crm_database import init_database, get_pipeline_stats
        init_database()
        stats = get_pipeline_stats()
        print(c(f"  ✅ SQLite CRM Database — OK (leads: {stats.get('total_leads', 0)})", "green"))
    except Exception as e:
        print(c(f"  ❌ Database — FAIL: {e}", "red"))
        errors.append("database")

    # Test 2: AI
    try:
        from salesai_agents.base import call_ai, AI_PROVIDER
        response = call_ai("Say 'SALESAI OK' in exactly 3 words.", temperature=0.1)
        print(c(f"  ✅ AI Provider ({AI_PROVIDER.upper()}) — OK: {response[:50]}", "green"))
    except Exception as e:
        print(c(f"  ❌ AI Provider — FAIL: {e}", "red"))
        errors.append("ai")

    # Test 3: Agents
    try:
        from salesai_agents.prospect_research_agent import ProspectResearchAgent
        from salesai_agents.lead_qualification_agent import LeadQualificationAgent
        from salesai_agents.email_writer_agent import EmailWriterAgent
        from salesai_agents.objection_crm_agents import ObjectionHandlerAgent
        from salesai_agents.crm_manager_agent import CRMManagerAgent
        from salesai_agents.meeting_coordinator_agent import MeetingCoordinatorAgent
        agents = [ProspectResearchAgent, LeadQualificationAgent, EmailWriterAgent,
                  ObjectionHandlerAgent, CRMManagerAgent, MeetingCoordinatorAgent]
        for AgentClass in agents:
            a = AgentClass()
            print(c(f"  ✅ {a.name} — OK", "green"))
    except Exception as e:
        print(c(f"  ❌ Agents — FAIL: {e}", "red"))
        errors.append("agents")

    # Test 4: Web Research
    try:
        from tools.web_research import search_duckduckgo
        results = search_duckduckgo("Salesforce CRM")
        print(c(f"  ✅ Web Research (DuckDuckGo) — OK ({len(results)} results)", "green"))
    except Exception as e:
        print(c(f"  ⚠️  Web Research — {e} (optional)", "yellow"))

    # Test 5: Email
    try:
        from tools.email_sender import get_smtp_status
        smtp = get_smtp_status()
        print(c(f"  {'✅' if smtp['configured'] else '⚠️ '} SMTP Email — {smtp['status']}", "green" if smtp['configured'] else "yellow"))
    except Exception as e:
        print(c(f"  ❌ Email — FAIL: {e}", "red"))
        errors.append("email")

    # Test 6: Gradio
    try:
        import gradio
        print(c(f"  ✅ Gradio {gradio.__version__} — OK", "green"))
    except Exception as e:
        print(c(f"  ❌ Gradio — FAIL: pip install gradio", "red"))
        errors.append("gradio")

    # Test 7: FastAPI
    try:
        import fastapi, uvicorn
        print(c(f"  ✅ FastAPI + Uvicorn — OK", "green"))
    except Exception as e:
        print(c(f"  ❌ FastAPI — FAIL: pip install fastapi uvicorn", "red"))
        errors.append("fastapi")

    if errors:
        print(c(f"\n⚠️  {len(errors)} issues found: {', '.join(errors)}", "yellow"))
        print(c("   Run: pip install -r Tab2_SalesAI_Agents/requirements.txt", "yellow"))
    else:
        print(c("\n🎉 All systems operational! Ready to launch.", "green"))
    
    return len(errors) == 0


def start_gradio(port: int = 7860, share: bool = False):
    """Launch the Gradio dashboard."""
    print(c(f"\n🌐 Starting Gradio Dashboard on http://localhost:{port}", "cyan"))
    if share:
        print(c("🌍 Generating public link for external evaluation...", "yellow"))
    os.environ.setdefault("GRADIO_PORT", str(port))
    
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'Tab2_SalesAI_Agents', 'src'))
    
    from gradio_app import build_gradio_app, THEME, CSS
    app = build_gradio_app()
    app.queue(default_concurrency_limit=20, max_size=2000)
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        theme=THEME,
        css=CSS,
        share=share,
        show_error=True,
        inbrowser=True
    )


def start_api(port: int = 8000):
    """Launch the FastAPI backend."""
    print(c(f"\n⚡ Starting FastAPI Backend on http://localhost:{port}", "cyan"))
    print(c(f"   Docs: http://localhost:{port}/docs", "cyan"))
    print(c(f"   N8N Webhook: http://localhost:{port}/webhook/n8n", "cyan"))
    
    import uvicorn
    # Import app from api_server
    sys.path.insert(0, ROOT)
    from api_server import app
    uvicorn.run(app, host="0.0.0.0", port=port)


def start_both(gradio_port=7860, api_port=8000, share: bool = False):
    """Start both Gradio and FastAPI concurrently."""
    api_thread = threading.Thread(target=start_api, args=(api_port,), daemon=True)
    api_thread.start()
    time.sleep(2)
    start_gradio(gradio_port, share=share)


def main():
    parser = argparse.ArgumentParser(description="SalesAI SDR v2.0 Launcher")
    parser.add_argument("--api",    action="store_true", help="Start FastAPI backend only")
    parser.add_argument("--both",   action="store_true", help="Start Gradio + FastAPI")
    parser.add_argument("--cli",    action="store_true", help="Terminal CLI mode")
    parser.add_argument("--test",   action="store_true", help="Run system test")
    parser.add_argument("--share",  action="store_true", help="Generate public URL (gradio.live) for external evaluation")
    parser.add_argument("--public", action="store_true", dest="share", help="Alias for --share")
    parser.add_argument("--gradio-port", type=int, default=7860)
    parser.add_argument("--api-port",    type=int, default=8000)
    args = parser.parse_args()

    print_banner()

    if args.test:
        raise SystemExit(0 if run_quick_test() else 1)

    if args.api:
        start_api(args.api_port)
    elif args.both:
        start_both(args.gradio_port, args.api_port, share=args.share)
    elif args.cli:
        # Fall through to original CLI
        os.chdir(os.path.join(ROOT, 'Tab2_SalesAI_Agents'))
        subprocess.run([sys.executable, "main.py"])
    else:
        # Default: Gradio UI
        print(c("\n📋 Startup Tips:", "yellow"))
        print(c("  • python launch.py          → Gradio UI at http://localhost:7860", "yellow"))
        print(c("  • python launch.py --share  → 🌍 Generate PUBLIC URL for IIT evaluators", "yellow"))
        print(c("  • python launch.py --both   → Gradio + FastAPI running simultaneously", "yellow"))
        print(c("  • python launch.py --test   → Quick system health check\n", "yellow"))
        start_gradio(args.gradio_port, share=args.share)


if __name__ == "__main__":
    main()
