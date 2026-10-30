# 🚀 Step-by-Step GitHub Publishing Guide
### IIT Jammu Summer School 2026 | Capstone Submission
**Project:** SalesFlow AI (n8n) & SalesAI SDR (AI Agents)  
**Candidate:** Vinay Bhardwaj

---

> [!IMPORTANT]
> **Privacy & Credential Safety Notice:**  
> A dedicated `.gitignore` has been created in your project root. It **strictly excludes** your `.env` file, virtual environments (`.venv`), temporary databases, and caches so **no API keys will ever be uploaded to GitHub**.
> 
> *As per your instructions, this project has NOT been pushed or published automatically. Follow the exact steps below when you are ready to upload it.*

---

## 🛠️ Prerequisites
1. Ensure Git is installed on your computer. (Verify in terminal: `git --version`).
2. Log into your GitHub account: [https://github.com/](https://github.com/)

---

## 📋 Step 1: Create a New Repository on GitHub

1. Go to [https://github.com/new](https://github.com/new).
2. **Repository Name:** Enter a clean name, for example:
   - `IIT-Jammu-SalesAI-Capstone-2026` or `salesflow-ai-sdr-capstone`
3. **Description:** Enter:
   - `IIT Jammu Summer School 2026 Capstone: N8N SalesFlow Automation (50 Nodes) & Multi-Agent SalesAI SDR`
4. **Visibility:**
   - Choose **Public** (recommended if your instructor/evaluator requires public inspection).
   - Or choose **Private** (if your instructor provided a specific GitHub username to invite as a collaborator).
5. **Initialize this repository with:**
   - ⚠️ **DO NOT** check "Add a README file"
   - ⚠️ **DO NOT** check "Add .gitignore"
   - ⚠️ **DO NOT** choose a license  
   *(Leave all boxes unchecked since we already have these files prepared locally).*
6. Click **"Create repository"**.
7. Copy your repository URL (e.g., `https://github.com/<your-username>/IIT-Jammu-SalesAI-Capstone-2026.git`).

---

## 💻 Step 2: Initialize Git and Commit Locally

Open **PowerShell** or **Command Prompt** in your project folder:
```powershell
cd "C:\Users\HP\Downloads\IIT PROJECT 1"
```

### 1. Initialize Local Git Repository
```powershell
git init
```

### 2. Verify `.gitignore` is Protecting Your Secrets
Check which files Git sees before adding anything:
```powershell
git status
```
> [!NOTE]
> Make sure `.env` does **NOT** appear in the list of untracked files. Only `.env.example` should appear.

### 3. Stage All Project Files
```powershell
git add .
```

### 4. Create Your Initial Commit
```powershell
git commit -m "feat: IIT Jammu Summer School 2026 Capstone — SalesFlow n8n & SalesAI SDR"
```

---

## 🌐 Step 3: Link and Push to GitHub

Run these commands in PowerShell (replace `<your-username>` and `<repo-name>` with your actual URL):

```powershell
# 1. Rename branch to main
git branch -M main

# 2. Add your GitHub remote URL
git remote add origin https://github.com/<your-username>/<repo-name>.git

# 3. Push to GitHub
git push -u origin main
```

---

## 🔒 Step 4: Verification After Pushing

1. Open your GitHub repository URL in your web browser.
2. Confirm the following:
   - Root `README.md` renders cleanly with architecture diagrams.
   - `submission/` folder contains your presentations, Word report, and demo checklist.
   - `.env` is **NOT** visible anywhere on GitHub.
   - `.env.example` is visible with safe placeholders (`your-gemini-api-key-here`).

---

## 🔗 Step 5: How Evaluators Can Test Your Project

In your submission portal, provide your GitHub repository link and instructions:
```markdown
### Evaluation Instructions for Evaluators:
1. Clone repository:
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>

2. Install dependencies:
   pip install -r requirements.txt

3. Set free Gemini API key (or use pre-configured .env):
   cp .env.example .env
   # Add Gemini key to .env

4. Run automated test suite:
   python test_import.py

5. Launch interactive web dashboard:
   python launch.py
   # Opens at http://localhost:7860
```
