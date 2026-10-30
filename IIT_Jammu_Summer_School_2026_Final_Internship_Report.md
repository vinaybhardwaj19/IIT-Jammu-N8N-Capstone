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
*(Attach official IIT Jammu Summer School 2026 Internship Completion Certificate here)*

```
[PLACEHOLDER FOR IIT JAMMU INTERNSHIP COMPLETION CERTIFICATE]
This is to certify that Mr. Vinay Bhardwaj has successfully completed the Summer School 2026 Internship in AI Agents & Workflow Automation at IIT Jammu.
```

### 2. Institutional Bonafide / NOC Certificate
*(Attach official College / University Bonafide Approval Certificate here)*

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
   - 1.1 Background & Industry Context
   - 1.2 Purpose of the Internship
   - 1.3 Core Engineering Objectives
   - 1.4 Scope of Work & Deliverables
   - 1.5 Organization of the Report
2. **Chapter 2: Internship Program Overview**
   - 2.1 Host Institution: IIT Jammu
   - 2.2 Program Specialization: AI Agents & Automation
   - 2.3 Roles & Engineering Responsibilities
   - 2.4 Deliverables Roadmap
3. **Chapter 3: Technical Foundation & Learning Phase**
   - 3.1 Advanced Python & Agent Design Patterns
   - 3.2 Visual Workflow Orchestration with n8n
   - 3.3 Large Language Model Integration & Fallbacks
   - 3.4 Relational & Document Data Persistence
   - 3.5 Interactive Dashboards & RESTful APIs
4. **Chapter 4: Project 1 — SalesFlow AI (n8n Automation Platform)**
   - 4.1 Problem Definition & Requirements Analysis
   - 4.2 System Architecture & State Machine Design
   - 4.3 Detailed Workflow Breakdown (50 Nodes Total)
     - 4.3.1 WF-01: Inbound Lead Capture & Instant AI Triage (9 Nodes)
     - 4.3.2 WF-02: AI Lead Scoring & 100-Point BANT Qualification (8 Nodes)
     - 4.3.3 WF-03: Dynamic Sales Rep Assignment & CRM Entry (8 Nodes)
     - 4.3.4 WF-04: Automated 5-Touch Follow-up Engine & Calendar Scheduler (8 Nodes)
     - 4.3.5 WF-05: AI Proposal Generation & HITL Token Approval (10 Nodes)
     - 4.3.6 WF-06: Sales Dashboard & Weekly Executive Analytics (7 Nodes)
   - 4.4 PostgreSQL Relational Schema & State Transitions
   - 4.5 Security, Error Handling & OAuth2 Integrations
   - 4.6 Verification & Live Workflow Simulation
5. **Chapter 5: Project 2 — SalesAI SDR (Autonomous Multi-Agent System)**
   - 5.1 Problem Statement & SDR Operational Challenges
   - 5.2 Multi-Agent Collaborative Architecture
   - 5.3 Specialized Agent Implementation (6 Agents)
     - 5.3.1 ProspectResearchAgent: Real-Time Web Intelligence
     - 5.3.2 LeadQualificationAgent: Mathematical BANT Scoring
     - 5.3.3 EmailWriterAgent: 5-Touch Cadence Copywriter & A/B Variants
     - 5.3.4 MeetingCoordinatorAgent: Agenda Generation & Calendar Invitations
     - 5.3.5 ObjectionHandlerAgent: Tactical Coaching & Sales Roleplay
     - 5.3.6 CRMManagerAgent: Pipeline Telemetry & Revenue Forecasting
   - 5.4 Live Tool Integrations & Persistence Layer
   - 5.5 Multi-Provider LLM Resilience (Gemini 2.0 Flash & Groq Fallback)
   - 5.6 Interactive Web UI (Gradio 6.30) & REST API (FastAPI)
6. **Chapter 6: Weekly Engineering Work Log**
   - 6.1 Weekly Task Breakdown (Weeks 1 to 8)
   - 6.2 Cumulative Milestones & Hours Summary
7. **Chapter 7: Technical Challenges, Problem Solving & Resolutions**
   - 7.1 Cross-Platform Unicode & Terminal Encoding
   - 7.2 LLM API Quota Limits & Multi-Provider Abstraction
   - 7.3 State Decoupling in Distributed n8n Workflows
   - 7.4 Human-in-the-Loop Asynchronous Execution Halting
