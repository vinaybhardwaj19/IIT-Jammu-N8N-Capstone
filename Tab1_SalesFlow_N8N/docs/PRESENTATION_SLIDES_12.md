# SalesFlow AI — 12-Slide Presentation Outline

**Course:** IIT Jammu Summer School 2026 — n8n capstone (Assignment 4)  
**Presenter:** Vinay Bhardwaj

### Slide 1 — Project overview
Six n8n workflow JSON exports for lead intake, qualification, assignment, follow-up, proposal approval, and analytics. Together they contain 56 nodes.

### Slide 2 — Problem and goals
Manual lead handling can make follow-up and CRM records inconsistent. This project explores a structured workflow for intake, qualification, routing, and manager review. These are design motivations; no business impact study has been conducted.

### Slide 3 — Solution design
The exports describe a sales workflow from lead capture through reporting. WF-02 includes score-based qualified and nurture branches. WF-05 includes a human approval step before proposal delivery.

### Slide 4 — Architecture and stack
- n8n workflow exports (56 nodes across six files)
- Integration nodes for AI, PostgreSQL, Gmail, Google Sheets, Calendar, Drive, and Slack
- A local Gradio dashboard with workflow gallery and local JSON simulator
- Live execution requires an n8n instance, credentials, and route validation

### Slides 5–10 — Workflow inventory
1. WF-01: lead capture and registration (9 nodes)
2. WF-02: AI lead scoring and qualification (8 nodes)
3. WF-03: representative assignment and CRM update (8 nodes)
4. WF-04: follow-up and meeting scheduler (8 nodes)
5. WF-05: proposal generation and human approval (10 nodes)
6. WF-06: sales dashboard analytics and report (7 nodes)

The JSON exports define integration steps. Local simulation reads the JSON and records a trace; it does not execute n8n nodes or contact external services.

### Slide 11 — Verification and evidence limits
Local checks validate workflow JSON, node counts, connection targets, simulator traces, and the project smoke suite. The WF-02 nurture and WF-05 approved response paths are present in the source exports. Those changes are not synced to the active n8n instance. No live SaaS run or before-and-after sales metrics are verified.

### Slide 12 — Deliverables and next steps
Use `python test_import.py` for local checks and `python launch.py --gradio-port 7890` to open the dashboard. Before a sandbox run, sync the current exports, resolve the duplicate `/capture-lead` route, configure sandbox credentials, and use synthetic records. Demo recording and remaining candidate-specific report fields need completion.


The six exports now include retry settings (three attempts) and a Stop and Error branch for integration failures; live behavior still requires sandbox validation.
