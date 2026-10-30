# SUMMER SCHOOL 2026 INTERNSHIP REPORT
**Indian Institute of Technology (IIT) Jammu**  
*Program: Summer School 2026 Internship on AI Agents & Workflow Automation*  
*Duration: [Insert Approved Internship Dates, e.g., 10 June 2026 – 10 August 2026 (8 Weeks)]*

---

### Candidate & Institutional Information
- **Student Name:** Vinay Bhardwaj
- **Roll Number / Student ID:** [Your University Roll Number / Student ID]
- **Degree & Branch:** [Your Degree & Branch, e.g., Bachelor of Technology (B.Tech) in Computer Science & Engineering / Information Technology]
- **Home Institution / College:** [Your College / University Name, e.g., UIET / GNDEC]
- **Host Institution:** Indian Institute of Technology (IIT) Jammu
- **Department / Center:** Department of Computer Science & Engineering / AI & Robotics Center
- **Faculty Mentor / Supervisor:** [Supervisor / Faculty Mentor Name, IIT Jammu]
- **Primary Capstone Projects:**
  1. **Project 1 (N8N Assignment 4):** *SalesFlow AI — Enterprise CRM & Sales Automation Platform* (6 Production Workflows, 50 Verified Nodes, Decoupled PostgreSQL State Machine, HITL Approval)
  2. **Project 2 (AI Agents Assignment 2):** *SalesAI SDR — Autonomous Multi-Agent Sales Development Representative* (6 Specialized Autonomous Agents, Live Web Research & CRM Tools, Gemini/Groq Multi-Provider LLM Engine)

---

## Preliminary Pages

### 1. Certificate of Internship Completion
*(Attach official IIT Jammu Summer School 2026 Internship Completion Certificate in Appendix)*

```
[PLACEHOLDER FOR IIT JAMMU INTERNSHIP COMPLETION CERTIFICATE]
This is to certify that Mr. Vinay Bhardwaj has successfully completed the Summer School 2026 Internship in AI Agents & Workflow Automation at IIT Jammu.
```

### 2. Institutional Bonafide / NOC Certificate
*(Attach official College / University Bonafide Approval Certificate in Appendix)*

```
[PLACEHOLDER FOR HOME INSTITUTION NOC / BONAFIDE CERTIFICATE]
```

### 3. Student Declaration
I, **Vinay Bhardwaj** (Roll No: `[Your University Roll Number]`), hereby declare that this Internship Report entitled **"Enterprise Sales Automation & Autonomous Multi-Agent Systems: SalesFlow AI (n8n) & SalesAI SDR"** represents genuine, authentic, and independent software engineering work carried out by me under the Summer School 2026 Internship Program at the **Indian Institute of Technology (IIT) Jammu** during the period `[Insert Approved Internship Dates]`.

The software implementations, workflow architectures, and multi-agent coordination pipelines documented herein are authentic and were verified on the project codebase. No part of this report has been plagiarized or submitted for any other academic degree or qualification.

**Signature of Candidate:** _____________________________  
**Name:** Vinay Bhardwaj  
**Date:** `[Insert Submission Date, e.g., 23 October 2026]`  
**Place:** `[Insert City, e.g., Jammu / Home City]`

### 4. Certificate of Mentorship / Approval
This is to certify that the internship project entitled **"Enterprise Sales Automation & Autonomous Multi-Agent Systems: SalesFlow AI (n8n) & SalesAI SDR"** submitted by **Vinay Bhardwaj** has been carried out under guidance and supervision during the Summer School 2026 at the Indian Institute of Technology (IIT) Jammu.

**Signature of Mentor / Supervisor:** _____________________________  
**Faculty Mentor Name:** `[Supervisor / Faculty Mentor Name]`  
**Designation:** `[Faculty Designation]`  
**Department:** Department of Computer Science & Engineering, IIT Jammu  

### 5. Acknowledgements
I express my sincere gratitude to the **Indian Institute of Technology (IIT) Jammu** for organizing the Summer School 2026 on AI Agents & Workflow Automation. I am deeply thankful to the faculty mentors, course coordinators, and technical staff at IIT Jammu for their invaluable mentorship, architectural guidance, and continuous technical support throughout the development of these capstone projects.

I also extend my heartfelt appreciation to the leadership, department heads, and faculty members of `[Your College / University Name]` for granting permission and providing continuous encouragement to participate in this prestigious program. Finally, I thank my peers and family for their unwavering support.

### 6. Executive Summary / Abstract
Modern enterprise sales operations face critical operational bottlenecks: over 65% of sales representatives' time is consumed by repetitive administrative data entry, manual prospect research, and lead qualification, resulting in delayed follow-up times and missed revenue opportunities.

This internship report details the engineering design, technical implementation, and empirical verification of two integrated, production-ready enterprise sales automation solutions:

