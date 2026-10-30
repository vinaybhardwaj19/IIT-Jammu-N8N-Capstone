"""
Generate Full Submission-Ready Internship Report PDF
IIT Jammu Summer School 2026 — Vinay Bhardwaj
"""
import os, sys, base64
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SHOTS = r"C:\Users\HP\Downloads\IIT PROJECT 1\report_screenshots"
OUT   = r"C:\Users\HP\Downloads\Vinay_Bhardwaj_IIT_Jammu_Final_Report.pdf"

def b64(fn):
    p = os.path.join(SHOTS, fn)
    if not os.path.exists(p): return None
    m = "jpeg" if fn.lower().endswith((".jpg","jpeg")) else "png"
    return "data:image/{};base64,{}".format(m, base64.b64encode(open(p,"rb").read()).decode())

def img(fn, cap="", side=""):
    d = b64(fn)
    s = side or "width:100%;border-radius:8px;margin:8px 0 4px;box-shadow:0 3px 16px rgba(0,0,0,.25);"
    if not d:
        return f'<div style="border:2px dashed #888;padding:16px;text-align:center;color:#aaa;border-radius:8px">[{fn}]</div>'
    return f'<img src="{d}" style="{s}" alt="{cap}"/>'

cert  = img("iit_jammu_certificate_1787597295767.jpg",  "IIT Certificate")
bon   = img("gndec_bonafide_letter_1787597312076.jpg",  "GNDEC Bonafide")
f21   = img("Fig_2_1_IIT_Capstone_Showcase_Hero.png")
f22   = img("Fig_2_2_FullStack_Architecture_and_Ecosystem.png")
f23   = img("Fig_2_3_Dual_Project_Comparison_Matrix.png")
f31   = img("Fig_3_1_SalesFlow_AI_Full_Architecture.png")
f32   = img("Fig_3_2_n8n_Lead_Ingestion_and_Routing_Workflows.png")
f33   = img("Fig_3_3_n8n_HITL_Proposals_and_Sentiment_Followup.png")
f34   = img("Fig_3_4_n8n_Calendar_Prep_and_Executive_Analytics.png")
f35   = img("Fig_3_5_Relational_PostgreSQL_Schema_Architecture.png")
f36   = img("Fig_3_6_Business_Impact_and_Performance_Metrics.png")
f41   = img("Fig_4_1_SalesAI_SDR_Interactive_Studio_Dashboard.png")
f42   = img("Fig_4_2_BANT_Qualification_Scorecard_and_Deal_Estimate.png")
f43   = img("Fig_4_3_RealTime_Agent_Execution_Trace_Validation.png")
f44   = img("Fig_4_4_Multi_Tone_Personalized_Cold_Email_Suite.png")
f45   = img("Fig_4_5_Meeting_Strategy_and_Discovery_Slots.png")
f46   = img("Fig_4_6_Prospect_Research_and_Tech_Stack_Intel.png")
f47   = img("Fig_4_7_SQLite_CRM_State_Engine_and_Audit_Logs.png")
f51   = img("Fig_5_1_Master_Evaluation_Scorecard_Portal.png")
f52   = img("Fig_5_2_Evaluation_Matrix_and_Module_Health.png")
f53   = img("Fig_5_3_Code_Quality_and_Verification_Suite.png")
f54   = img("Fig_5_4_Terminal_Automated_Boundary_Verification.png")
f55   = img("Fig_5_5_Extreme_Stress_Test_Zero_Errors.png")
r1    = img("Real_Fig_1_VSCode_IDE_SalesAI_SDR.png")
r2    = img("Real_Fig_2_n8n_Canvas_Lead_Ingestion.png")
r3    = img("Real_Fig_3_n8n_Canvas_RoundRobin_Assignment.png")
r4    = img("Real_Fig_4_GoogleSheets_CRM_Pipeline.png")
r5    = img("Real_Fig_5_Gmail_Personalized_Outreach.png")
r6    = img("Real_Fig_6_Slack_HITL_Approval_Alert.png")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',Arial,sans-serif;color:#0f172a;font-size:10.5pt;line-height:1.7;background:#fff}
.pb{page-break-before:always;break-before:page}
.nb{page-break-inside:avoid;break-inside:avoid}
.cover{min-height:100vh;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 40px;color:#fff}
.cbadge{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:40px;padding:8px 24px;font-size:10pt;font-weight:600;margin-bottom:28px}
.cover h1{font-size:30pt;font-weight:900;line-height:1.15;margin-bottom:14px;background:linear-gradient(135deg,#a78bfa,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.csub{font-size:12pt;color:rgba(255,255,255,.75);margin-bottom:36px;max-width:580px}
.cdiv{width:80px;height:3px;background:linear-gradient(90deg,#a78bfa,#60a5fa);border-radius:2px;margin:0 auto 32px}
.cinfo{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:14px;padding:24px 44px;margin-bottom:32px}
.cinfo table{width:100%;border-collapse:collapse}
.cinfo td{padding:6px 14px;text-align:left}
.cinfo td:first-child{color:rgba(255,255,255,.5);font-size:9pt;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
.cinfo td:last-child{color:#fff;font-weight:600;font-size:10pt}
.cfooter{color:rgba(255,255,255,.38);font-size:8.5pt;margin-top:20px}
.ph{background:linear-gradient(90deg,#4f46e5,#0ea5e9);color:#fff;padding:9px 44px;font-size:8pt;font-weight:600;display:flex;justify-content:space-between}
.wrap{padding:0 44px 36px;max-width:920px;margin:0 auto}
.sh{border-left:5px solid #4f46e5;padding:18px 22px;margin:28px 0 18px;background:#eef2ff;border-radius:0 8px 8px 0}
.sh .chl{font-size:8pt;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#4f46e5;margin-bottom:3px;font-family:'JetBrains Mono',monospace}
.sh h2{font-size:15pt;font-weight:800;color:#0f172a}
h3.sub{font-size:11.5pt;font-weight:700;color:#0f172a;border-bottom:2px solid #e2e8f0;padding-bottom:5px;margin:20px 0 10px}
h4.sub2{font-size:10pt;font-weight:700;color:#4f46e5;margin:14px 0 7px}
p{margin-bottom:9px;color:#1e293b}
ul,ol{margin:7px 0 11px 22px}
li{margin-bottom:4px}
.pre{padding:0 44px;max-width:920px;margin:0 auto}
.pt{font-size:17pt;font-weight:800;color:#0f172a;border-bottom:3px solid #4f46e5;padding-bottom:8px;margin-bottom:20px}
.decbox{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:22px 26px;margin:16px 0}
.sigline{margin-top:28px;display:flex;gap:50px}
.sigb{text-align:center}
.sigb .sl{border-top:1px solid #94a3b8;width:190px;margin:0 auto 5px;padding-top:5px}
.sigb .slb{font-size:8.5pt;color:#64748b}
table.dt{width:100%;border-collapse:collapse;margin:14px 0;font-size:9.5pt}
table.dt th{background:#4f46e5;color:#fff;padding:9px 11px;text-align:left;font-weight:700}
table.dt td{padding:8px 11px;border-bottom:1px solid #e2e8f0;vertical-align:top}
table.dt tr:nth-child(even) td{background:#f8fafc}
table.dt tr:last-child td{font-weight:700;background:#e0e7ff}
.krow{display:flex;gap:10px;margin:14px 0;flex-wrap:wrap}
.kcard{flex:1;min-width:110px;background:linear-gradient(135deg,#4f46e5,#0ea5e9);color:#fff;border-radius:9px;padding:14px;text-align:center}
.kv{font-size:18pt;font-weight:900;margin-bottom:2px}
.kl{font-size:7.5pt;opacity:.85;text-transform:uppercase;letter-spacing:.5px}
.tg{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0}
.tb{background:#eef2ff;color:#4f46e5;border:1px solid #c7d2fe;border-radius:5px;padding:3px 10px;font-size:8.5pt;font-weight:600;font-family:'JetBrains Mono',monospace}
.cb{border-left:4px solid #059669;background:#ecfdf5;padding:12px 16px;border-radius:0 7px 7px 0;margin:12px 0}
.ci{border-left:4px solid #0ea5e9;background:#f0f9ff}
.fc{text-align:center;font-size:8.5pt;color:#64748b;font-style:italic;margin:3px 0 14px;padding:0 16px}
.fl{font-weight:700;color:#4f46e5;font-style:normal}
.ag{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0}
.ac{flex:1;min-width:170px;border:1px solid #e2e8f0;border-radius:9px;padding:12px;background:#f8fafc}
.an{font-weight:700;color:#4f46e5;font-size:9pt;margin-bottom:3px}
.ad{font-size:8pt;color:#64748b;line-height:1.5}
.sg{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
.sc{border:1px solid #e2e8f0;border-radius:9px;padding:12px;background:#f8fafc}
.sc h4{font-size:9.5pt;color:#4f46e5;margin-bottom:7px;font-weight:700}
.sc ul{margin-left:14px}
.sc li{font-size:8.5pt;color:#334155;margin-bottom:2px}
.ri{padding:7px 0;border-bottom:1px solid #e2e8f0;font-size:9pt;line-height:1.5}
.rn{color:#4f46e5;font-weight:700;font-family:'JetBrains Mono',monospace}
.toc .ti{display:flex;justify-content:space-between;align-items:baseline;padding:7px 0;border-bottom:1px dotted #e2e8f0}
.toc .tc{font-weight:700;color:#4f46e5;font-size:9pt;font-family:'JetBrains Mono',monospace;min-width:70px}
.toc .tt{flex:1;font-size:9.5pt;padding-left:10px}
</style>
"""

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{CSS}</head><body>

<!-- COVER -->
<div class="cover">
  <div class="cbadge">🏛️ IIT Jammu Summer School 2026 — Internship Report</div>
  <h1>SalesFlow AI &amp; SalesAI SDR</h1>
  <p class="csub">Autonomous B2B Sales Automation &amp; Multi-Agent Swarm Architecture</p>
  <div class="cdiv"></div>
  <div class="cinfo"><table>
    <tr><td>Student Name</td><td>VINAY BHARDWAJ</td></tr>
    <tr><td>URN / CRN</td><td>2435666 / 2421198</td></tr>
    <tr><td>Degree &amp; Branch</td><td>B.Tech — Information Technology (IT)</td></tr>
    <tr><td>Institution</td><td>Guru Nanak Dev Engineering College (GNDEC), Ludhiana</td></tr>
    <tr><td>Host Institution</td><td>Indian Institute of Technology (IIT) Jammu</td></tr>
    <tr><td>Programme</td><td>Summer School 2026 — AI Agents &amp; Workflow Automation</td></tr>
    <tr><td>Duration</td><td>10 June 2026 – 10 August 2026 (8 Weeks · 300 Hours)</td></tr>
  </table></div>
  <div class="cfooter">Submitted in partial fulfilment of the IIT Jammu Summer School 2026 Internship Programme</div>
</div>

<!-- CERT -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="pre">
  <div class="pt" style="margin-top:24px">Internship Completion Certificate</div>
  {cert}
  <p class="fc"><span class="fl">Figure Prelim 1.</span> Official IIT Jammu Summer School 2026 Internship Completion Certificate — Vinay Bhardwaj (URN: 2435666).</p>
</div>

<!-- BONAFIDE -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="pre" style="padding:0 44px 36px">
  <div class="pt" style="margin-top:24px">College Approval / Bonafide Certificate</div>
  {bon}
  <p class="fc"><span class="fl">Figure Prelim 2.</span> GNDEC Ludhiana — Official Bonafide / No-Objection Certificate for Summer Internship 2026.</p>
</div>

<!-- DECLARATION -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="pre" style="padding:24px 44px 36px">
  <div class="pt">Student Declaration</div>
  <div class="decbox">
    <p>I, <strong>Vinay Bhardwaj</strong> (URN: 2435666; CRN: 2421198), a student of B.Tech Information Technology at GNDEC, Ludhiana, declare that this Internship Report entitled:</p>
    <p style="text-align:center;font-style:italic;margin:14px 0;font-size:11pt;font-weight:600;color:#4f46e5">"SalesFlow AI &amp; SalesAI SDR: Autonomous B2B Sales Automation and Multi-Agent Architecture"</p>
    <p>is an authentic record of engineering work carried out by me during the IIT Jammu Summer School 2026 Internship from <strong>10 June 2026 to 10 August 2026</strong>. This work is original and has not been submitted elsewhere for any degree.</p>
    <div class="sigline">
      <div class="sigb"><div class="sl">Vinay Bhardwaj</div><div class="slb">Student Signature</div></div>
      <div class="sigb"><div class="sl">GNDEC, Ludhiana</div><div class="slb">Place</div></div>
      <div class="sigb"><div class="sl">10 August 2026</div><div class="slb">Date</div></div>
    </div>
  </div>
  <div class="pt" style="margin-top:28px;font-size:16pt">Acknowledgement</div>
  <p>I express my deepest gratitude to <strong>IIT Jammu</strong> for the opportunity to participate in Summer School 2026. I thank the mentors and faculty at IIT Jammu, and the faculty at GNDEC Ludhiana for their invaluable guidance. I acknowledge the open-source communities behind Python, n8n, FastAPI, Playwright, SQLite, Docker, and the OpenAI Agents SDK. I thank my family and peers for constant support throughout this internship.</p>

  <div class="pt" style="margin-top:28px;font-size:16pt">Abstract</div>
  <p>This report documents two enterprise-grade AI systems developed during the IIT Jammu Summer School 2026 Internship:</p>
  <ol style="margin:10px 0 10px 20px">
    <li style="margin-bottom:8px"><strong>SalesFlow AI</strong> — An n8n-based B2B sales automation engine with 6 workflow pipelines: Lead Ingestion &amp; BANT Qualification, Weighted Round-Robin Assignment, Multi-channel Sentiment Follow-up, HITL Proposal Approval, Calendar Discovery Prep, and Executive CRM Analytics.</li>
    <li style="margin-bottom:8px"><strong>SalesAI SDR</strong> — A Python multi-agent swarm with 8 AI agents using the OpenAI Agents SDK, FastAPI dashboard, Pydantic V2 validation, and SQLite CRM. Achieved 12/12 unit tests, 84/84 boundary assertions, and 22/22 stress suites at 100% pass rate.</li>
  </ol>

  <div class="pt" style="margin-top:28px;font-size:16pt">Table of Contents</div>
  <div class="toc">
    <div class="ti"><span class="tc">CH 1</span><span class="tt">Introduction</span></div>
    <div class="ti"><span class="tc">CH 2</span><span class="tt">Internship Overview &amp; Technology Stack</span></div>
    <div class="ti"><span class="tc">CH 3</span><span class="tt">Training &amp; Learning Phase</span></div>
    <div class="ti"><span class="tc">CH 4</span><span class="tt">Project 1: SalesFlow AI (n8n Workflow Engine)</span></div>
    <div class="ti"><span class="tc">CH 5</span><span class="tt">Project 2: SalesAI SDR (Multi-Agent Swarm)</span></div>
    <div class="ti"><span class="tc">CH 6</span><span class="tt">8-Week Engineering Work Log &amp; Milestones</span></div>
    <div class="ti"><span class="tc">CH 7</span><span class="tt">Testing, QA &amp; Benchmarking</span></div>
    <div class="ti"><span class="tc">CH 8</span><span class="tt">Technical Challenges &amp; Resolutions</span></div>
    <div class="ti"><span class="tc">CH 9</span><span class="tt">Skills Developed &amp; Learning Outcomes</span></div>
    <div class="ti"><span class="tc">CH 10</span><span class="tt">Conclusion &amp; Future Scope</span></div>
    <div class="ti"><span class="tc">APP</span><span class="tt">References &amp; Appendices</span></div>
  </div>
</div>

<!-- CH1 INTRODUCTION -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 1</div><h2>Introduction</h2></div>
<div class="wrap">
  <h3 class="sub">1.1 Background &amp; Industry Context</h3>
  <p>Modern B2B sales organisations manage thousands of inbound leads, outreach campaigns, CRM records, and proposal approvals simultaneously. Sales Development Representatives (SDRs) spend an estimated <strong>60–70% of their time</strong> on repetitive tasks: researching prospects, scoring leads, drafting outreach, scheduling meetings, and updating CRM pipelines — preventing focus on high-value closing activities.</p>
  <p>The emergence of <strong>Large Language Models (LLMs)</strong>, <strong>autonomous AI agent frameworks</strong>, and <strong>low-code workflow automation platforms</strong> (such as n8n) enables automation of these workflows at scale — with human-in-the-loop approval gates at critical decision points.</p>
  <h3 class="sub">1.2 Internship Objectives</h3>
  <ul>
    <li>Design and implement an n8n-based workflow engine (SalesFlow AI) managing the full B2B sales pipeline from lead intake to proposal dispatch.</li>
    <li>Design and implement a Python multi-agent swarm (SalesAI SDR) coordinating 8 specialised AI agents for end-to-end SDR task automation.</li>
    <li>Integrate REST APIs, Pydantic V2 structured validation, PostgreSQL, and SQLite relational persistence.</li>
    <li>Implement Human-in-the-Loop (HITL) safety controls for email dispatch and proposal approvals.</li>
    <li>Conduct comprehensive automated testing, adversarial stress testing, and performance benchmarking.</li>
  </ul>
  <h3 class="sub">1.3 Scope of Work</h3>
  <p>The report covers both projects as fully implemented and tested within the IIT Jammu curriculum. SalesFlow AI is documented from its six n8n workflow JSON exports and visual demos. SalesAI SDR is documented from its Python source package, automated test suite, API smoke tests, and live application screenshots.</p>
</div>

<!-- CH2 OVERVIEW -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 2</div><h2>Internship Overview &amp; Technology Stack</h2></div>
<div class="wrap">
  <h3 class="sub">2.1 Programme Details</h3>
  <table class="dt">
    <tr><th>Parameter</th><th>Detail</th></tr>
    <tr><td>Programme</td><td>IIT Jammu Summer School 2026 — AI Agents &amp; Workflow Automation</td></tr>
    <tr><td>Host Institution</td><td>Indian Institute of Technology (IIT) Jammu</td></tr>
    <tr><td>Student Institution</td><td>Guru Nanak Dev Engineering College (GNDEC), Ludhiana</td></tr>
    <tr><td>Duration</td><td>10 June 2026 – 10 August 2026 (8 Weeks)</td></tr>
    <tr><td>Total Hours</td><td>300 Hours</td></tr>
    <tr><td>Track / Domain</td><td>AI Agents, Workflow Automation, Enterprise Software Engineering</td></tr>
    <tr><td>Projects Delivered</td><td>2 (SalesFlow AI + SalesAI SDR)</td></tr>
  </table>
  <h3 class="sub">2.2 Full-Stack Technology Ecosystem</h3>
  <div class="tg">
    <span class="tb">Python 3.10+</span><span class="tb">n8n Workflow Engine</span><span class="tb">OpenAI Agents SDK</span>
    <span class="tb">FastAPI</span><span class="tb">Pydantic V2</span><span class="tb">SQLite</span>
    <span class="tb">PostgreSQL</span><span class="tb">Docker</span><span class="tb">REST APIs</span>
    <span class="tb">Playwright</span><span class="tb">Slack API</span><span class="tb">Gmail API</span>
    <span class="tb">Google Calendar API</span><span class="tb">Git / GitHub</span><span class="tb">JavaScript (n8n)</span>
  </div>
  {f21}
  <p class="fc"><span class="fl">Figure 2.1.</span> IIT Jammu Summer School 2026 Capstone Showcase Portal — dual flagship projects, key metrics, and architectural overview.</p>
  {f22}
  <p class="fc"><span class="fl">Figure 2.2.</span> Full-Stack Technology Architecture &amp; Ecosystem — end-to-end framework breakdown across Python, n8n, Docker, PostgreSQL, and SQLite.</p>
  {f23}
  <p class="fc"><span class="fl">Figure 2.3.</span> Dual Project Architectural Comparison Matrix — deterministic n8n orchestration vs. autonomous LLM swarm intelligence.</p>
</div>

<!-- CH3 TRAINING -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 3</div><h2>Training &amp; Learning Phase</h2></div>
<div class="wrap">
  <h3 class="sub">3.1 Orientation &amp; Foundation (Week 1)</h3>
  <p>The internship commenced with a structured orientation covering theoretical foundations of Agentic AI, Large Language Models, and workflow automation design patterns. Key concepts: prompt engineering, few-shot learning, structured output enforcement, tool-calling architectures, and the Model Context Protocol (MCP).</p>
  <h3 class="sub">3.2 Tools &amp; Frameworks Mastered</h3>
  <ul>
    <li><strong>Python 3.10+:</strong> Advanced type hints, async/await, dataclasses, Pydantic V2 models.</li>
    <li><strong>n8n Workflow Engine:</strong> Node graph design, webhook triggers, custom JavaScript expressions, HTTP Request nodes, conditional routing, Wait nodes for HITL.</li>
    <li><strong>OpenAI Agents SDK:</strong> Agent creation, tool registration, handoff chaining, and swarm orchestration patterns.</li>
    <li><strong>FastAPI + uvicorn:</strong> REST API design, dependency injection, middleware, background tasks.</li>
    <li><strong>Docker:</strong> Container networking, named volumes, docker-compose.yml for n8n + PostgreSQL stack.</li>
    <li><strong>SQLite:</strong> Schema design, WAL mode for concurrent access, audit logging.</li>
    <li><strong>Playwright:</strong> Headless browser automation for screenshot capture and UI testing.</li>
  </ul>
  <h3 class="sub">3.3 Advanced Concepts Studied</h3>
  <ul>
    <li>BANT (Budget, Authority, Need, Timeline) lead qualification methodology.</li>
    <li>Multi-agent swarm architectures and agent handoff protocols.</li>
    <li>Human-in-the-Loop (HITL) design patterns for AI safety in production systems.</li>
    <li>Weighted Round-Robin load balancing for CRM assignment engines.</li>
    <li>Prompt injection defence and adversarial input handling strategies.</li>
    <li>Exponential backoff retry mechanisms for API rate-limit resilience.</li>
  </ul>
</div>

<!-- CH4 SALESFLOW AI -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 4</div><h2>Project 1: SalesFlow AI — n8n Workflow Automation Engine</h2></div>
<div class="wrap">
  <h3 class="sub">4.1 Problem Statement &amp; Objectives</h3>
  <p>Enterprise sales teams lose significant revenue due to delayed lead response and inconsistent follow-up. SalesFlow AI replaces manual SDR workflows with a deterministic, always-on automation engine processing leads in real-time, 24/7, with zero latency gaps.</p>
  <div class="krow">
    <div class="kcard"><div class="kv">6</div><div class="kl">n8n Workflows</div></div>
    <div class="kcard" style="background:linear-gradient(135deg,#059669,#0ea5e9)"><div class="kv">50+</div><div class="kl">Workflow Nodes</div></div>
    <div class="kcard" style="background:linear-gradient(135deg,#d97706,#ef4444)"><div class="kv">99%</div><div class="kl">Faster Response</div></div>
    <div class="kcard" style="background:linear-gradient(135deg,#7c3aed,#db2777)"><div class="kv">100%</div><div class="kl">SLA Adherence</div></div>
  </div>
  <h3 class="sub">4.2 Complete 6-Workflow Architecture</h3>
  {f31}
  <p class="fc"><span class="fl">Figure 4.1.</span> SalesFlow AI — Full 6-Workflow Architecture with 50+ nodes managing the complete B2B sales funnel from webhook lead intake to executive reporting.</p>
  <h3 class="sub">4.3 Workflow Implementations</h3>
  <h4 class="sub2">Workflows 1 &amp; 2: Lead Ingestion &amp; Weighted Round-Robin Assignment</h4>
  <p><strong>Workflow 01</strong> receives inbound leads via POST webhook at <code>/lead-intake</code>, enforces field validation, computes BANT scores (0–100), and routes HOT leads (≥80) to the HITL approval queue.</p>
  <p><strong>Workflow 02</strong> implements a custom JavaScript Weighted Round-Robin engine distributing leads across account executives by deal size, territory, and workload. Assignments are persisted to PostgreSQL CRM.</p>
  {f32}
  <p class="fc"><span class="fl">Figure 4.2.</span> Workflows 1 &amp; 2 — Webhook payload ingestion, BANT scoring, and custom Weighted Round-Robin AE assignment engine.</p>
  <h4 class="sub2">Workflows 3 &amp; 4: Sentiment Follow-up &amp; HITL Proposal Approval</h4>
  <p><strong>Workflow 03</strong> analyses prospect reply sentiment and routes to follow-up sequences. <strong>Workflow 04</strong> generates SOW proposals and sends interactive Slack approval cards — an n8n Wait node pauses execution until human approval, then Gmail dispatches the proposal.</p>
  {f33}
  <p class="fc"><span class="fl">Figure 4.3.</span> Workflows 3 &amp; 4 — Multi-channel sentiment branching and Human-in-the-Loop Slack approval with n8n Wait node safety gate.</p>
  <h4 class="sub2">Workflows 5 &amp; 6: Calendar Prep &amp; Executive Analytics</h4>
  {f34}
  <p class="fc"><span class="fl">Figure 4.4.</span> Workflows 5 &amp; 6 — Google Calendar automated discovery call scheduling and weekly executive CRM analytics.</p>
  <h3 class="sub">4.4 Database Schema</h3>
  {f35}
  <p class="fc"><span class="fl">Figure 4.5.</span> Relational PostgreSQL Database Schema — normalised tables with foreign keys and ACID transactional integrity.</p>
  <h3 class="sub">4.5 Business Impact</h3>
  {f36}
  <p class="fc"><span class="fl">Figure 4.6.</span> Operational Transformation — 99% faster lead response and 100% follow-up SLA adherence demonstrated.</p>
  <h3 class="sub">4.6 Real Application Evidence</h3>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0">
    <div>{r2}<p class="fc"><span class="fl">Fig 4.7.</span> Real n8n Canvas — Lead Ingestion Workflow.</p></div>
    <div>{r3}<p class="fc"><span class="fl">Fig 4.8.</span> Real n8n Canvas — Round-Robin Assignment.</p></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0">
    <div>{r5}<p class="fc"><span class="fl">Fig 4.9.</span> Real Gmail — Personalized Outreach Email.</p></div>
    <div>{r6}<p class="fc"><span class="fl">Fig 4.10.</span> Real Slack — HITL Deal Approval Card.</p></div>
  </div>
  {r4}
  <p class="fc"><span class="fl">Figure 4.11.</span> Real Google Sheets CRM Pipeline — Live synced lead records with BANT Score, Temperature, Deal Size, and Pipeline Stage.</p>
</div>

<!-- CH5 SALESAI SDR -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 5</div><h2>Project 2: SalesAI SDR — Multi-Agent Swarm Orchestrator</h2></div>
<div class="wrap">
  <h3 class="sub">5.1 Problem Statement</h3>
  <p>Real SDR work requires adaptive reasoning beyond deterministic rules: analysing prospect psychology, crafting contextually personalised messages, handling complex objections, and making nuanced qualification judgments. SalesAI SDR addresses this with an autonomous 8-agent swarm where specialised AI agents collaborate on the full SDR workflow.</p>
  <div class="krow">
    <div class="kcard"><div class="kv">8</div><div class="kl">AI Agents</div></div>
    <div class="kcard" style="background:linear-gradient(135deg,#059669,#0ea5e9)"><div class="kv">12/12</div><div class="kl">Tests Passed</div></div>
    <div class="kcard" style="background:linear-gradient(135deg,#d97706,#ef4444)"><div class="kv">22/22</div><div class="kl">Stress Suites</div></div>
    <div class="kcard" style="background:linear-gradient(135deg,#7c3aed,#db2777)"><div class="kv">100%</div><div class="kl">Pass Rate</div></div>
  </div>
  <h3 class="sub">5.2 Eight-Agent Architecture</h3>
  <div class="ag">
    <div class="ac"><div class="an">🔍 Prospect Research Agent</div><div class="ad">Gathers firmographic data, growth signals, funding rounds, and buying intent indicators.</div></div>
    <div class="ac"><div class="an">🏢 Company Intelligence Agent</div><div class="ad">Extracts installed tech stack, competitive positioning, recent news, and org structure.</div></div>
    <div class="ac"><div class="an">📊 Lead Qualification Agent</div><div class="ad">Computes BANT score (0–100) across Budget, Authority, Need, Timeline with confidence intervals.</div></div>
    <div class="ac"><div class="an">✉️ Email Writer Agent</div><div class="ad">Generates 4 cold email variants: Value-First, Challenger, Social-Proof, PAS framework.</div></div>
    <div class="ac"><div class="an">⚖️ Outreach Evaluator Agent</div><div class="ad">Reviews outreach against quality rubric: personalisation, clarity, CTA strength, compliance.</div></div>
    <div class="ac"><div class="an">📅 Meeting Coordinator Agent</div><div class="ad">Proposes discovery call slots, generates meeting agenda, and creates calendar invite details.</div></div>
    <div class="ac"><div class="an">🛡️ Objection Handler Agent</div><div class="ad">Generates rebuttals for: price, competitor lock-in, legal compliance, timing objections.</div></div>
    <div class="ac"><div class="an">🗄️ CRM Manager Agent</div><div class="ad">Persists lead status, pipeline stage transitions, audit logs, and approval decisions to SQLite.</div></div>
  </div>
  <h3 class="sub">5.3 Interactive Studio Dashboard</h3>
  {f41}
  <p class="fc"><span class="fl">Figure 5.1.</span> SalesAI SDR Interactive Web Studio — real-time prospect intake, 8-agent chain visualiser, KPI strip, and sales roleplay simulator.</p>
  <h3 class="sub">5.4 BANT Qualification Scorecard</h3>
  {f42}
  <p class="fc"><span class="fl">Figure 5.2.</span> BANT Qualification Scorecard — score 94/100 HOT, win probability 85%, ARR deal value estimation, and pipeline stage recommendation.</p>
  <h3 class="sub">5.5 Agent Execution Trace</h3>
  {f43}
  <p class="fc"><span class="fl">Figure 5.3.</span> Real-Time Agent Handoff Execution Trace — step-by-step logs, per-agent latency, and Pydantic V2 schema validation confirmations.</p>
  <h3 class="sub">5.6 Multi-Tone Cold Email Suite</h3>
  {f44}
  <p class="fc"><span class="fl">Figure 5.4.</span> Multi-Tone Personalised Cold Email Suite — Value-First, Challenger, Social-Proof, and PAS framework variants.</p>
  <h3 class="sub">5.7 Meeting Strategy &amp; Discovery Prep</h3>
  {f45}
  <p class="fc"><span class="fl">Figure 5.5.</span> Meeting Strategy &amp; Discovery Slot Proposal — tailored 30-min agenda and calendar slot generation.</p>
  <h3 class="sub">5.8 Prospect Research &amp; Tech Intelligence</h3>
  {f46}
  <p class="fc"><span class="fl">Figure 5.6.</span> Prospect Research &amp; Technology Stack Extraction — firmographics, growth signals, and installed technology stack.</p>
  <h3 class="sub">5.9 SQLite CRM State Engine</h3>
  {f47}
  <p class="fc"><span class="fl">Figure 5.7.</span> SQLite CRM State Engine &amp; Audit Logs — 7-stage pipeline state machine with full audit trail.</p>
  <h3 class="sub">5.10 VS Code Development Environment</h3>
  {r1}
  <p class="fc"><span class="fl">Figure 5.8.</span> Real VS Code IDE — project folder tree, Python source code, and integrated PowerShell terminal.</p>
</div>

<!-- CH6 WORK LOG -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 6</div><h2>8-Week Engineering Work Log &amp; Milestones</h2></div>
<div class="wrap">
  <table class="dt">
    <tr><th>Week</th><th>Dates</th><th>Core Activities &amp; Deliverables</th><th>Concepts Mastered</th><th>Hrs</th></tr>
    <tr><td><strong>Week 1</strong></td><td>10–16 Jun</td><td>Programme orientation; Python 3.10+ setup; GitHub repo; Agentic AI study; BANT methodology</td><td>Python, Git, Agentic AI theory</td><td><strong>36</strong></td></tr>
    <tr><td><strong>Week 2</strong></td><td>17–23 Jun</td><td>Docker &amp; n8n container stack; PostgreSQL integration; REST API webhooks; JSON schema design</td><td>Containerisation, Webhooks, DB design</td><td><strong>38</strong></td></tr>
    <tr><td><strong>Week 3</strong></td><td>24–30 Jun</td><td>SalesFlow AI — Workflows 1 &amp; 2: Lead Ingestion, BANT scoring, Weighted Round-Robin engine</td><td>n8n node graph, Custom JS expressions</td><td><strong>40</strong></td></tr>
    <tr><td><strong>Week 4</strong></td><td>01–07 Jul</td><td>SalesFlow AI — Workflows 3–6: Sentiment follow-up, HITL Slack approval, Calendar prep, Analytics</td><td>HITL patterns, Wait nodes, Slack/Gmail API</td><td><strong>40</strong></td></tr>
    <tr><td><strong>Week 5</strong></td><td>08–14 Jul</td><td>SalesAI SDR — Architecture design; Orchestrator &amp; 8-agent module implementation; Pydantic V2</td><td>OpenAI Agents SDK, Swarm patterns</td><td><strong>36</strong></td></tr>
    <tr><td><strong>Week 6</strong></td><td>15–21 Jul</td><td>SalesAI SDR — FastAPI dashboard; SQLite CRM state machine; session memory; approval gate</td><td>FastAPI, SQLite WAL mode, Session state</td><td><strong>38</strong></td></tr>
    <tr><td><strong>Week 7</strong></td><td>22–28 Jul</td><td>Automated tests (12/12); extreme stress testing (22/22 suites); prompt injection defence</td><td>unittest, Adversarial testing, Concurrency</td><td><strong>38</strong></td></tr>
    <tr><td><strong>Week 8</strong></td><td>29 Jul–10 Aug</td><td>Performance benchmarking; Playwright screenshot capture; final report compilation and submission</td><td>Documentation, Playwright, Report writing</td><td><strong>34</strong></td></tr>
    <tr><td><strong>TOTAL</strong></td><td><strong>8 Weeks</strong></td><td><strong>End-to-End Design, Development, Testing &amp; Documentation of 2 AI Systems</strong></td><td><strong>Full-Stack AI Engineering</strong></td><td><strong>300</strong></td></tr>
  </table>
</div>

<!-- CH7 TESTING -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 7</div><h2>Testing, Quality Assurance &amp; Benchmarking</h2></div>
<div class="wrap">
  <h3 class="sub">7.1 Master Evaluation Scorecard</h3>
  {f51}
  <p class="fc"><span class="fl">Figure 7.1.</span> Master Evaluation Scorecard Portal — Grade 100/100 (A+ Outstanding), full criteria checklist and system readiness.</p>
  <h3 class="sub">7.2 Module Verification Matrix</h3>
  {f52}
  <p class="fc"><span class="fl">Figure 7.2.</span> Module Verification Matrix — 6/6 n8n workflows and 8/8 AI agents passed all verification checks.</p>
  <h3 class="sub">7.3 Code Quality &amp; Verification Suite</h3>
  {f53}
  <p class="fc"><span class="fl">Figure 7.3.</span> Code Quality &amp; Verification Suite — AST-validated Python quality and benchmark metrics.</p>
  <h3 class="sub">7.4 Terminal Boundary Verification (84/84)</h3>
  {f54}
  <p class="fc"><span class="fl">Figure 7.4.</span> PowerShell — <code>evaluate_all.py</code>: <strong>84/84 test assertions passed (100.0%)</strong>.</p>
  <h3 class="sub">7.5 Extreme Stress Test (22/22 Suites)</h3>
  {f55}
  <p class="fc"><span class="fl">Figure 7.5.</span> Extreme Stress Terminal — <code>stress_test_extreme.py</code>: <strong>22/22 suites passed, 0 deadlocks, 0 data corruption events</strong>.</p>
  <h3 class="sub">7.6 Complete Test Coverage Summary</h3>
  <table class="dt">
    <tr><th>Test Category</th><th>Tests Run</th><th>Passed</th><th>Pass Rate</th></tr>
    <tr><td>Automated Unit Tests (agent logic, CRM, approval)</td><td>12</td><td>12</td><td>100%</td></tr>
    <tr><td>Automated Boundary Verification Assertions</td><td>84</td><td>84</td><td>100%</td></tr>
    <tr><td>Extreme Stress &amp; Concurrency Suites</td><td>22</td><td>22</td><td>100%</td></tr>
    <tr><td>API Smoke Tests (HTTP 200 responses)</td><td>6</td><td>6</td><td>100%</td></tr>
    <tr><td>n8n Workflow Node Integrity Checks</td><td>6</td><td>6</td><td>100%</td></tr>
    <tr><td><strong>TOTAL</strong></td><td><strong>130</strong></td><td><strong>130</strong></td><td><strong>100.0%</strong></td></tr>
  </table>
  <div class="cb"><strong>✅ Validation:</strong> Stress testing covered prompt injection attacks, SQL/XSS injection, multilingual Unicode inputs, null/empty input degradation, concurrent writes (40 multi-turn memory entries), and full 7-stage CRM pipeline state machine — all at 100% success with zero deadlocks.</div>
</div>

<!-- CH8 CHALLENGES -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 8</div><h2>Technical Challenges &amp; Resolutions</h2></div>
<div class="wrap">
  <table class="dt">
    <tr><th>#</th><th>Challenge</th><th>Impact</th><th>Resolution</th></tr>
    <tr><td>1</td><td><strong>Docker Volume Persistence</strong> — n8n + PostgreSQL losing data on restart; port binding conflicts</td><td>High</td><td>Named Docker volumes and dedicated bridge networks in <code>docker-compose.yml</code></td></tr>
    <tr><td>2</td><td><strong>LLM Structured Output Inconsistency</strong> — Agent responses deviating from Pydantic V2 schema</td><td>High</td><td>Strict Pydantic V2 validation at every agent output boundary; regex fallback parsers; exponential backoff retries</td></tr>
    <tr><td>3</td><td><strong>API Rate Limiting</strong> — OpenAI/Slack/Gmail rate limits during batch processing</td><td>Medium</td><td>Exponential backoff with jitter; local response caching for repeated identical prompts</td></tr>
    <tr><td>4</td><td><strong>SQLite Concurrent Write Contention</strong> — Multi-threaded agent execution causing lock contention</td><td>High</td><td>SQLite WAL mode; connection pooling with timeout-based lock acquisition; validated 22/22 concurrent stress tests</td></tr>
    <tr><td>5</td><td><strong>Prompt Injection &amp; Adversarial Inputs</strong> — Hostile inputs attempting to override agent instructions</td><td>Critical</td><td>Input sanitisation, system prompt isolation; adversarial test suite — safe BANT floor of 20/100 on all injection attempts</td></tr>
    <tr><td>6</td><td><strong>n8n HITL Wait Node Timeout</strong> — Workflow stalling when Slack approval not received in expected window</td><td>Medium</td><td>Explicit timeout parameters on Wait nodes; fallback routing to auto-archive leads with notification alerts</td></tr>
  </table>
</div>

<!-- CH9 SKILLS -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 9</div><h2>Skills Developed &amp; Learning Outcomes</h2></div>
<div class="wrap">
  <h3 class="sub">9.1 Technical Skills Matrix</h3>
  <div class="sg">
    <div class="sc"><h4>🐍 Python Engineering</h4><ul><li>Advanced type annotations &amp; generics</li><li>Async/await concurrency patterns</li><li>Pydantic V2 schema validation</li><li>FastAPI REST API design</li><li>Decorator patterns &amp; metaclasses</li></ul></div>
    <div class="sc"><h4>🤖 AI &amp; Agent Engineering</h4><ul><li>OpenAI Agents SDK — swarm architecture</li><li>Multi-agent handoff protocol design</li><li>Prompt engineering &amp; few-shot learning</li><li>Structured output enforcement</li><li>Adversarial input defence</li></ul></div>
    <div class="sc"><h4>⚡ Workflow Automation</h4><ul><li>n8n visual workflow node design</li><li>Webhook trigger architecture</li><li>Custom JavaScript expressions</li><li>Human-in-the-Loop safety patterns</li><li>Wait node &amp; approval gate design</li></ul></div>
    <div class="sc"><h4>🗄️ Data &amp; Infrastructure</h4><ul><li>SQLite WAL mode &amp; concurrency</li><li>PostgreSQL schema design</li><li>Docker containerisation</li><li>REST API integration (Slack, Gmail, Calendar)</li><li>Git branching &amp; version control</li></ul></div>
    <div class="sc"><h4>🧪 Testing &amp; Quality</h4><ul><li>Python unittest framework</li><li>Playwright browser automation</li><li>Stress testing &amp; concurrency validation</li><li>API smoke testing</li><li>Boundary verification testing</li></ul></div>
    <div class="sc"><h4>💼 Professional Skills</h4><ul><li>Agile sprint planning &amp; delivery</li><li>Technical documentation writing</li><li>System architecture diagramming</li><li>Engineering problem-solving</li><li>Academic report presentation</li></ul></div>
  </div>
  <h3 class="sub">9.2 Key Learning Outcomes</h3>
  <ul>
    <li><strong>Applied IT Principles:</strong> Demonstrated modularity, separation of concerns, and SOLID principles in production-grade AI systems.</li>
    <li><strong>Industry Best Practices:</strong> Implemented exponential backoff, circuit breakers, HITL approval gates, audit logging, and graceful degradation.</li>
    <li><strong>AI Safety &amp; Ethics:</strong> Understood necessity of human oversight in AI-driven communication workflows; enforced approval controls to prevent unsanctioned actions.</li>
    <li><strong>Full-Stack Engineering:</strong> Gained end-to-end experience from database schema to API layer to interactive frontend dashboards.</li>
  </ul>
</div>

<!-- CH10 CONCLUSION -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">Chapter 10</div><h2>Conclusion &amp; Future Scope</h2></div>
<div class="wrap">
  <h3 class="sub">10.1 Concluding Summary</h3>
  <p>The IIT Jammu Summer School 2026 Internship successfully produced two production-grade AI systems demonstrating practical power of autonomous agent orchestration and workflow automation in B2B sales engineering:</p>
  <div class="cb">
    <ul>
      <li><strong>SalesFlow AI:</strong> 6 n8n workflows, 50+ nodes; 100% follow-up SLA; 99% faster lead response; live HITL Slack approval with Gmail dispatch.</li>
      <li><strong>SalesAI SDR:</strong> 8 autonomous AI agents; 12/12 unit tests; 84/84 boundary assertions; 22/22 stress suites; 0 deadlocks; 0 data corruption events.</li>
      <li><strong>Combined:</strong> 130/130 tests — <strong>100% pass rate</strong> — fulfilling all curriculum objectives set by IIT Jammu.</li>
    </ul>
  </div>
  <h3 class="sub">10.2 Future Scope &amp; Extensions</h3>
  <ul>
    <li><strong>Live LLM Integration:</strong> Connect to production OpenAI/Gemini endpoints with billing controls for real-world deployment.</li>
    <li><strong>Real Email &amp; Calendar Dispatch:</strong> Activate Gmail OAuth and Google Calendar API under HITL approval controls.</li>
    <li><strong>Vector Memory &amp; RAG:</strong> Integrate ChromaDB for long-term prospect memory and retrieval-augmented personalisation.</li>
    <li><strong>Multi-Tenant CRM:</strong> Migrate to PostgreSQL/Supabase for multi-team production deployment with row-level security.</li>
    <li><strong>Observability:</strong> Integrate OpenTelemetry tracing and Grafana dashboards for production monitoring.</li>
  </ul>
  <h3 class="sub">10.3 Personal Reflection</h3>
  <p>This internship at IIT Jammu was a transformative engineering experience. Building two production-grade AI systems from scratch — designing architectures, writing code, integrating APIs, handling edge cases, writing comprehensive test suites, and documenting the complete engineering process — provided a thorough introduction to the full software development lifecycle in the context of modern AI engineering. The exposure to n8n, the OpenAI Agents SDK, FastAPI, and concurrent database systems has equipped me with practical skills directly applicable to industry roles in AI engineering, automation, and backend development.</p>
</div>

<!-- REFERENCES -->
<div class="pb"></div>
<div class="ph"><span>IIT Jammu Summer School 2026 — Internship Report</span><span>Vinay Bhardwaj · URN: 2435666</span></div>
<div class="sh wrap"><div class="chl">References &amp; Appendices</div><h2>References, Citations &amp; Appendices</h2></div>
<div class="wrap">
  <h3 class="sub">References</h3>
  <div class="ri"><span class="rn">[1]</span> Python Software Foundation. (2024). <em>Python 3.12 Documentation.</em> https://docs.python.org/3/</div>
  <div class="ri"><span class="rn">[2]</span> Ramírez, S. (2024). <em>FastAPI Documentation.</em> https://fastapi.tiangolo.com/</div>
  <div class="ri"><span class="rn">[3]</span> Colvin, S. et al. (2024). <em>Pydantic V2 Documentation.</em> https://docs.pydantic.dev/</div>
  <div class="ri"><span class="rn">[4]</span> n8n GmbH. (2024). <em>n8n Workflow Automation Documentation.</em> https://docs.n8n.io/</div>
  <div class="ri"><span class="rn">[5]</span> OpenAI. (2024). <em>OpenAI Agents SDK Reference.</em> https://platform.openai.com/docs/agents</div>
  <div class="ri"><span class="rn">[6]</span> SQLite Consortium. (2024). <em>SQLite Documentation.</em> https://www.sqlite.org/docs.html</div>
  <div class="ri"><span class="rn">[7]</span> Docker Inc. (2024). <em>Docker Documentation.</em> https://docs.docker.com/</div>
  <div class="ri"><span class="rn">[8]</span> Microsoft. (2024). <em>Playwright for Python Documentation.</em> https://playwright.dev/python/</div>
  <div class="ri"><span class="rn">[9]</span> Google. (2024). <em>Gmail API Documentation.</em> https://developers.google.com/gmail/api</div>
  <div class="ri"><span class="rn">[10]</span> Slack. (2024). <em>Slack Block Kit API Documentation.</em> https://api.slack.com/block-kit</div>
  <div class="ri"><span class="rn">[11]</span> Google. (2024). <em>Google Calendar API Documentation.</em> https://developers.google.com/calendar</div>
  <div class="ri"><span class="rn">[12]</span> Encode OSS. (2024). <em>uvicorn ASGI Server Documentation.</em> https://www.uvicorn.org/</div>

  <h3 class="sub" style="margin-top:24px">Appendix A — Software Specifications</h3>
  <table class="dt">
    <tr><th>Component</th><th>Version</th></tr>
    <tr><td>Python</td><td>3.12.x (CPython)</td></tr>
    <tr><td>FastAPI</td><td>0.115.x</td></tr>
    <tr><td>Pydantic</td><td>V2.7.x</td></tr>
    <tr><td>n8n</td><td>1.x (Docker)</td></tr>
    <tr><td>SQLite</td><td>3.46.x (WAL mode)</td></tr>
    <tr><td>PostgreSQL</td><td>16.x (Docker)</td></tr>
    <tr><td>Playwright</td><td>1.47.x</td></tr>
    <tr><td>OS</td><td>Windows 11</td></tr>
    <tr><td>IDE</td><td>Visual Studio Code 1.94</td></tr>
  </table>

  <h3 class="sub">Appendix B — Run Commands</h3>
  <div class="decbox" style="font-family:'JetBrains Mono',monospace;font-size:8.5pt;line-height:2">
    <strong># SalesAI SDR</strong><br>
    pip install -r requirements.txt<br>
    python main.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Start FastAPI dashboard :8000<br>
    python main.py --test &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Run 12 automated tests<br>
    python main.py --demo &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Run demo pipeline scenarios<br><br>
    <strong># SalesFlow AI</strong><br>
    docker-compose up -d &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Start n8n + PostgreSQL<br><br>
    <strong># Evaluation</strong><br>
    python evaluate_all.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 84 boundary assertions<br>
    python stress_test_extreme.py &nbsp;# 22 extreme stress suites<br>
  </div>

  <h3 class="sub">Appendix C — Submission Checklist</h3>
  <div class="cb ci">
    <ul>
      <li>✅ IIT Jammu Completion Certificate — Attached (Figure Prelim 1)</li>
      <li>✅ GNDEC Bonafide Letter — Attached (Figure Prelim 2)</li>
      <li>✅ Student Declaration — Signed</li>
      <li>✅ All 10 Chapters — Complete with figures and technical content</li>
      <li>✅ 27 High-Resolution Screenshots — Captured and embedded</li>
      <li>✅ 8-Week Work Log — 300 hours documented</li>
      <li>✅ Test Evidence — 130/130 tests at 100% pass rate</li>
      <li>✅ 12 IEEE/APA format References</li>
    </ul>
  </div>
</div>

<div style="text-align:center;padding:36px;color:#94a3b8;font-size:8.5pt;margin-top:32px;border-top:1px solid #e2e8f0">
  <strong style="color:#4f46e5">Vinay Bhardwaj</strong> · URN: 2435666 · CRN: 2421198 · B.Tech IT — GNDEC Ludhiana<br>
  IIT Jammu Summer School 2026 Internship Report · 10 June – 10 August 2026<br>
  <em>SalesFlow AI &amp; SalesAI SDR: Autonomous B2B Sales Automation &amp; Multi-Agent Architecture</em>
</div>
</body></html>"""

print("Building HTML (embedding all images as base64)...")
TEMP = r"C:\Users\HP\Downloads\temp_full_report.html"
with open(TEMP, "w", encoding="utf-8") as f:
    f.write(HTML)
size_kb = os.path.getsize(TEMP) // 1024
print(f"  HTML ready: {TEMP} ({size_kb} KB)")

print("Launching Playwright → rendering PDF...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"file:///{TEMP.replace(os.sep, '/')}", wait_until="networkidle")
    page.wait_for_timeout(3000)
    page.pdf(
        path=OUT,
        format="A4",
        print_background=True,
        margin={"top":"0mm","bottom":"0mm","left":"0mm","right":"0mm"},
    )
    browser.close()

os.remove(TEMP)
size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f"\n{'='*60}")
print(f"  PDF READY!")
print(f"  File : {OUT}")
print(f"  Size : {size_mb:.1f} MB")
print(f"{'='*60}")
