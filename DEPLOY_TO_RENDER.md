# 🌐 Deploying SalesFlow AI to Render (Global Cloud Deployment)

This project is fully configured and ready to run 24/7 globally on Render (or any cloud provider).

---

## ⚡ Option 1: Deploy to Render in 3 Minutes (Recommended)

### Step 1: Push your code to GitHub
Make sure your latest code is pushed to your GitHub repository:
```bash
git add .
git commit -m "Production ready: all 58 nodes running, live SMTP & unified ASGI server"
git push origin main
```

### Step 2: Open Render
1. Go to [https://dashboard.render.com/](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** (top right) and select **Web Service**.
3. Select your repository: **`IIT-Jammu-N8N-Capstone`**.

### Step 3: Configure Service
Fill in these exact settings:
- **Name:** `salesflow-ai-crm`
- **Region:** Any (e.g., Oregon or Frankfurt)
- **Branch:** `main`
- **Runtime:** `Python 3`
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `python app.py`
- **Plan:** Free

### Step 4: Environment Variables (Add under "Environment")
Render will automatically read `render.yaml`, but you can also verify these in the dashboard:
| Key | Value | Description |
|---|---|---|
| `ENVIRONMENT` | `production` | Production mode |
| `AI_PROVIDER` | `gemini` | High-load fallback + Gemini |
| `AI_HIGH_LOAD_FALLBACK` | `true` | Ensures zero crashes even with no API keys |
| `SMTP_HOST` | `smtp.ethereal.email` | Working TLS SMTP server |
| `SMTP_PORT` | `587` | TLS port |
| `SMTP_USER` | `s2apuxrhufdlx7ye@ethereal.email` | Verified active test user |
| `SMTP_PASSWORD` | `tChtVBH7cNEXWv2hCh` | Verified test password |
| `SMTP_FROM_NAME` | `SalesAI SDR \| SalesFlow CRM` | Sender branding |
| `GEMINI_API_KEY` | *(Optional)* | Your Google Gemini API key if you want live LLM calls |

### Step 5: Click "Create Web Service"
- Render will build and deploy the app in ~2 minutes.
- When done, your public URL will look like:
  `https://salesflow-ai-crm.onrender.com/`

---

## 🌍 Option 2: Run Globally Right Now From Your Terminal (Instant Public Link)

If you need a public URL immediately without waiting for Render:
```bash
python app.py --share
```
This generates a worldwide public link (e.g. `https://xxxx.gradio.live`) that works globally from any phone, laptop, or browser.

---

## 🔍 What Runs on Your Public Web Service

Once deployed, your single public URL serves everything:
1. **Interactive Dashboard:** `https://your-service.onrender.com/`
   - Workflow Blueprint Gallery (All 6 workflows / 58 nodes)
   - Live Workflow Runner (Safe Simulation & Live Webhook)
   - Centralized CRM Kanban & Deal Pipeline
   - Deterministic RevOps ROI Simulator
   - AI Sales Copilot (Research, BANT Qualification, Cadence, Meeting Scheduler, Objections)
   - Competitor Battlecards (RAG)
2. **REST API Swagger Documentation:** `https://your-service.onrender.com/docs`
3. **Live Webhook Receiver:** `https://your-service.onrender.com/webhook/n8n`
4. **Health Check Probe:** `https://your-service.onrender.com/health` (Returns HTTP 200)