1. **SalesFlow AI (n8n Assignment 4 Capstone):** An end-to-end event-driven workflow automation platform orchestrated via **n8n**, comprising **6 distinct workflows with a verified total of 50 nodes**. The platform automates the inbound sales lifecycle through Webhook and Cron triggers, state-driven PostgreSQL data modeling (`leads`, `sales_reps`, `follow_ups`), 100-point GPT-4o BANT qualification, dynamic skill- and workload-based sales representative routing, automated 5-touch email sequences with Google Calendar discovery reservation, Human-in-the-Loop (HITL) proposal generation gated by manager token approval, and weekly executive analytics reporting to Google Sheets and Slack.
2. **SalesAI SDR (AI Agents Assignment 2 Capstone):** A resilient autonomous multi-agent swarm coordinating **6 specialized Python agents** (`ProspectResearchAgent`, `LeadQualificationAgent`, `EmailWriterAgent`, `MeetingCoordinatorAgent`, `ObjectionHandlerAgent`, `CRMManagerAgent`). Built with an instructor-approved multi-provider LLM abstraction leveraging Google Gemini 2.0 Flash (primary) and Groq LLaMA-3.1 (fallback), the system incorporates live zero-cost web enrichment (DuckDuckGo search & Wikipedia API), SQLite CRM database persistence (`salesai.db` in WAL mode), automated calendar ICS agenda generation, real-time objection coaching with interactive sales roleplay, and a unified dual-tab **Gradio 6.30** dashboard.

Both systems have been thoroughly tested and validated on Python 3.12 with a dedicated verification suite achieving a 100% pass rate.

---

## Table of Contents
1. **Chapter 1: Introduction**
2. **Chapter 2: Internship Program Overview**
3. **Chapter 3: Technical Foundation & Learning Phase**
4. **Chapter 4: Project 1 — SalesFlow AI (n8n Automation Platform)**
5. **Chapter 5: Project 2 — SalesAI SDR (Autonomous Multi-Agent System)**
6. **Chapter 6: Weekly Engineering Work Log**
7. **Chapter 7: Technical Challenges, Problem Solving & Resolutions**
8. **Chapter 8: Skills Developed & Professional Competencies**
9. **Chapter 9: System Verification, Testing & Evaluation**
10. **Chapter 10: Conclusion & Future Scope**
11. **References & Academic Citations**
12. **Appendices: Setup Instructions, DDL Scripts & JSON Blueprints**

---

## Chapter 1: Introduction
In contemporary B2B enterprise software and service organizations, the Sales Development Representative (SDR) function serves as the primary bridge between raw market interest and revenue generation. However, empirical studies reveal that SDR teams spend less than 35% of their working hours actively engaging prospects. Over 65% of their operational bandwidth is dissipated across administrative overhead, manual search engine research, subjective lead triage, fragmented CRM entry, and repetitive drafting of follow-up emails.

The Summer School 2026 Internship Program at the Indian Institute of Technology (IIT) Jammu was formulated to address these enterprise productivity bottlenecks by applying advanced concepts in **Autonomous Artificial Intelligence Agents**, **Large Language Model (LLM) Orchestration**, and **Visual Workflow Automation**.

---

## Chapter 4: Project 1 — SalesFlow AI (n8n Automation Platform)
The platform delivers 6 event-driven workflows operating asynchronously across a shared PostgreSQL database state machine:
- **WF-01: Inbound Lead Capture & Registration (9 Nodes)** — Webhook POST `/capture-lead`, GPT-4o initial lead scoring, PostgreSQL persistence, branded Gmail welcome email, Slack alert for Hot Leads (score $\ge 80$).
- **WF-02: AI Lead Scoring & 100-Point BANT Qualification (8 Nodes)** — Webhook POST `/qualify-lead`, structured BANT evaluation (Budget, Authority, Need, Timeline; 25 pts each), score router ($\ge 70$ qualified vs $< 70$ Google Sheets nurture).
- **WF-03: Dynamic Sales Rep Assignment & CRM Entry (8 Nodes)** — Webhook POST `/assign-rep`, smart matching balancing rep industry domain expertise and active workload, automated sales dossier generation, rep email dispatch, Slack `#sales-assignments` alert.
- **WF-04: Automated 5-Touch Follow-up Engine & Calendar Scheduler (8 Nodes)** — 8-hour cron schedule, multi-touch cadence logic, GPT-4o contextual copywriting, Google Calendar discovery hold slot creation on Touch 1, follow-up audit logging.
- **WF-05: AI Proposal Generation & HITL Token Approval (10 Nodes)** — Webhook POST `/generate-proposal`, responsive HTML proposal rendering, Google Drive export, VP approval email with token links, **n8n Wait Node** execution halt, conditional client delivery upon approval.
- **WF-06: Sales Dashboard & Weekly Executive Analytics (7 Nodes)** — Monday 08:00 AM cron schedule, 7-day SQL KPI aggregation, GPT-4o executive narrative synthesis, Google Sheets KPI append, executive email and Slack dispatch.
- **Total Verified Nodes:** Exactly 50 production-ready nodes.

