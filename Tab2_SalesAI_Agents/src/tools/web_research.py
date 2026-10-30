"""
Web Research Tool
=================
Real web data enrichment for leads.
Uses public APIs (DuckDuckGo Instant Answer, Wikipedia, Hunter.io concepts)
and web scraping (requests + basic parsing) — no paid API keys needed.
"""

import re
import json
import time
import requests
from typing import Optional, Dict, List
from urllib.parse import quote_plus, urlparse


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html;q=0.9",
}

TIMEOUT = 8


def search_duckduckgo(query: str) -> List[Dict]:
    """Search using DuckDuckGo Instant Answer API (free, no key needed)."""
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json()
        results = []

        # Abstract
        if data.get("Abstract"):
            results.append({
                "type": "abstract",
                "title": data.get("Heading", query),
                "text": data["Abstract"][:500],
                "source": data.get("AbstractURL", "")
            })

        # Related topics
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append({
                    "type": "related",
                    "text": topic["Text"][:300],
                    "source": topic.get("FirstURL", "")
                })

        return results
    except Exception:
        return []


def get_company_info_duckduckgo(company_name: str) -> Dict:
    """Get company information from DuckDuckGo."""
    results = search_duckduckgo(f"{company_name} company startup B2B")
    if not results:
        results = search_duckduckgo(company_name)

    combined_text = " ".join([r.get("text", "") for r in results])
    return {
        "company": company_name,
        "raw_text": combined_text[:800],
        "sources": [r.get("source", "") for r in results if r.get("source")],
        "found": len(results) > 0
    }


def check_website_live(url: str) -> Dict:
    """Check if a company website is live and get basic meta info."""
    if not url:
        return {"live": False, "url": url}
    if not url.startswith("http"):
        url = "https://" + url

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        html = resp.text[:5000]

        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        # Extract description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', html, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract keywords
        kw_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)', html, re.IGNORECASE)
        keywords = kw_match.group(1).strip() if kw_match else ""

        # Detect tech signals
        tech_signals = []
        tech_patterns = {
            "React": ["react", "_next", "NextJS"],
            "WordPress": ["wp-content", "wordpress"],
            "Shopify": ["shopify", "myshopify"],
            "HubSpot": ["hubspot", "hs-scripts"],
            "Salesforce": ["salesforce", "pardot"],
            "Intercom": ["intercom"],
            "Zendesk": ["zendesk"],
            "Stripe": ["stripe"],
            "Google Analytics": ["gtag", "google-analytics", "UA-"],
            "Hotjar": ["hotjar"],
            "Drift": ["drift"],
        }
        for tech, patterns in tech_patterns.items():
            if any(p.lower() in html.lower() for p in patterns):
                tech_signals.append(tech)

        return {
            "live": True,
            "url": url,
            "title": title[:100],
            "description": description[:300],
            "keywords": keywords[:200],
            "tech_signals": tech_signals,
            "status_code": resp.status_code
        }
    except requests.exceptions.SSLError:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            return {"live": True, "url": url, "title": "", "description": "", "tech_signals": [], "status_code": resp.status_code}
        except Exception:
            return {"live": False, "url": url, "error": "SSL error"}
    except Exception as e:
        return {"live": False, "url": url, "error": str(e)[:100]}


def get_linkedin_signals(company_name: str, person_name: str = "") -> Dict:
    """
    Get LinkedIn signals via DuckDuckGo (LinkedIn blocks direct scraping).
    Searches for LinkedIn profile/company data via search engine results.
    """
    results = {}

    # Search for company on LinkedIn via DDG
    company_query = f"site:linkedin.com/company {company_name}"
    co_results = search_duckduckgo(company_query)
    if co_results:
        results["company_linkedin"] = co_results[0].get("text", "")

    # Search for person on LinkedIn via DDG
    if person_name:
        person_query = f"site:linkedin.com/in {person_name} {company_name}"
        p_results = search_duckduckgo(person_query)
        if p_results:
            results["person_linkedin"] = p_results[0].get("text", "")

    return results


