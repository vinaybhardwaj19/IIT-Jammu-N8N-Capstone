# 🚀 SalesAI SDR — Multi-Agent Sales Intelligence System
### IIT Summer School 2026 | Capstone Project | Vinay Bhardwaj

---

## ⚠️ IMPORTANT — Submission Entry Point

> **The complete capstone submission is in the `salesai-sdr/` directory.**  
> `Tab2_SalesAI_Agents/` is an earlier prototype — evaluate `salesai-sdr/` only.

---

## 🏗️ Project Architecture

```
IIT PROJECT 1/
├── salesai-sdr/          ← ✅ PRIMARY SUBMISSION (Full 6-Agent System)
│   ├── agents/           ← 6 specialized OpenAI Agents SDK agents
│   ├── tools/            ← 6 callable tools (Email, Calendar, CRM, Web, DB)
│   ├── database/         ← SQLite CRM + Audit + Approval persistence layer
│   ├── memory/           ← SQLiteSession multi-turn memory manager
│   ├── models/           ← Pydantic structured output schemas
│   ├── api/              ← FastAPI REST API with /docs
│   ├── frontend/         ← Premium dark-mode web dashboard
│   ├── tests/            ← 12 IIT capstone unit & integration tests
│   └── main.py           ← Entry point (see usage below)
│
├── Tab1_SalesFlow_N8N/   ← N8N automation workflows (Tab 1)
│   └── workflows/        ← 6 JSON workflow files
│
└── Tab2_SalesAI_Agents/  ← Earlier 5-agent prototype (reference only)
```

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
cd salesai-sdr
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `salesai-sdr/.env`:
```env
MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=production

# Optional: For live email dispatch after Human Approval Gate
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 3. Run All 4 Capstone Demonstration Scenarios
```bash
cd salesai-sdr
python main.py --demo
```
This runs all 4 IIT required scenarios:
- Scenario 1: Full 6-Agent Swarm (Plan → Act → Evaluate)
- Scenario 2: Multi-Turn SQLiteSession Memory
- Scenario 3: Controlled Failure Recovery & Graceful Degradation
- Scenario 4: Human Approval Gate (Approve vs Reject)

### 4. Launch Web Dashboard & REST API
```bash
python main.py
# Opens http://127.0.0.1:8000 automatically
# API docs: http://127.0.0.1:8000/docs
```

### 5. Interactive CLI Mode
```bash
python main.py --cli
```

### 6. Run Full Test Suite (13 Tests)
```bash
python main.py --test
```

---

## 🤖 6-Agent Swarm Architecture

```
SDROrchestratorAgent
       │
       ▼ HANDOFF
ProspectResearchAgent (WebResearchTool)
       │
       ▼ HANDOFF
CompanyIntelligenceAgent (CompanyIntelligenceTool)
       │
       ▼ HANDOFF
LeadQualificationAgent (BANT Scoring, Pydantic Output)
       │
       ▼ HANDOFF
EmailWriterAgent (EmailTool, A/B Testing, HTML)
       │
       ▼ HANDOFF
OutreachEvaluatorAgent (8-point Reflection Rubric)
       │
       ▼ [HUMAN APPROVAL GATE] ← HOT leads require human sign-off
MeetingCoordinatorAgent (CalendarTool)
       │
       ▼ HANDOFF
CRMManagerAgent (CRMTool + DatabaseTool → SQLite)
```

**AI Provider:** Google Gemini 2.5 Flash (primary) | Groq LLaMA-3.1-70b (fallback)  
**Verified Mode:** LIVE_AGENT_EXECUTION ✅

---

## 📋 IIT Capstone Rubric Coverage

| Criterion | Implementation | Status |
|-----------|---------------|--------|
| Multi-Agent Swarm | 6 specialized agents with explicit handoff chain | ✅ |
| Tool Calling | 6 tools (WebResearch, Email, Calendar, CRM, DB, Company Intel) | ✅ |
| Structured Output | Pydantic models for all agent outputs | ✅ |
| Multi-Turn Memory | SQLiteSession persist/load across turns | ✅ |
| Human-in-the-Loop | Approval gate before external email dispatch | ✅ |
| Plan→Act→Evaluate | Outreach Evaluator reflection loop | ✅ |
| Failure Recovery | Bounded retry + graceful degradation | ✅ |
| Real Database | SQLite CRM with full audit trail | ✅ |
| REST API | FastAPI with /docs swagger | ✅ |
| Unit Tests | 12 tests covering all IIT criteria | ✅ |

---

## 📦 Submission Contents

- `salesai-sdr/` — Complete production-ready multi-agent system
- `Tab1_SalesFlow_N8N/` — 6 N8N automation workflow JSON files
- `Vinay_Bhardwaj_IIT_Jammu_Final_Report.pdf` — Project report
- `Vinay_Bhardwaj_IIT_Capstone_Submission.zip` — Packaged submission

---

*Candidate: Vinay Bhardwaj | IIT Summer School 2026 | Contact: via email on file*
