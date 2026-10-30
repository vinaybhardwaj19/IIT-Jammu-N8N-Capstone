"""
SalesAI SDR Multi-Agent System
================================
Tab 2: OpenAI Agents SDK Capstone — IIT Summer School 2026
Author: Vinay Bhardwaj
Domain: B2B Sales Automation using AI Agents

Architecture: 6 OpenAI Agents SDK specialists. The legacy multi-provider
call_ai() helper remains for compatibility utilities only.

Agents:
1. ProspectResearchAgent    — Deep company & contact intelligence
2. LeadQualificationAgent   — BANT scoring + ICP matching
3. EmailWriterAgent         — Hyper-personalized outreach sequences  
4. MeetingCoordinatorAgent  — Calendar management & scheduling
5. ObjectionHandlerAgent    — Real-time objection rebuttal engine
6. CRMManagerAgent          — Pipeline tracking & deal progression
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION — Compatibility Provider Helper
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
AI_API_KEY = os.environ.get("AI_API_KEY", "").strip()
AI_BASE_URL = os.environ.get("AI_BASE_URL", "").strip().rstrip("/")
AI_MODEL = os.environ.get("AI_MODEL", "").strip()

AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini").lower()


class AIProviderError(RuntimeError):
    """Raised when no configured AI provider can return a response."""

# ============================================================
# COMPATIBILITY AI CLIENT HELPER
# ============================================================

def get_ai_client():
    """Initialize AI client based on configured provider."""
    if AI_PROVIDER == "gemini":
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            return client, "gemini"
        except ImportError:
            print("⚠️  google-genai not installed. Falling back to Groq.")
            return _get_groq_client()
    else:
        return _get_groq_client()

def _get_groq_client():
    """Initialize Groq client as fallback."""
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        return client, "groq"
    except ImportError:
        print("❌ Neither google-genai nor groq is installed.")
        print("Run: pip install google-genai groq")
        sys.exit(1)

def call_ai(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    """Call the configured live provider; fail clearly instead of returning canned text."""
    errors = []

    def use_gemini():
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        models = [os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"), "gemini-flash-latest"]
        failures = []
        for model in dict.fromkeys(models):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=(f"{system}\n\n{prompt}" if system else prompt),
                    config=types.GenerateContentConfig(temperature=temperature),
                )
                if response.text:
                    return response.text
                failures.append(f"{model}: empty response")
            except Exception as exc:
                failures.append(f"{model}: {type(exc).__name__}")
        raise RuntimeError("; ".join(failures))

    def use_groq():
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        messages = ([{"role": "system", "content": system}] if system else [])
        messages.append({"role": "user", "content": prompt})
        failures = []
        for model in (os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"), "llama-3.1-8b-instant"):
            try:
                response = client.chat.completions.create(
                    model=model, messages=messages, temperature=temperature, max_tokens=3000,
                )
                content = response.choices[0].message.content
                if content:
                    return content
                failures.append(f"{model}: empty response")
            except Exception as exc:
                failures.append(f"{model}: {type(exc).__name__}")
        raise RuntimeError("; ".join(failures))

    def use_openai_compatible(api_key: str, base_url: str, model: str, provider: str):
        messages = ([{"role": "system", "content": system}] if system else [])
        messages.append({"role": "user", "content": prompt})
        response = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": temperature},
            timeout=90,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
        content = response.json()["choices"][0]["message"].get("content")
        if not content:
            raise RuntimeError("empty response")
        return content

    compatible = []
    if OPENAI_API_KEY:
        compatible.append(("openai", OPENAI_API_KEY, "https://api.openai.com/v1", AI_MODEL or "gpt-4o-mini"))
    if OPENROUTER_API_KEY:
        compatible.append(("openrouter", OPENROUTER_API_KEY, "https://openrouter.ai/api/v1", AI_MODEL or "openai/gpt-4o-mini"))
    if AI_API_KEY and AI_BASE_URL:
        compatible.append(("custom OpenAI-compatible API", AI_API_KEY, AI_BASE_URL, AI_MODEL))

    providers = {
        "gemini": (lambda: use_gemini(), bool(GEMINI_API_KEY)),
        "groq": (lambda: use_groq(), bool(GROQ_API_KEY)),
    }
    for name, key, url, model in compatible:
        providers[name] = (lambda k=key, u=url, m=model, n=name: use_openai_compatible(k, u, m, n), True)

    preferred = AI_PROVIDER.lower()
    order = [preferred] + [name for name in providers if name != preferred]
    available = [name for name in order if name in providers and providers[name][1]]
    if not available:
        raise AIProviderError("No AI provider key is configured. Set Gemini, Groq, OpenAI, OpenRouter, or AI_API_KEY with AI_BASE_URL and AI_MODEL in .env.")

    for name in available:
        try:
            return providers[name][0]()
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__} ({str(exc)[:300]})")

    raise AIProviderError("All configured AI providers failed: " + " | ".join(errors))


# ============================================================
# BASE AGENT CLASS
# ============================================================

class BaseAgent:
    """
    Base class for all SalesAI SDR agents.
    Every agent has: name, role, system_prompt, and a run() method.
    """
    
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.memory = []  # Conversation history
        self.tokens_used = 0
        # The project agents now run through the official OpenAI Agents SDK.
        # Import lazily so local utilities that only use call_ai remain importable.
        from salesai_agents.sdk_runtime import register_agent
        self.sdk_agent = register_agent(name, role, system_prompt)
        
    def _log(self, message: str):
        """Structured logging with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"  [{timestamp}] [{self.name}] {message}")
    
    def _remember(self, role: str, content: str):
        """Add message to agent memory."""
        self.memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def think(self, user_input: str, temperature: float = 0.3) -> str:
        """Run this specialist through the OpenAI Agents SDK and return its typed payload."""
        self._remember("user", user_input)
        
        # Build context from memory (last 5 exchanges)
        context = ""
        if len(self.memory) > 2:
            recent = self.memory[-5:-1]
            context = "\n".join([f"{m['role'].upper()}: {m['content'][:200]}" for m in recent])
            context = f"\n\nRecent context:\n{context}\n\n"
        
        full_prompt = f"{context}Current task: {user_input}"
        
        from salesai_agents.sdk_runtime import run_agent
        response = run_agent(self.sdk_agent, full_prompt, temperature=temperature)
        self._remember("assistant", response)
        return response
    
    def run(self, task: dict) -> dict:
        """Override this in each agent subclass."""
        raise NotImplementedError(f"{self.name}.run() must be implemented")
    
    def get_stats(self) -> dict:
        return {
            "agent": self.name,
            "role": self.role,
            "interactions": len(self.memory) // 2,
            "memory_entries": len(self.memory)
        }