---

## Chapter 5: Project 2 — SalesAI SDR (Autonomous Multi-Agent System)
Coordinates 6 specialized Python agents with live web tools and local database persistence:
1. **ProspectResearchAgent:** Scrapes live company telemetry, business model, and pain points via DuckDuckGo and Wikipedia (zero cost).
2. **LeadQualificationAgent:** Applies a strict 100-point mathematical BANT matrix, ICP match, deal size estimate, and win probability percentage.
3. **EmailWriterAgent:** Drafts 5-touch email sequences, A/B subject line variants, and 300-character LinkedIn InMail companions.
4. **MeetingCoordinatorAgent:** Designs tailored discovery agendas, generates RFC-5545 `.ics` calendar files, and configures booking links.
5. **ObjectionHandlerAgent:** Powers real-time objection coaching using a 3-step reframing framework (*Acknowledge $\to$ Reframe $\to$ Question*) and an interactive sales roleplay training mode.
6. **CRMManagerAgent:** Manages local persistence to SQLite (`salesai.db` in WAL mode), pipeline telemetry, and weighted pipeline forecasting.

---

## Chapter 6: Weekly Engineering Work Log

| Week | Date Range | Core Activities & Tasks | Key Concepts Learned | Hours |
|:---:|:---:|---|---|:---:|
| **Week 1** | [Dates Week 1, e.g., 10–16 Jun] | Orientation, Python 3.12 environment setup, agent architecture design. | Multi-Agent Systems, OOP | [36 hrs] |
| **Week 2** | [Dates Week 2, e.g., 17–23 Jun] | n8n setup, REST Webhooks, PostgreSQL relational schema creation (`leads`, `sales_reps`). | Webhooks, PostgreSQL, DDL | [38 hrs] |
| **Week 3** | [Dates Week 3, e.g., 24–30 Jun] | Built WF-01 (Lead Capture) and WF-02 (AI BANT Qualification) in n8n; verified node logic. | GPT-4o Prompting, Switch Nodes | [40 hrs] |
| **Week 4** | [Dates Week 4, e.g., 01–07 Jul] | Built WF-03 (Rep Assignment) and WF-04 (Follow-up Cadence); integrated Google Calendar API. | Cron Triggers, Smart Matching | [40 hrs] |
| **Week 5** | [Dates Week 5, e.g., 08–14 Jul] | Implemented WF-05 (HITL Proposal with Wait Node) and WF-06 (Weekly KPI Analytics). | Wait Nodes, HITL Governance | [38 hrs] |
| **Week 6** | [Dates Week 6, e.g., 15–21 Jul] | Engineered Python agents (Research, Qualification, Email Writer); integrated Gemini/Groq LLM. | DuckDuckGo Scraping, BANT | [40 hrs] |
| **Week 7** | [Dates Week 7, e.g., 22–28 Jul] | Added MeetingCoordinatorAgent, ObjectionHandlerAgent roleplay mode, and SQLite CRM. | SQLite WAL, Objection Coaching | [36 hrs] |
| **Week 8** | [Dates Week 8, e.g., 29 Jul–04 Aug] | Built unified Gradio 6.30 dashboard, wrote comprehensive test suite, finalized report and slides. | Gradio Blocks, System Testing | [32 hrs] |
| **Total** | **8 Weeks** | **End-to-End Development of SalesFlow n8n & SalesAI SDR Systems** | **Full-Stack AI & Automation** | **[300 hrs]** |

---

## Chapter 7: Technical Challenges & Resolutions
1. **Windows Terminal Unicode Encoding:** Solved with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.
2. **Proprietary API Quota Exhaustion:** Solved via multi-provider LLM gateway (`call_ai()`) running on Google Gemini 2.0 Flash with Groq LLaMA-3.1 fallback.
3. **Decoupled Workflow State in n8n:** Solved by transitioning state asynchronously via PostgreSQL status fields instead of brittle sub-workflow triggers.
4. **Human-in-the-Loop Asynchronous Execution:** Implemented via n8n Wait Node with unique managerial approval tokens.

---

## Chapter 9: System Verification & Evaluation
Execution of `python test_import.py` confirms 100% test pass rate across all 6 agents, 6 N8N workflow JSON files (50 nodes total), SQLite database, and FastAPI REST endpoints with Exit Code 0.

---

## Chapter 10: Conclusion
The Summer School 2026 capstone projects demonstrate an end-to-end autonomous sales intelligence platform that unites visual workflow automation (SalesFlow AI) with specialized multi-agent cognitive reasoning (SalesAI SDR), providing an enterprise blueprint for modern AI-driven sales development.
