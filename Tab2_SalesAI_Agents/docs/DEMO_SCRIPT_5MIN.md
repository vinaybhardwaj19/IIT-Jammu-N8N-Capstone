# 5-Minute Evaluation Demo Script — SalesAI SDR

**Presenter:** Vinay Bhardwaj  
**Duration:** 5 minutes

| Time | Demonstration |
|---|---|
| 0:00–0:45 | Introduce the six custom agent modules and their roles. |
| 0:45–2:00 | Show the dashboard and agent forms with synthetic example values; do not run a real web search or model call. |
| 2:00–3:15 | Show the objection-handler interface and explain that responses require configured provider inference. |
| 3:15–4:15 | Explain email simulation, meeting preparation, and local SQLite CRM behavior. |
| 4:15–5:00 | Run or describe the local smoke check and state the official SDK/live provider verification still required. |

## Spoken script

### Introduction
“SalesAI SDR organizes sales development tasks into six custom Python agent modules: prospect research, lead qualification, email drafting, meeting coordination, objection handling, and CRM management. They share a project-defined `BaseAgent` framework and use local tools, a SQLite CRM, a FastAPI backend, and a Gradio interface. This implementation is not the official OpenAI Agents SDK.”

### Dashboard and agents
“The dashboard exposes the project’s agent workflows. Prospect research can use configured web tools, and model-backed agents depend on provider credentials, quota, and network access. The local smoke suite checks imports and setup; it does not make model calls. I’ll use synthetic example fields for this review.”

### Safe actions
“Email output is handled through a safe simulation path during local checks. Meeting coordination prepares content, while live calendar actions require separate credentials and testing. CRM operations shown here use the local SQLite database; no external CRM synchronization is configured.”

### Verification and close
“Local verification covers the smoke suite, local database behavior, and project setup. It does not establish response quality, latency, cost, or a complete live-provider pipeline. Before submission, I will confirm whether the course requires the official OpenAI Agents SDK, and I will only demonstrate provider-backed behavior with approved credentials and synthetic data.”