8. **Chapter 8: Skills Developed & Professional Competencies**
   - 8.1 Technical Skills Matrix
   - 8.2 Software Engineering & Architectural Methodologies
9. **Chapter 9: System Verification, Testing & Evaluation**
   - 9.1 Automated Test Runner & Results
   - 9.2 Validation of Operational vs. Simulated Features
10. **Chapter 10: Conclusion & Future Scope**
    - 10.1 Concluding Summary
    - 10.2 Future Architectural Enhancements
11. **References & Academic Citations**
12. **Appendices: Setup Instructions, DDL Scripts & JSON Blueprints**

---

## Chapter 1: Introduction

### 1.1 Background & Industry Context
In contemporary B2B enterprise software and service organizations, the Sales Development Representative (SDR) function serves as the primary bridge between raw market interest and revenue generation. However, empirical studies reveal that SDR teams spend less than 35% of their working hours actively engaging prospects. Over 65% of their operational bandwidth is dissipated across administrative overhead, manual search engine research, subjective lead triage, fragmented CRM entry, and repetitive drafting of follow-up emails.

Furthermore, prospect responsiveness decays exponentially over time: leads engaged within 5 minutes are 21 times more likely to enter the sales qualification pipeline than those contacted after 30 minutes. When manual triage causes lead response latencies of 12 to 48 hours, enterprise sales pipelines suffer severe conversion drop-offs.

### 1.2 Purpose of the Internship
The Summer School 2026 Internship Program at the Indian Institute of Technology (IIT) Jammu was formulated to address these enterprise productivity bottlenecks by applying advanced concepts in **Autonomous Artificial Intelligence Agents**, **Large Language Model (LLM) Orchestration**, and **Visual Workflow Automation**.

The objective of the internship was to engineer, implement, verify, and document two distinct yet complementary capstone platforms:
1. An event-driven workflow automation architecture built on **n8n** that completely automates data movement, scoring, routing, and managerial oversight.
2. A Python-based multi-agent system combining specialized autonomous agents equipped with real-time web search tools, CRM persistence, and conversational sales roleplay.

### 1.3 Core Engineering Objectives
- **Event-Driven Orchestration:** Construct a resilient n8n automation pipeline across 6 production-grade workflows comprising 50 verified nodes.
- **Specialized Multi-Agent Swarm:** Design and implement 6 autonomous agents conforming to clean separation of concerns, structured JSON input/output schemas, and stateful memory.
- **Multi-Provider LLM Resilience:** Integrate Google Gemini 2.0 Flash as the primary inference engine with seamless fallback to Groq LLaMA-3.1, eliminating single-provider quota dependencies.
- **Persistent Data Modeling:** Architect a normalized relational database schema in PostgreSQL (for n8n workflows) and SQLite in WAL mode (for Python agents) to record lead dossiers, BANT matrices, and audit logs.
- **Human-in-the-Loop Governance:** Implement token-based gating mechanisms to ensure critical commercial decisions (such as proposal delivery) remain subject to explicit human managerial approval.
- **Production-Grade Interface:** Build an interactive, dark-themed dual-tab dashboard in Gradio 6.30 alongside a FastAPI REST service to facilitate comprehensive evaluation.

---

## Chapter 2: Internship Program Overview

### 2.1 Host Institution: IIT Jammu
The Indian Institute of Technology (IIT) Jammu is an Institute of National Importance established by the Government of India. Renowned for its cutting-edge engineering curriculum and advanced research centers, IIT Jammu provided state-of-the-art computational infrastructure, structured curriculum design, and expert mentorship for the Summer School 2026 program.

### 2.2 Program Specialization: AI Agents & Automation
The Summer School 2026 curriculum focused intensely on:
- Architectures for autonomous agentic reasoning (ReAct, plan-and-solve, multi-agent swarms).
- Function calling, tool use, and structured outputs with modern frontier LLMs.
- Enterprise integration patterns, REST APIs, Webhook event dispatching, and asynchronous queues.
- Visual workflow automation platforms, with an emphasis on n8n node development.
- Human-in-the-Loop (HITL) control patterns and safety guardrails.

