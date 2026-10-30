# Step-by-Step Instructions for Other AIs & IDEs
## How to Run, Extend, or Troubleshoot SalesAI SDR
**Document Purpose**: Clear, fail-safe, step-by-step instructions for future AI assistants (Gemini Flash 3.7, Claude, OpenAI Codex, Cursor, Android Studio Bot, etc.) and human developers when interacting with this repository.

---

## 1. Quick Summary of the Project

* **Project Root**: `C:\Users\HP\Downloads\IIT PROJECT 1\Tab2_SalesAI_Agents\`
* **Entry Point**: `main.py`
* **Core Agent Modules**: `src/agents/base.py`, `src/agents/prospect_research_agent.py`, `src/agents/lead_qualification_agent.py`, `src/agents/email_writer_agent.py`, `src/agents/objection_crm_agents.py`
* **Active LLM Provider**: Google GenAI SDK (`google-genai`), using model `gemini-2.5-flash` (or `gemini-2.0-flash` / `gemini-1.5-flash` / Groq `llama-3.1-70b-versatile`).

---

## 2. Environment Setup & Execution Instructions

### Step 1: Install Dependencies
```bash
cd "C:\Users\HP\Downloads\IIT PROJECT 1\Tab2_SalesAI_Agents"
pip install google-genai groq rich requests python-dotenv
```

### Step 2: Set the API Key
**Windows PowerShell**:
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key-here"
$env:AI_PROVIDER = "gemini"
```
**Windows Command Prompt (CMD)**:
```cmd
set GEMINI_API_KEY=your-gemini-api-key-here
set AI_PROVIDER=gemini
```
**Linux / macOS**:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
export AI_PROVIDER="gemini"
```

### Step 3: Run the Modes
1. **Full Automated Pipeline Demo**:
   ```bash
   python main.py --pipeline
   ```
2. **Interactive Demo + ChatGPT-Style Chat Mode**:
   ```bash
   python main.py --demo
   ```
3. **Standalone Chat / Objection Handler**:
   ```bash
   python main.py --chat
   ```

---

## 3. Running Inside Specific IDEs

### 🤖 Android Studio
1. Open Android Studio and open the folder `C:\Users\HP\Downloads\IIT PROJECT 1\Tab2_SalesAI_Agents`.
2. Open the **Terminal** tab at the bottom toolbar (`Alt + F12`).
3. Ensure Python 3.10+ is active.
4. Run:
   ```powershell
   $env:GEMINI_API_KEY = "your-gemini-api-key-here"; python main.py --demo
   ```

### 💻 VS Code / Cursor
1. Open folder in VS Code / Cursor.
2. Open built-in terminal (`Ctrl + \``).
3. Select PowerShell or Command Prompt.
4. Run `python main.py --demo`.

---

## 4. How Another AI Assistant Can Extend or Modify the Code

### Task A: Adding a New Agent
1. Create a new file in `src/agents/new_agent.py`.
2. Inherit from `BaseAgent`:
   ```python
   from .base import BaseAgent

   class NewCustomAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               name="NewCustomAgent",
               role="Specialist Role",
               system_prompt="Your custom system prompt..."
           )

       def run(self, task: dict) -> dict:
           prompt = f"Perform task on: {task}"
           response = self.think(prompt)
           return {"status": "success", "data": response}
   ```
3. Export it in `src/agents/__init__.py`.
4. Initialize and call it inside `main.py` -> `SalesAIOrchestrator`.

### Task B: Switching AI Models or Providers
In `src/agents/base.py`:
* **To change Gemini model**: Update `model="gemini-2.5-flash"` inside `call_ai()`.
* **To switch to Groq**: Set `$env:AI_PROVIDER = "groq"` and `$env:GROQ_API_KEY = "your-groq-key"`.

### Task C: Fixing Potential Windows Terminal Unicode Errors
`main.py` already includes automatic UTF-8 reconfiguration:
```python
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```
Ensure all file reading and writing specifies `encoding="utf-8"`.

---

## 5. Troubleshooting Matrix for AIs

| Error / Symptom | Root Cause | Exact Solution |
|---|---|---|
| `google.genai.errors.ClientError: 404 NOT_FOUND` | Model name mismatch or deprecated model | Check available models using `client.models.list()`. Use `gemini-2.5-flash` or `gemini-2.0-flash`. |
| `UnicodeEncodeError: 'charmap'` | Windows default code page 1252 | Keep `sys.stdout.reconfigure(encoding="utf-8")` at top of `main.py`. |
| `KeyError: choices` or JSON Parse Error | LLM returned markdown wrapped JSON | The code uses regex `re.search(r'\{.*\}', s, re.DOTALL)` to extract raw JSON safely. |
| API Key Rate Limit | Free tier quota hit | Switch provider to Groq: `$env:AI_PROVIDER = "groq"`. |
