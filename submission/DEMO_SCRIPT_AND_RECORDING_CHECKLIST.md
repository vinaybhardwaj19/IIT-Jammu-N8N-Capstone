# Demo Scripts and Recording Checklist

IIT Jammu Summer School 2026 | SalesFlow n8n and SalesAI SDR capstones

**Recording status:** No video is included yet. Vinay must record and submit a genuine 5–10 minute demonstration.

## Prepare the local demo

Open PowerShell at `C:\Users\HP\Downloads\IIT PROJECT 1`:

```powershell
python test_import.py
python launch.py --gradio-port 7890
```

Open `http://localhost:7890/`. Use synthetic values only, such as `Example Company`, `Synthetic Contact`, and `contact@example.com`. Do not use a real prospect. Do not click any model-backed research/pipeline actions unless a provider is deliberately configured and its quota/cost is acceptable. Do not enable SMTP or live n8n execution. The local JSON simulator does not call external services.

For project-specific scripts, see:

- `Tab1_SalesFlow_N8N/docs/DEMO_SCRIPT_5MIN.md`
- `Tab2_SalesAI_Agents/docs/DEMO_SCRIPT_5MIN.md`

The FastAPI backend may be shown at `http://localhost:8000/docs` if it is running. The Gradio launcher port is explicitly set to 7890 above.

## Combined 7-minute presentation script

### 0:00–1:00 — Introduction
“Today I’m presenting two IIT Jammu capstone projects: SalesFlow AI, six n8n workflow exports with 50 nodes, and SalesAI SDR, six custom Python agent modules. The first project focuses on sales workflow automation; the second organizes SDR tasks into custom agents. Local checks demonstrate project structure and safe simulation. They do not establish live SaaS behavior or measured business outcomes.”

### 1:00–3:30 — SalesFlow n8n project
Show the workflow gallery. Walk through WF-01 lead capture, WF-02 qualification, WF-03 assignment, WF-04 follow-up, WF-05 proposal approval, and WF-06 analytics. The JSON files define integration nodes for AI, PostgreSQL, Gmail, Sheets, Calendar, Drive, and Slack. Explain that n8n credentials are not configured and WF-02/WF-05 source changes are not synced into the active instance. Run only “Local JSON Simulation” using a synthetic lead. It renders a trace from the JSON and makes no external calls. Mention the duplicate `/capture-lead` path must be resolved before sandbox execution.

### 3:30–6:00 — SalesAI SDR project
Show the Gradio agent forms and the local CRM/dashboard. Describe the six custom Python modules and sequential context passing in the CLI orchestrator. Explain that provider-backed inference is not covered by the local smoke test. Show objection handling with synthetic example context; avoid presenting a response as a verified live model result unless you deliberately run a provider call and disclose that. Email dispatch uses a safe simulation in local checks; meeting actions and external CRM synchronization are not verified. The current implementation uses a custom `BaseAgent`, not the official OpenAI Agents SDK.

### 6:00–7:00 — Verification and close
Show `python test_import.py` output and point to the reviewed presentations in `submission/verified/`. State remaining work: confirm/implement the official SDK requirement, sandbox-sync and verify n8n if live execution is required, record the demo video, and complete candidate-specific report fields. Do not claim production deployment, ROI, conversion improvements, response-time savings, or live integrations.

## Recording checklist

- [ ] Run the local smoke check and confirm `LOCAL VERIFICATION PASSED`.
- [ ] Start Gradio on port 7890 and open the local dashboard.
- [ ] Use only synthetic example values; hide terminal/API-key fields from the recording.
- [ ] Show the n8n local JSON simulator, not live execution.
- [ ] Record a genuine 5–10 minute video with clear narration.
- [ ] Save the video and add its link to the submission portal.