### 2.3 Roles & Engineering Responsibilities
As a Capstone Software Engineering Intern, key responsibilities included:
- Formulating technical specification documents and sequence diagrams for enterprise sales flows.
- Developing and exporting 6 valid n8n workflow blueprints meeting rigorous node count criteria.
- Writing modular Python 3.12 agent classes adhering to object-oriented and functional principles.
- Implementing zero-cost external tool wrappers for real-time web scraping and local CRM operations.
- Constructing automated test suites to guarantee 100% error-free execution across all modules.

---

## Chapter 3: Technical Foundation & Learning Phase

### 3.1 Advanced Python & Agent Design Patterns
During the foundational phase of the internship, agent design patterns were explored. Key principles mastered included:
- **Single Responsibility Principle for Agents:** Ensuring that each agent encapsulates one domain (e.g., qualification vs. email drafting).
- **Structured JSON Contracts:** Enforcing deterministic JSON schemas through prompt instructions and robust regex-based extraction parsers to handle non-compliant LLM outputs.
- **Context Window Management:** Pruning agent conversational memory to preserve relevant lead details without exceeding token context limits.

### 3.2 Visual Workflow Orchestration with n8n
The n8n visual automation platform was studied as an enterprise alternative to monolithic codebases. Key concepts mastered included:
- Webhook node configuration for synchronous and asynchronous REST intake.
- Relational database nodes (PostgreSQL) for transactional record locking and status updates.
- JavaScript Code nodes for deterministic payload transformation and mathematical calculations.
- Flow control primitives: Switch nodes, IF nodes, SplitInBatches nodes, and asynchronous Wait nodes.

### 3.3 Large Language Model Integration & Fallbacks
Due to quota constraints on commercial proprietary APIs, an instructor-approved multi-provider architecture was implemented:
- **Google Gemini 2.0 Flash:** Serves as the primary provider, delivering sub-second token generation latency and large context window capability.
- **Groq LLaMA-3.1 (70B):** Serves as the high-speed open-weights fallback provider via the Groq Cloud LPUs.
- **Multi-Provider Client:** The custom `call_ai()` abstraction in `src/agents/base.py` automatically detects configured keys and manages provider failover.

---

## Chapter 4: Project 1 — SalesFlow AI (n8n Automation Platform)

### 4.1 Problem Definition & Requirements Analysis
B2B sales organizations managing inbound website traffic frequently experience:
1. Inbound leads sitting unattended for hours before SDR review.
2. Inconsistent qualification standards where reps pursue unviable prospects.
3. Reps cherry-picking inbound leads without fair workload distribution.
4. Abandoned follow-ups after 1 or 2 unanswered attempts.
5. Lack of executive visibility into pipeline velocity and conversion bottlenecks.

To fulfill Assignment 4 specifications, the platform was required to deliver 4 to 6 interconnected workflows containing at least 20 to 25 total nodes, integrating AI scoring, CRM storage, communication channels, and human approvals.

### 4.2 System Architecture & State Machine Design
SalesFlow AI implements an event-driven architecture where 6 independent workflows operate asynchronously across a shared PostgreSQL database state machine:

```
[Inbound Form] ──► (WF-01: Capture) ──► status: 'NEW' / 'SCORED'
                                               │
                                               ▼
[Webhook / DB] ──► (WF-02: BANT)    ──► status: 'QUALIFIED' or 'NURTURE'
                                               │
                                               ▼
[Webhook / DB] ──► (WF-03: Assign)  ──► status: 'ASSIGNED'
                                               │
                                               ▼
[8h Cron Job]  ──► (WF-04: Cadence) ──► status: 'ENGAGED' (5 Touches)
                                               │
                                               ▼
[Discovery]    ──► (WF-05: Proposal)──► status: 'PROPOSAL_SENT' (Post-HITL)
                                               │
                                               ▼
[Mon 8AM Cron] ──► (WF-06: Digest)  ──► Executive Briefing (Sheets + Slack)
```

### 4.3 Detailed Workflow Breakdown (50 Verified Nodes)

The implementation consists of **6 production-ready workflows with an exact total of 50 verified nodes**:

