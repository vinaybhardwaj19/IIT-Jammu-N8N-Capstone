# SalesAI SDR — OpenAI Agents SDK capstone

IIT Jammu Summer School 2026 | Assignment 2: AI Sales Development Representative

SalesAI SDR contains six specialists implemented with the official OpenAI Agents SDK. Each specialist is an `Agent` run by `Runner`, returns a Pydantic-validated output envelope, and has narrowly scoped local tools. SDK handoffs connect research → qualification → email drafting → meeting preparation → CRM; objection handling can hand off to qualification, email, or CRM specialists. Legacy `run(dict) -> dict` interfaces remain for the Gradio and FastAPI applications.

## Agents and tools

| Agent | Responsibility | SDK tools |
|---|---|---|
| `ProspectResearchAgent` | Prospect/company context | Web enrichment |
| `LeadQualificationAgent` | BANT and ICP assessment | CRM lead lookup |
| `EmailWriterAgent` | Draft outreach | Approval-gated email send |
| `MeetingCoordinatorAgent` | Meeting package and agenda | Meeting preparation (draft only) |
| `ObjectionHandlerAgent` | Objection responses and roleplay | CRM lead lookup |
| `CRMManagerAgent` | Local CRM reads and writes | SQLite lookup/upsert |

The email send tool is decorated with `needs_approval=True`. An SDK run pauses on that tool until a human approves its interruption. The existing API/UI send option also defaults off. Meeting preparation does not book a calendar event; no calendar provider is configured.

## Run locally

Install dependencies and configure an OpenAI API key in the environment:

```powershell
cd Tab2_SalesAI_Agents
pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-key"
$env:OPENAI_AGENT_MODEL = "gpt-4.1-mini"
python main.py --pipeline
```

For the combined Gradio dashboard, configure the same environment in the project root and run:

```powershell
python launch.py --gradio-port 7890
```

Model-backed runs call the configured OpenAI model and may incur API usage. Use synthetic lead data. Tools that access the web, write SQLite records, or send email run only when invoked by an agent; sending is approval-gated.

## Data and safety boundaries

- Local CRM data is stored in SQLite (`salesai.db`); foreign key enforcement is enabled on each connection.
- Web research uses the existing enrichment utility and requires network access when invoked.
- Calendar booking is not configured; meeting output is a draft.
- Email delivery requires SMTP configuration and human approval through the SDK tool or an explicit UI/API send action.
- The local n8n JSON simulator does not execute exported workflows or contact external services.

The project retains Gemini/Groq helper code for non-agent utilities and compatibility, but the six capstone agents run through the OpenAI Agents SDK and require `OPENAI_API_KEY`.
