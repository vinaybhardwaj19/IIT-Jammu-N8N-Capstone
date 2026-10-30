# SalesAI SDR — 12-Slide Presentation Outline

**Course:** IIT Jammu Summer School 2026 — AI agents capstone (Assignment 2)  
**Presenter:** Vinay Bhardwaj

### Slide 1 — Project overview
SalesAI SDR is a six-specialist sales development prototype built with the official OpenAI Agents SDK, a local SQLite CRM, FastAPI, and Gradio.

### Slide 2 — Problem and goals
Sales development work combines research, qualification, drafting, meeting preparation, objection coaching, and CRM updates. The project explores assistive automation for those tasks. No measured productivity or revenue improvement is claimed.

### Slide 3 — Agent architecture
ProspectResearchAgent → LeadQualificationAgent → EmailWriterAgent → MeetingCoordinatorAgent → CRMManagerAgent, with SDK handoff edges between specialists. ObjectionHandlerAgent can delegate to qualification, email, or CRM specialists. The pipeline adapter still calls stages in order; a handoff is model-selected.

### Slide 4 — Technology
Python, OpenAI Agents SDK (`openai-agents`), Pydantic output envelope, Gradio, FastAPI, SQLite, and local web/CRM/email/meeting tools. Model-backed agent runs require `OPENAI_API_KEY` and the configured `OPENAI_AGENT_MODEL`.

### Slides 5–9 — Agent responsibilities
- Prospect research can use the configured web enrichment tool; verify findings before outreach.
- Qualification organizes Budget, Authority, Need, and Timeline inputs; scores are model output, not calibrated predictions.
- EmailWriterAgent drafts outreach; its SDK send tool pauses for human approval.
- MeetingCoordinatorAgent prepares meeting content; no calendar booking is configured.
- ObjectionHandlerAgent provides coaching and roleplay; CRMManagerAgent reads/writes local SQLite data.

### Slide 10 — Dashboard and safe demonstration
The Gradio dashboard contains agent interfaces and a local n8n JSON simulator. The simulator does not execute external integrations or modify n8n.

### Slide 11 — Verification scope
The implementation was changed after the previous audit. No tests, model calls, email sends, calendar bookings, or live n8n executions were run during this migration. The full live pipeline remains unverified.

### Slide 12 — Deliverables and next steps
Configure an OpenAI key and use synthetic data for a model-backed demo. Keep email review enabled, do not claim calendar booking, and test n8n exports only in a sandbox with dedicated credentials. Record a demo video separately; one was not found in the project files.