#### 4.3.1 WF-01: Inbound Lead Capture & Instant AI Triage (`01_lead_capture_registration.json`)
- **Node Count:** 9 nodes
- **Trigger:** Webhook `POST /capture-lead`
- **Functional Description:** Ingests raw lead submissions from web forms. Normalizes company and phone attributes, invokes GPT-4o to generate an initial 1–100 lead score, saves the record to the PostgreSQL `leads` table, delivers an automated welcome email via Gmail OAuth2, and checks if the score exceeds 80 to fire an instant Slack alert to `#hot-leads-alert`.
- **Node Pipeline:** `Webhook` → `Code (Normalize)` → `OpenAI (GPT-4o Scoring)` → `Code (Parse AI Score)` → `PostgreSQL (Insert Lead)` → `Gmail (Welcome Email)` → `IF (Hot Lead?)` → `Slack (Hot Alert)` → `Respond to Webhook`.

#### 4.3.2 WF-02: AI Lead Scoring & 100-Point BANT Qualification (`02_ai_lead_scoring_qualification.json`)
- **Node Count:** 8 nodes
- **Trigger:** Webhook `POST /qualify-lead`
- **Functional Description:** Fetches lead background and queries GPT-4o using a strict 100-point BANT evaluation prompt:
  - *Budget (25 pts):* Financial allocation vs. product pricing.
  - *Authority (25 pts):* Title evaluation (C-Level, VP, Director).
  - *Need (25 pts):* Pain point severity and business alignment.
  - *Timeline (25 pts):* Purchase horizon (<30 days vs. exploratory).
  Updates lead qualification status in PostgreSQL. Leads scoring $\ge 70$ are routed as Sales Qualified; leads scoring $< 70$ are appended to Google Sheets for automated long-term nurturing.
- **Node Pipeline:** `Webhook` → `PostgreSQL (Fetch Lead)` → `OpenAI (BANT Evaluation)` → `Code (Compute BANT)` → `PostgreSQL (Update Status)` → `Switch (Score Router)` → `Google Sheets (Log Nurture)` → `Respond to Webhook`.

#### 4.3.3 WF-03: Dynamic Sales Rep Assignment & CRM Entry (`03_sales_rep_assignment_crm.json`)
- **Node Count:** 8 nodes
- **Trigger:** Webhook `POST /assign-rep`
- **Functional Description:** Fetches active sales reps and their current active deal counts from PostgreSQL. Calculates a weighted matching score combining domain expertise (matching lead industry to rep specialty) and current workload balancing. Assigns the winning rep, updates PostgreSQL, drafts a personalized internal sales dossier for the rep, emails the rep via Gmail, and broadcasts the assignment to Slack `#sales-assignments`.
- **Node Pipeline:** `Webhook` → `PostgreSQL (Fetch Reps)` → `Code (Smart Matching)` → `PostgreSQL (Assign Rep)` → `OpenAI (Rep Dossier)` → `Gmail (Email Rep)` → `Slack (Post Assignment)` → `Respond to Webhook`.

#### 4.3.4 WF-04: Automated 5-Touch Follow-up Engine & Calendar Scheduler (`04_automated_followup_meeting_scheduler.json`)
- **Node Count:** 8 nodes
- **Trigger:** Cron Schedule (Every 8 hours)
- **Functional Description:** Queries PostgreSQL for leads where elapsed hours since last contact exceed 48 hours and total touches are less than 5. Splits leads in batches. For each lead, GPT-4o crafts a contextual follow-up email matching the specific touch stage (Touch 1: Executive Value; Touch 2: Metric Proof; Touch 3: Tech Architecture; Touch 4: Re-engagement; Touch 5: Breakup). Automatically reserves a provisional discovery meeting hold on Google Calendar upon Touch 1, and logs each touchpoint to the `follow_ups` audit table.
- **Node Pipeline:** `Schedule Trigger (8h)` → `PostgreSQL (Query Leads)` → `Split In Batches` → `OpenAI (Draft Touch Copy)` → `Gmail (Send Follow-up)` → `Google Calendar (Create Hold)` → `PostgreSQL (Log Follow-up)` → `Code (Update Touch Count)`.