def get_news_signals(company_name: str) -> List[Dict]:
    """Get recent news about a company via DuckDuckGo News search."""
    try:
        query = f"{company_name} funding OR launch OR partnership OR growth OR hiring 2025 OR 2026"
        results = search_duckduckgo(query)
        news = []
        for r in results[:5]:
            if r.get("text"):
                news.append({
                    "headline": r["text"][:150],
                    "source": r.get("source", ""),
                    "relevance": "high" if any(w in r["text"].lower() for w in ["fund", "launch", "partner", "hire", "expand"]) else "medium"
                })
        return news
    except Exception:
        return []


def enrich_lead(company_name: str, contact_name: str = "", website: str = "", industry: str = "") -> Dict:
    """
    Master enrichment function — aggregates all data sources.
    Returns a rich profile with real data from the web.
    """
    enrichment = {
        "company": company_name,
        "contact": contact_name,
        "enriched_at": __import__('datetime').datetime.now().isoformat(),
        "data_sources": []
    }

    # 1. Check website
    if website:
        site_data = check_website_live(website)
        enrichment["website_data"] = site_data
        if site_data.get("live"):
            enrichment["data_sources"].append("website")
            enrichment["tech_stack_detected"] = site_data.get("tech_signals", [])

    # 2. Company search
    co_info = get_company_info_duckduckgo(company_name)
    enrichment["company_web_info"] = co_info
    if co_info.get("found"):
        enrichment["data_sources"].append("web_search")

    # 3. News signals
    news = get_news_signals(company_name)
    enrichment["recent_news"] = news
    if news:
        enrichment["data_sources"].append("news")

    # 4. LinkedIn signals
    li_signals = get_linkedin_signals(company_name, contact_name)
    enrichment["linkedin_signals"] = li_signals
    if li_signals:
        enrichment["data_sources"].append("linkedin_search")

    # 5. Infer from all data
    enrichment["summary"] = _build_enrichment_summary(enrichment, industry)

    return enrichment


def _build_enrichment_summary(enrichment: Dict, industry: str = "") -> Dict:
    """Build a summary of key insights from enrichment data."""
    tech_stack = enrichment.get("tech_stack_detected", [])
    news = enrichment.get("recent_news", [])
    website_data = enrichment.get("website_data", {})
    web_text = enrichment.get("company_web_info", {}).get("raw_text", "")

    # Infer company size from signals
    size_signals = []
    if any(w in web_text.lower() for w in ["series a", "series b", "seed"]):
        size_signals.append("startup/early-stage")
    if any(w in web_text.lower() for w in ["enterprise", "fortune 500", "global"]):
        size_signals.append("enterprise")
    if any(w in web_text.lower() for w in ["50 employees", "100 employees", "team of"]):
        size_signals.append("smb")

    # Revenue triggers
    triggers = []
    for n in news:
        h = n.get("headline", "").lower()
        if "fund" in h or "raise" in h or "million" in h:
            triggers.append(f"Funding activity: {n['headline'][:80]}")
        if "hire" in h or "hiring" in h or "expand" in h:
            triggers.append(f"Growth signal: {n['headline'][:80]}")
        if "partner" in h or "launch" in h:
            triggers.append(f"Business event: {n['headline'][:80]}")

    # Tech stack insights
    crm_tools = [t for t in tech_stack if t in ["HubSpot", "Salesforce", "Zendesk", "Intercom", "Drift"]]
    analytics_tools = [t for t in tech_stack if t in ["Google Analytics", "Hotjar"]]

    return {
        "size_signals": size_signals[:2] if size_signals else ["unknown"],
        "business_triggers": triggers[:3],
        "current_crm_tools": crm_tools,
        "analytics_tools": analytics_tools,
        "website_live": website_data.get("live", False),
        "website_description": website_data.get("description", ""),
        "data_quality": "high" if len(enrichment.get("data_sources", [])) >= 3 else "medium" if len(enrichment.get("data_sources", [])) >= 2 else "low"
    }
