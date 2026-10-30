"""
Convert the verified IIT Jammu Summer School 2026 Internship Report to .docx format.
Generates:
1. IIT_Jammu_Summer_School_2026_Final_Internship_Report.docx
2. Vinay_Bhardwaj_IIT_Jammu_Summer_School_2026_Final_Report.docx
3. submission/IIT_Jammu_Summer_School_2026_Final_Internship_Report.docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report_document(output_path):
    doc = docx.Document()

    # Set page margins (1 inch all around)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styling helper
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(24)
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor(15, 23, 42)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(71, 85, 105)
        run.font.name = "Calibri"
        p.paragraph_format.space_after = Pt(18)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor(79, 70, 229)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_body(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.bold = True
            run_b.font.size = Pt(11)
            run_b.font.name = "Calibri"
            run_b.font.color.rgb = RGBColor(15, 23, 42)
        run_t = p.add_run(text)
        run_t.font.size = Pt(11)
        run_t.font.name = "Calibri"
        run_t.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.bold = True
            run_b.font.size = Pt(11)
            run_b.font.name = "Calibri"
            run_b.font.color.rgb = RGBColor(15, 23, 42)
        run_t = p.add_run(text)
        run_t.font.size = Pt(11)
        run_t.font.name = "Calibri"
        run_t.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_placeholder_box(title, instructions):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(f"[{title.upper()}]\n")
        r1.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(180, 83, 9)
        r2 = p.add_run(instructions)
        r2.italic = True
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(100, 116, 139)
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ── COVER / TITLE ─────────────────────────────────────────────────────────
    add_title("SUMMER SCHOOL 2026 INTERNSHIP REPORT")
    add_subtitle("Indian Institute of Technology (IIT) Jammu\nProgram: AI Agents & Workflow Automation\nDuration: [Insert Approved Dates, e.g., 10 June 2026 – 10 August 2026 (8 Weeks)]")

    # Candidate Info Table
    info_table = doc.add_table(rows=6, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Student Name:", "Vinay Bhardwaj"),
        ("Roll Number / Student ID:", "[Your University Roll Number / Student ID]"),
        ("Degree & Branch:", "[Your Degree & Branch, e.g., B.Tech in CSE / IT]"),
        ("Home Institution / College:", "[Your College / University Name, e.g., UIET / GNDEC]"),
        ("Host Institution:", "Indian Institute of Technology (IIT) Jammu"),
        ("Capstone Projects:", "1. SalesFlow AI (n8n Assignment 4 — 6 Workflows, 50 Nodes)\n2. SalesAI SDR (AI Agents Assignment 2 — 6 Agents, Web/CRM Tools)")
    ]
    for i, (label, val) in enumerate(info_data):
        c0 = info_table.cell(i, 0)
        c1 = info_table.cell(i, 1)
        c0.width = Inches(2.3)
        c1.width = Inches(4.2)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(10.5)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.size = Pt(10.5)

    doc.add_page_break()

    # ── PRELIMINARY PAGES ─────────────────────────────────────────────────────
    add_h1("Preliminary Certificates & Declaration")
    
    add_h2("1. Certificate of Internship Completion")
    add_placeholder_box("Attachment: IIT Jammu Official Completion Certificate", "Please insert or attach the scanned copy of your official IIT Jammu Summer School 2026 completion certificate here.")

    add_h2("2. College Approval / Bonafide Certificate")
    add_placeholder_box("Attachment: Home College Bonafide / NOC Letter", "Please insert or attach the scanned copy of your home institution Bonafide or No Objection Certificate (NOC) here.")

    add_h2("3. Student Declaration")
    add_body("I, Vinay Bhardwaj (Roll No: [Your University Roll Number]), student of [Your Degree/Branch] at [Your College/University Name], hereby declare that this Internship Report entitled \"Enterprise Sales Automation & Autonomous Multi-Agent Systems: SalesFlow AI (n8n) & SalesAI SDR\" is an authentic record of the independent engineering work, research, and software development carried out by me during the Summer School 2026 Internship Program at the Indian Institute of Technology (IIT) Jammu from [Insert Approved Dates]. The work presented herein is original and has not been submitted elsewhere for any academic degree.")
    add_body("Name: Vinay Bhardwaj\nDate: [Insert Submission Date, e.g., 23 October 2026]\nPlace: [Insert City, e.g., Jammu / Home City]", bold_prefix="Candidate Details:\n")

    add_h2("4. Certificate of Mentorship / Approval")
    add_body("This is to certify that the internship projects documented in this report have been carried out by Vinay Bhardwaj under guidance and supervision during the Summer School 2026 at the Indian Institute of Technology (IIT) Jammu.")
    add_body("Faculty Mentor Name: [Supervisor / Faculty Mentor Name]\nDesignation: [Faculty Designation]\nDepartment: Department of Computer Science & Engineering, IIT Jammu", bold_prefix="Supervisor Details:\n")

    add_h2("5. Acknowledgements")
    add_body("I express my sincere gratitude to the Indian Institute of Technology (IIT) Jammu for organizing the Summer School 2026 on AI Agents & Workflow Automation. I am deeply thankful to the faculty mentors, course coordinators, and technical staff at IIT Jammu for their invaluable mentorship, architectural guidance, and continuous technical support throughout the development of these capstone projects. I also extend my heartfelt appreciation to the leadership and faculty of [Your College / University Name] for providing continuous encouragement.")

    add_h2("6. Executive Summary / Abstract")
    add_body("Modern enterprise sales operations face critical operational bottlenecks: over 65% of sales representatives' time is consumed by repetitive administrative data entry, manual prospect research, and lead qualification, resulting in delayed follow-up times and missed revenue opportunities.")
    add_body("This internship report details the engineering design, technical implementation, and empirical verification of two integrated, production-ready enterprise sales automation solutions:")
    add_bullet("An end-to-end event-driven workflow automation platform orchestrated via n8n, comprising 6 distinct workflows with a verified total of 50 nodes. The platform automates the inbound sales lifecycle through Webhook and Cron triggers, state-driven PostgreSQL data modeling (leads, sales_reps, follow_ups), 100-point GPT-4o BANT qualification, dynamic skill- and workload-based sales representative routing, automated 5-touch email sequences with Google Calendar discovery reservation, Human-in-the-Loop (HITL) proposal generation gated by manager token approval, and weekly executive analytics reporting to Google Sheets and Slack.", bold_prefix="1. SalesFlow AI (n8n Assignment 4 Capstone): ")
    add_bullet("A resilient autonomous multi-agent swarm coordinating 6 specialized Python agents (ProspectResearchAgent, LeadQualificationAgent, EmailWriterAgent, MeetingCoordinatorAgent, ObjectionHandlerAgent, CRMManagerAgent). Built with an instructor-approved multi-provider LLM abstraction leveraging Google Gemini 2.0 Flash (primary) and Groq LLaMA-3.1 (fallback), the system incorporates live zero-cost web enrichment (DuckDuckGo search & Wikipedia API), SQLite CRM database persistence (salesai.db in WAL mode), automated calendar ICS agenda generation, real-time objection coaching with interactive sales roleplay, and a unified dual-tab Gradio 6.30 dashboard.", bold_prefix="2. SalesAI SDR (AI Agents Assignment 2 Capstone): ")
    add_body("Both systems have been thoroughly tested and validated on Python 3.12 with a dedicated verification suite achieving a 100% pass rate.")

    doc.add_page_break()

    # ── CHAPTER 1 ─────────────────────────────────────────────────────────────
    add_h1("Chapter 1: Introduction & Industry Context")
    add_h2("1.1 Background & Industry Problem")
    add_body("In contemporary B2B enterprise software and service organizations, the Sales Development Representative (SDR) function serves as the primary bridge between raw market interest and revenue generation. However, empirical studies reveal that SDR teams spend less than 35% of their working hours actively engaging prospects. Over 65% of their operational bandwidth is dissipated across administrative overhead, manual search engine research, subjective lead triage, fragmented CRM entry, and repetitive drafting of follow-up emails.")
    add_body("Furthermore, prospect responsiveness decays exponentially over time: leads engaged within 5 minutes are 21 times more likely to enter the sales qualification pipeline than those contacted after 30 minutes. When manual triage causes lead response latencies of 12 to 48 hours, enterprise sales pipelines suffer severe conversion drop-offs.")

    add_h2("1.2 Purpose & Scope of the Internship")
    add_body("The Summer School 2026 Internship Program at the Indian Institute of Technology (IIT) Jammu was formulated to address these enterprise productivity bottlenecks by applying advanced concepts in Autonomous Artificial Intelligence Agents, Large Language Model (LLM) Orchestration, and Visual Workflow Automation.")
    add_body("The objective of the internship was to engineer, implement, verify, and document two distinct yet complementary capstone platforms:")
    add_bullet("An event-driven workflow automation architecture built on n8n that completely automates data movement, scoring, routing, and managerial oversight across 6 production workflows and 50 nodes.", bold_prefix="Project 1: ")
    add_bullet("A Python-based multi-agent system combining 6 specialized autonomous agents equipped with real-time web search tools, CRM persistence, meeting scheduling, and conversational sales roleplay.", bold_prefix="Project 2: ")

    # ── CHAPTER 4 ─────────────────────────────────────────────────────────────
    add_h1("Chapter 4: Project 1 — SalesFlow AI (n8n Automation Platform)")
    add_h2("4.1 Architecture & Decoupled State Machine")
    add_body("SalesFlow AI implements an event-driven architecture where 6 independent workflows operate asynchronously across a shared PostgreSQL database state machine. Workflows transition records across standardized states: NEW -> SCORED -> QUALIFIED -> ASSIGNED -> ENGAGED -> PROPOSAL_SENT.")

    # Table of 6 Workflows
    wf_table = doc.add_table(rows=7, cols=5)
    wf_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["#", "Workflow Name", "Trigger", "Key Integrations", "Nodes"]
    for j, h in enumerate(headers):
        cell = wf_table.cell(0, j)
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)

    wf_data = [
        ("WF-01", "Lead Capture & Registration", "Webhook POST /capture-lead", "GPT-4o, Postgres, Gmail, Slack", "9"),
        ("WF-02", "AI Lead Scoring & BANT", "Webhook POST /qualify-lead", "GPT-4o BANT, Postgres, Google Sheets", "8"),
        ("WF-03", "Sales Rep Assignment", "Webhook POST /assign-rep", "Smart Round-Robin, Gmail, Slack", "8"),
        ("WF-04", "Follow-up Cadence & Meetings", "Cron (Every 8 Hours)", "GPT-4o, Gmail, Google Calendar", "8"),
        ("WF-05", "AI Proposal Generation + HITL", "Webhook POST /generate-proposal", "GPT-4o, Google Drive, Wait Node, Gmail", "10"),
        ("WF-06", "Weekly Analytics & Reporting", "Cron (Monday 08:00 AM)", "SQL Aggregation, GPT-4o, Sheets, Slack", "7")
    ]
    for i, row in enumerate(wf_data):
        bg = "F8FAFC" if i % 2 == 0 else "FFFFFF"
        for j, val in enumerate(row):
            cell = wf_table.cell(i+1, j)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9.5)

    add_body("Total Verified Nodes across all 6 workflows: Exactly 50 Nodes (Exceeds the 20–25 node assignment requirement).", bold_prefix="\nNode Count Verification: ")

    add_h2("4.2 Human-in-the-Loop (HITL) Governance")
    add_body("In Workflow 05, rather than directly sending commercial proposals to high-value prospects without review, the workflow leverages an n8n Wait Node. The system generates an interactive email to the Sales VP with unique Approve and Reject callback URLs. Execution state pauses safely. Upon manager approval, the proposal is dispatched via Gmail OAuth2 and status updated in PostgreSQL.")

    # ── CHAPTER 5 ─────────────────────────────────────────────────────────────
    add_h1("Chapter 5: Project 2 — SalesAI SDR (Autonomous Multi-Agent System)")
    add_h2("5.1 6-Agent Swarm Architecture")
    add_body("The SalesAI SDR multi-agent system coordinates 6 specialized Python agents adhering to the BaseAgent abstract pattern, utilizing structured JSON input/output schemas and conversational memory.")

    # Table of 6 Agents
    ag_table = doc.add_table(rows=7, cols=3)
    ag_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ag_headers = ["Agent Name", "Operational Role", "Key Capabilities & Tools"]
    for j, h in enumerate(ag_headers):
        cell = ag_table.cell(0, j)
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)

    ag_data = [
        ("ProspectResearchAgent", "Intelligence Analyst", "Live web scraping via DuckDuckGo and Wikipedia (zero cost), finds pain points & hooks"),
        ("LeadQualificationAgent", "Qualification Specialist", "100-point BANT scoring matrix (Budget, Authority, Need, Timeline; 25 pts each), deal size & win probability"),
        ("EmailWriterAgent", "Sales Copywriter", "5-touch cadence email generation, A/B subject line variants, 300-char LinkedIn InMail companion"),
        ("MeetingCoordinatorAgent", "Scheduling Specialist", "Discovery call agendas, calendar availability routing, RFC-5545 .ics calendar invites, booking links"),
        ("ObjectionHandlerAgent", "Tactical Coach", "Real-time objection reframing (Acknowledge -> Reframe -> Question), interactive sales roleplay mode"),
        ("CRMManagerAgent", "Pipeline Manager", "SQLite CRM database persistence (salesai.db in WAL mode), pipeline telemetry, revenue forecasting")
    ]
    for i, row in enumerate(ag_data):
        bg = "F8FAFC" if i % 2 == 0 else "FFFFFF"
        for j, val in enumerate(row):
            cell = ag_table.cell(i+1, j)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9.5)

    add_h2("5.2 Multi-Provider LLM Resilience")
    add_body("To address OpenAI API quota limitations, the instructor approved using alternative providers. The system implements a resilient multi-provider abstraction in agents.base.call_ai() leveraging Google Gemini 2.0 Flash as the primary provider and Groq LLaMA-3.1 as an ultra-fast fallback provider. This zero-cost operational setup guarantees continuous functionality.")

    # ── CHAPTER 6 ─────────────────────────────────────────────────────────────
    add_h1("Chapter 6: Weekly Engineering Work Log")
    log_table = doc.add_table(rows=9, cols=5)
    log_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    log_headers = ["Week", "Dates", "Core Engineering Activities", "Key Concepts Learned", "Hours"]
    for j, h in enumerate(log_headers):
        cell = log_table.cell(0, j)
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)

    log_data = [
        ("Week 1", "[Dates Week 1, e.g., 10–16 Jun]", "Orientation, Python 3.12 setup, agent architecture design.", "Multi-Agent Systems, OOP", "[36 hrs]"),
        ("Week 2", "[Dates Week 2, e.g., 17–23 Jun]", "n8n setup, REST Webhooks, PostgreSQL relational schema creation.", "Webhooks, PostgreSQL, DDL", "[38 hrs]"),
        ("Week 3", "[Dates Week 3, e.g., 24–30 Jun]", "Built WF-01 (Lead Capture) & WF-02 (BANT Qualification) in n8n.", "GPT-4o Prompting, Switch Nodes", "[40 hrs]"),
        ("Week 4", "[Dates Week 4, e.g., 01–07 Jul]", "Built WF-03 (Rep Assignment) & WF-04 (Follow-up Cadence); GCal API.", "Cron Triggers, Smart Matching", "[40 hrs]"),
        ("Week 5", "[Dates Week 5, e.g., 08–14 Jul]", "Implemented WF-05 (HITL Proposal Wait Node) & WF-06 (KPI Analytics).", "Wait Nodes, HITL Governance", "[38 hrs]"),
        ("Week 6", "[Dates Week 6, e.g., 15–21 Jul]", "Engineered Python agents (Research, Qualify, Email); Gemini/Groq LLM.", "DuckDuckGo Scraping, BANT", "[40 hrs]"),
        ("Week 7", "[Dates Week 7, e.g., 22–28 Jul]", "Added MeetingCoordinatorAgent, Objection roleplay, SQLite CRM.", "SQLite WAL, Objection Coaching", "[36 hrs]"),
        ("Week 8", "[Dates Week 8, e.g., 29 Jul–04 Aug]", "Built unified Gradio 6.30 dashboard, wrote test suite, compiled report.", "Gradio Blocks, System Testing", "[32 hrs]")
    ]
    for i, row in enumerate(log_data):
        bg = "F8FAFC" if i % 2 == 0 else "FFFFFF"
        for j, val in enumerate(row):
            cell = log_table.cell(i+1, j)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9.5)

    add_body("Total Cumulative Logged Hours: [300 hrs across 8 Weeks]. Date ranges and logged hours are formatted with clear bracketed placeholders to allow adjustment to official institutional documentation.", bold_prefix="\nWork Log Summary: ")

    # ── CHAPTER 9 ─────────────────────────────────────────────────────────────
    add_h1("Chapter 9: System Verification, Testing & Evaluation")
    add_h2("9.1 Automated Test Runner & Results")
    add_body("The complete system was validated via python test_import.py. The test suite verifies:")
    add_bullet("Gradio 6.30 environment and UI Blocks configuration.")
    add_bullet("LLM API client connectivity (Google Gemini 2.0 Flash primary, Groq fallback).")
    add_bullet("Successful instantiation and schema validation of all 6 specialized agents.")
    add_bullet("SQLite CRM database initialization, WAL mode status, and schema integrity.")
    add_bullet("Validation of all 6 N8N workflow JSON files confirming exactly 50 total nodes.")
    add_bullet("Execution of the Live N8N Workflow Simulator with simulated telemetry.")
    add_bullet("FastAPI REST backend router verification.")
    add_body("Test Result: ALL TESTS PASSED (Exit Code 0) — Ready for professional IIT submission.", bold_prefix="Execution Outcome: ")

    add_h2("9.2 Working vs. Simulated Features")
    add_bullet("SQLite database persistence, Gemini/Groq LLM reasoning, DuckDuckGo live web research, interactive Gradio dual-tab UI, FastAPI REST server, and live workflow simulator.", bold_prefix="Verified Working Local Features: ")
    add_bullet("SMTP email sending operates in safe simulated logging mode unless credentials are provided. N8N workflows are validated as compliant JSON blueprints ready for deployment.", bold_prefix="Features in Simulation Mode: ")

    # ── CHAPTER 10 ────────────────────────────────────────────────────────────
    add_h1("Chapter 10: Conclusion")
    add_body("The Summer School 2026 capstone projects successfully demonstrate an enterprise-grade autonomous sales development platform. SalesFlow AI provides a reliable visual workflow backbone across 50 nodes with human approval gating, while SalesAI SDR coordinates 6 specialized AI agents with live research and CRM tools. Together, they represent a complete, verified solution for modern B2B sales automation.")

    doc.save(output_path)
    print(f"[OK] Generated: {output_path}")

if __name__ == "__main__":
    create_report_document("IIT_Jammu_Summer_School_2026_Final_Internship_Report.docx")
    create_report_document("Vinay_Bhardwaj_IIT_Jammu_Summer_School_2026_Final_Report.docx")
    create_report_document(os.path.join("submission", "IIT_Jammu_Summer_School_2026_Final_Internship_Report.docx"))