#### 4.3.5 WF-05: AI Proposal Generation & HITL Token Approval (`05_proposal_generation_human_approval.json`)
- **Node Count:** 10 nodes
- **Trigger:** Webhook `POST /generate-proposal`
- **Functional Description:** Fetches deal financials and customer requirements. Invokes GPT-4o to construct a complete responsive HTML proposal containing three tiered pricing packages. Saves the proposal asset to Google Drive and emails an approval request to the Sales VP containing unique `Approve` and `Reject` callback URL tokens. The **n8n Wait Node** pauses the workflow execution. Upon receipt of manager token callback: if approved, the proposal is automatically delivered to the client via Gmail and status updated to `PROPOSAL_SENT`; if rejected, feedback is logged for rep revision.
- **Node Pipeline:** `Webhook` → `PostgreSQL (Fetch Deal)` → `OpenAI (Render HTML Proposal)` → `Google Drive (Save File)` → `Gmail (Send VP Approval Request)` → `Wait Node (Await Callback)` → `IF (Approved?)` → `Gmail (Deliver to Client)` → `PostgreSQL (Update Deal Status)` → `Respond to Webhook`.

#### 4.3.6 WF-06: Sales Dashboard & Weekly Executive Analytics (`06_sales_dashboard_analytics_report.json`)
- **Node Count:** 7 nodes
- **Trigger:** Cron Schedule (Every Monday at 08:00 AM)
- **Functional Description:** Performs SQL aggregation across the preceding 7 days of sales data in PostgreSQL: total leads captured, qualification conversion rate, rep win-rate leaderboard, and total weighted pipeline value. GPT-4o synthesizes these raw metrics into a concise executive sales narrative. Appends the weekly summary row to a Google Sheets KPI dashboard, delivers the executive HTML report via Gmail, and posts the summary to Slack `#sales-leadership`.
- **Node Pipeline:** `Schedule Trigger (Mon 8AM)` → `PostgreSQL (Aggregate 7-Day KPIs)` → `OpenAI (Synthesize Briefing)` → `Google Sheets (Append KPI Row)` → `Gmail (Send Executive Email)` → `Slack (Post to Leadership)` → `Code (Log Execution)`.

### 4.4 PostgreSQL Relational Schema & State Transitions
The PostgreSQL database schema underpinning the n8n workflows consists of three normalized tables:
- **`leads`:** Primary key `id`, unique `lead_id`, contact details, company attributes, `bant_score`, `lead_temperature`, `priority_tier`, `assigned_rep`, and current pipeline `status`.
- **`sales_reps`:** Primary key `id`, unique `rep_id`, contact details, `tier_level`, `industry_specialties`, `performance_score`, and active flag.
- **`follow_ups`:** Primary key `id`, foreign key `lead_id`, `followup_number`, communication channel, and dispatch timestamp.

---

## Chapter 5: Project 2 — SalesAI SDR (Autonomous Multi-Agent System)

### 5.1 Problem Statement & SDR Operational Challenges
While workflow automation platforms excel at structured data routing, modern sales development requires deep contextual intelligence: researching prospect web presence, evaluating nuanced qualification criteria, handling objections in real time, and scheduling discovery calls. 

Project 2 solves this by implementing an autonomous multi-agent swarm architecture where 6 specialized AI agents coordinate the sales development lifecycle.

### 5.2 Multi-Agent Collaborative Architecture
The multi-agent system adopts a modular design centered around the `BaseAgent` class, which manages system prompts, multi-turn memory, and tool invocation:

```
[Inbound Prospect Details]
            │
            ▼
┌────────────────────────────────────────┐
│ 1. ProspectResearchAgent               │ ◄── DuckDuckGo / Wikipedia Scraper
│    - Web Scraping & Pain Points        │
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│ 2. LeadQualificationAgent              │
│    - 100-Point BANT Scoring Matrix     │
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│ 3. EmailWriterAgent                    │
│    - 5-Touch Cadence & A/B Variants    │
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│ 4. MeetingCoordinatorAgent             │ ◄── Discovery Agenda & Calendar ICS
│    - Agenda Design & Booking Links     │
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│ 5. ObjectionHandlerAgent               │ ◄── Interactive Roleplay & Coaching
│    - 3-Step Objection Reframing        │
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│ 6. CRMManagerAgent                     │ ◄── SQLite Database (salesai.db)
│    - Dossier Logging & Forecasting     │
└────────────────────────────────────────┘
```

### 5.3 Specialized Agent Implementation (6 Agents)

