# 5-Minute Evaluation Demo Script — SalesFlow AI

**Presenter:** Vinay Bhardwaj  
**Duration:** 5 minutes

| Time | Demonstration |
|---|---|
| 0:00–0:45 | State the project goal and explain the six workflow exports. |
| 0:45–2:00 | Open the workflow gallery and show node connections for WF-01 and WF-02. |
| 2:00–3:15 | Run the local JSON simulation with a synthetic `@example.com` lead; explain that it produces a trace without calling n8n or SaaS services. |
| 3:15–4:15 | Show the WF-05 approval design and its response branches in the exported JSON. Clarify that live approval delivery has not been exercised. |
| 4:15–5:00 | Show the six-workflow inventory, local verification scope, and sandbox steps still needed. |

## Spoken script

### Introduction
“SalesFlow AI is my n8n sales automation capstone. The repository contains six workflow JSON exports with 56 nodes, covering lead capture, qualification, assignment, follow-up, proposal approval, and analytics. The exports describe integrations such as PostgreSQL, Gmail, Google Sheets, Calendar, Drive, and Slack. Live services require n8n credentials and sandbox testing.”

### Workflow design
“WF-01 defines lead capture and registration. WF-02 applies score-based qualification and has qualified and nurture branches. The nurture branch now returns through the webhook response in the source export. WF-03 describes representative assignment, and WF-04 describes scheduled follow-up and meeting steps. These are workflow definitions; the local simulator does not execute their external nodes.”

### Human review and analytics
“WF-05 includes a wait and approval design before proposal delivery. Both approval outcomes have response paths in the source JSON. WF-06 defines scheduled analytics and report integrations. These workflows have not been run against live services in this verification.”

### Local demonstration and close
“I’ll run the local JSON simulation using synthetic input. The dashboard displays the workflow structure and a node trace without sending email or changing an external CRM. Local checks cover the JSON files, connection targets, simulator, and project smoke suite. Before a live sandbox evaluation, the updated exports must be synced, the duplicate `/capture-lead` route resolved, and sandbox credentials configured. No measured ROI or conversion improvement is being claimed.”


The six exports now include retry settings (three attempts) and a Stop and Error branch for integration failures; live behavior still requires sandbox validation.
