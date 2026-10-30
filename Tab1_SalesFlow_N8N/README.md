# SalesFlow AI — n8n CRM and Sales Automation Capstone

IIT Jammu Summer School 2026 | Assignment 4

The repository contains six n8n workflow JSON exports with 56 nodes total, including one error-stop node per workflow. AI calls and read-only PostgreSQL queries retry up to three times. Side-effecting integrations do not retry automatically; failures route to the workflow's Stop and Error node and failed execution data is retained. A local Gradio dashboard displays the exports and provides a local JSON simulator. The simulator does not execute n8n nodes or contact external services.

## Workflow inventory

| Export | Purpose | Nodes |
|---|---|---:|
| `01_lead_capture_registration.json` | Lead registration | 10 |
| `02_ai_lead_scoring_qualification.json` | Qualification and score routing | 9 |
| `03_sales_rep_assignment_crm.json` | Representative assignment and CRM update | 9 |
| `04_automated_followup_meeting_scheduler.json` | Follow-up and meeting design | 9 |
| `05_proposal_generation_human_approval.json` | Proposal approval | 11 |
| `06_sales_dashboard_analytics_report.json` | Analytics/report design | 8 |
| **Total** |  | **56** |

The exports define integrations for AI, PostgreSQL, Gmail, Google Sheets, Google Calendar, Google Drive, and Slack. These are design/configuration nodes; they require working n8n credentials and sandbox execution to verify. The active n8n instance has no saved project credentials. WF-02 and WF-05 response-path fixes are present in source files but not synced to the active instance. WF-01's `/capture-lead` route conflicts with another active workflow.

## Local use

From the repository root:

```powershell
python launch.py --gradio-port 7890
```

Open `http://localhost:7890/`, select the n8n tab, and use **Local JSON Simulation** with synthetic example input. The simulator reads JSON exports and returns a local trace; it does not call AI providers, n8n, databases, email, Slack, or calendar services.

## Evaluation limits and next steps

Local checks validate JSON structure, node totals, connection targets, and simulator traces. They do not prove live integrations, business outcomes, response-time improvements, conversion uplift, or ROI. For a sandbox test, first sync the updated WF-02/WF-05 exports, resolve the duplicate route, configure test credentials, and use synthetic records.