1. **ProspectResearchAgent (`prospect_research_agent.py`):**
   - Integrates live web search via DuckDuckGo and Wikipedia (zero API cost).
   - Scrapes company overview, estimated employee count, business model, and recent news.
   - Extracts specific operational pain points and formulates personalized opening hooks.
2. **LeadQualificationAgent (`lead_qualification_agent.py`):**
   - Evaluates lead details against a structured 100-point BANT matrix (Budget, Authority, Need, Timeline; 25 points each).
   - Categorizes temperature into Hot ($\ge 75$), Warm ($50–74$), or Cold ($<50$).
   - Predicts deal size tier ($1,000–$50,000+) and estimated win probability percentage.
3. **EmailWriterAgent (`email_writer_agent.py`):**
   - Generates hyper-personalized cold outreach copy referencing the specific research hooks.
   - Outputs dual subject lines (Subject Line A for curiosity, Subject Line B for direct value) for A/B testing.
   - Produces a companion 300-character LinkedIn InMail message.
4. **MeetingCoordinatorAgent (`meeting_coordinator_agent.py`):**
   - Formulates tailored discovery meeting agendas matching the prospect's industry.
   - Suggests optimal meeting times across upcoming business days.
   - Generates RFC-5545 compliant `.ics` calendar invite files and Calendly booking links.
5. **ObjectionHandlerAgent (`objection_crm_agents.py`):**
   - Powers the interactive conversational interface in both terminal and web UI.
   - Employs a 3-step objection reframing method: *Acknowledge → Reframe Value → Ask Open-Ended Question*.
   - Features an interactive **Sales Roleplay Mode** where the agent acts as a skeptical VP of Sales to train human reps.
6. **CRMManagerAgent (`crm_manager_agent.py`):**
   - Manages persistence to the local SQLite database (`salesai.db`).
   - Computes weighted pipeline revenue values ($W = \sum \text{Deal Size} \times P_{\text{win}}$).
   - Maintains an immutable audit log of all agent executions and latencies.

### 5.4 Live Tool Integrations & Persistence Layer
- **Live Web Research (`web_research.py`):** Wraps DuckDuckGo HTML scraping and Wikipedia REST API to enrich lead data dynamically without requiring external API keys.
- **SQLite CRM Database (`crm_database.py`):** Implements tables for `leads`, `qualifications`, `outreach_emails`, and `activity_logs`. Configured in Write-Ahead Logging (WAL) mode for concurrent access.
- **Email Sender (`email_sender.py`):** Delivers live emails via SMTP when credentials are supplied in `.env`, or operates safely in simulated logging mode to prevent unauthorized dispatches during testing.

### 5.5 Multi-Provider LLM Resilience
To guarantee system operation in the absence of an OpenAI API quota, the multi-agent system uses Google Gemini 2.0 Flash as its primary LLM provider and Groq LLaMA-3.1 as an ultra-fast fallback provider. The `call_ai()` gateway handles timeout management, backoff retries, and markdown code block stripping to ensure 100% valid JSON returns.

### 5.6 Interactive Web UI (Gradio 6.30) & REST API (FastAPI)
- **Gradio Dual-Tab Dashboard (`gradio_app.py`):** Features Tab 1 (SalesFlow N8N Platform with interactive Live Workflow Simulator and JSON viewer) and Tab 2 (SalesAI Multi-Agent Swarm with single-lead pipeline runner, interactive chat, and live CRM telemetry).
- **FastAPI REST Backend (`api_server.py`):** Exposes OpenAPI endpoints (`/docs`), lead ingestion webhooks (`/webhook/n8n`), and health monitoring endpoints.

---

## Chapter 6: Weekly Engineering Work Log

| Week | Date Range | Core Activities & Tasks | Key Concepts & Frameworks | Hours Logged |
|:---:|:---:|---|---|:---:|
| **Week 1** | [Dates Week 1, e.g., 10–16 Jun 2026] | Program orientation, Python 3.12 environment setup, agent architecture design. | Multi-Agent Patterns, OOP | [36 hrs] |
| **Week 2** | [Dates Week 2, e.g., 17–23 Jun 2026] | n8n setup, REST Webhooks, PostgreSQL relational schema creation (`leads`, `sales_reps`). | Webhooks, PostgreSQL, DDL | [38 hrs] |
| **Week 3** | [Dates Week 3, e.g., 24–30 Jun 2026] | Built WF-01 (Lead Capture) and WF-02 (AI BANT Qualification) in n8n; verified node logic. | GPT-4o Prompting, Switch Nodes | [40 hrs] |
| **Week 4** | [Dates Week 4, e.g., 01–07 Jul 2026] | Built WF-03 (Rep Assignment) and WF-04 (Follow-up Cadence); integrated Google Calendar API. | Cron Triggers, Smart Matching | [40 hrs] |
| **Week 5** | [Dates Week 5, e.g., 08–14 Jul 2026] | Implemented WF-05 (HITL Proposal with Wait Node) and WF-06 (Weekly KPI Analytics). | Wait Nodes, HITL Governance | [38 hrs] |
| **Week 6** | [Dates Week 6, e.g., 15–21 Jul 2026] | Engineered Python agents (Research, Qualification, Email Writer); integrated Gemini/Groq LLM. | DuckDuckGo Scraping, BANT | [40 hrs] |
| **Week 7** | [Dates Week 7, e.g., 22–28 Jul 2026] | Added MeetingCoordinatorAgent, ObjectionHandlerAgent roleplay mode, and SQLite CRM. | SQLite WAL, Objection Coaching | [36 hrs] |
| **Week 8** | [Dates Week 8, e.g., 29 Jul–04 Aug 2026] | Built unified Gradio 6.30 dashboard, wrote comprehensive test suite, finalized report and slides. | Gradio Blocks, System Testing | [32 hrs] |
| **Total** | **8 Weeks** | **End-to-End Development of SalesFlow n8n & SalesAI SDR Systems** | **Full-Stack AI & Automation** | **[300 hrs]** |

*(Note: Date ranges and logged hours are formatted with clear brackets and can be adapted to match official institutional records.)*

---

## Chapter 7: Technical Challenges, Problem Solving & Resolutions

### 7.1 Cross-Platform Terminal Unicode Encoding
- **Challenge:** On Windows command-line environments, agent execution logs containing status emojis (🚀, 🔍, ✅) triggered `UnicodeEncodeError: 'charmap' codec can't encode character`.
- **Resolution:** Reconfigured standard output streams programmatically in `main.py` and `launch.py` using `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

### 7.2 API Quota Exhaustion & Provider Failover
- **Challenge:** Exhaustion of OpenAI API quotas halted development of proprietary SDK implementations.
- **Resolution:** Engineered a provider-agnostic LLM interface in `base.py` utilizing Google Gemini 2.0 Flash as the primary provider and Groq LLaMA-3.1 as an automatic fallback, operating at zero cost.

### 7.3 Inter-Workflow State Decoupling in n8n
- **Challenge:** Creating tightly coupled sub-workflow executions in n8n introduced brittle execution dependencies and single-point-of-failure vulnerabilities.
- **Resolution:** Decoupled all 6 workflows to communicate through shared PostgreSQL database state transitions (`NEW` $\to$ `SCORED` $\to$ `QUALIFIED` $\to$ `ASSIGNED` $\to$ `CONTACTED` $\to$ `PROPOSAL_SENT`) and REST Webhooks.

### 7.4 Asynchronous Human-in-the-Loop Pausing
- **Challenge:** Commercial proposals required manager sign-off without keeping HTTP client connections indefinitely open.
- **Resolution:** Implemented the n8n **Wait Node** in WF-05, safely freezing execution state and generating unique approval callback URLs embedded in managerial review emails.

---

## Chapter 8: Skills Developed & Professional Competencies

### 8.1 Technical Skills Matrix
- **Workflow Automation:** n8n workflow construction, Webhook triggers, Cron scheduling, Wait nodes, error handling.
- **Agentic AI Engineering:** Multi-agent swarms, BANT qualification logic, dynamic prompt engineering, structured JSON extraction.
- **LLM APIs:** Google Gemini 2.0 Flash, Groq LLaMA-3.1, function calling, fallback design.
- **Data Persistence:** PostgreSQL relational modeling, SQLite in WAL mode, database indexing, SQL aggregation.
- **Web Development & APIs:** Gradio 6.30 Blocks, FastAPI REST services, OpenAPI/Swagger documentation, HTML/CSS proposal rendering.

### 8.2 Software Engineering Best Practices
- **Security & Hygiene:** Comprehensive `.gitignore` configuration, zero credential leakage, environment variable isolation.
- **Testing & Verification:** Automated end-to-end verification scripts (`test_import.py`) ensuring zero runtime errors.
- **Documentation:** Architectural blueprints, sequence diagrams, and reproducible execution guides.

---

## Chapter 9: System Verification, Testing & Evaluation

### 9.1 Automated Test Runner & Results
The project includes a comprehensive verification suite in `test_import.py`. Execution validates all system components:
```
============================================================
SalesAI SDR - IIT Submission Test Runner
============================================================
[OK] Gradio 6.30.0 imported
[OK] base.py | Provider=gemini | Gemini=SET | Groq=SET
[OK] ProspectResearchAgent
[OK] LeadQualificationAgent
[OK] EmailWriterAgent
[OK] ObjectionHandlerAgent
[OK] CRMManagerAgent (crm_manager_agent.py)
[OK] MeetingCoordinatorAgent
[OK] crm_database
[OK] email_sender
[OK] web_research
[OK] Database initialized | Leads: 13
[OK] SMTP status: Simulated mode (add SMTP credentials to .env)
[OK] All 6 agents instantiated successfully
[OK] Tab 1: All 6 N8N Workflow JSONs validated (50 nodes total)
[OK] Tab 1: Live N8N Workflow Simulator tested successfully
[OK] FastAPI REST Backend verified
============================================================
RESULT: ALL TESTS PASSED - Ready for IIT submission!
```

### 9.2 Operational vs. Simulated Features
- **Working Local Features:** Real SQLite database operations, real Gemini/Groq LLM inference, real DuckDuckGo web scraping, interactive Gradio dual-tab interface, FastAPI REST server, and live workflow simulator.
- **Simulated Features:** Live SMTP email dispatch operates in safe simulated logging mode unless valid credentials are provided in `.env`. N8N workflows are validated as compliant JSON blueprints ready for self-hosted or cloud n8n deployment.

---

## Chapter 10: Conclusion & Future Scope

### 10.1 Concluding Summary
During the Summer School 2026 Internship at IIT Jammu, two enterprise-grade software platforms were designed, developed, and verified. **SalesFlow AI** automates complex B2B data flows across 6 n8n workflows totaling 50 nodes with strict Human-in-the-Loop oversight. **SalesAI SDR** coordinates 6 autonomous agents equipped with live web tools, mathematical BANT scoring, and persistent CRM tracking. Together, these systems demonstrate the transformative potential of combining visual workflow automation with autonomous multi-agent intelligence.

### 10.2 Future Architectural Enhancements
- Integration of enterprise CRM connectors (Salesforce REST API, HubSpot OAuth).
- Implementation of voice-agent capabilities using WebRTC and low-latency audio streaming for automated inbound qualification calls.
- Distributed workflow deployment via Docker Compose and Kubernetes for enterprise-scale throughput.

---

## References & Academic Citations
1. Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. John Wiley & Sons.
2. Yao, S., Zhao, J., Yu, D., et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. arXiv preprint arXiv:2210.03629.
3. n8n GmbH. (2026). *n8n Documentation: Advanced Node Workflows and Webhook Integrations*. https://docs.n8n.io/
4. Google DeepMind. (2026). *Gemini 2.0 Technical Documentation & API Specifications*. https://ai.google.dev/
5. Harvard Business Review. (2011). *The Short Life of Online Sales Leads*. https://hbr.org/2011/03/the-short-life-of-online-sales-leads

---

## Appendices

### Appendix A: System Verification Command
To verify the complete software installation and run all module checks:
```bash
python test_import.py
```

### Appendix B: Unified Dashboard Launch Command
To launch the interactive dual-tab Gradio interface:
```bash
python launch.py
```

### Appendix C: N8N Workflow Node Summary
- `01_lead_capture_registration.json`: 9 nodes
- `02_ai_lead_scoring_qualification.json`: 8 nodes
- `03_sales_rep_assignment_crm.json`: 8 nodes
- `04_automated_followup_meeting_scheduler.json`: 8 nodes
- `05_proposal_generation_human_approval.json`: 10 nodes
- `06_sales_dashboard_analytics_report.json`: 7 nodes
- **Total Verified Nodes:** 50 nodes
