import os
import httpx
from typing import List, Dict, Any
from .local_insights import heuristic_insights

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "text-bison-001")
GEMINI_ENDPOINT = os.environ.get("GEMINI_ENDPOINT", "https://api.openai.com/v1/")  # placeholder; adjust per provider

# NOTE: The example below is a generic HTTP call pattern. Replace GEMINI_ENDPOINT and request body
# to match your actual LLM endpoint provider. For Google Gemini you would use the official endpoint.
# This function is written to be easily swapped for any provider.

def _build_prompt(metrics: List[Dict[str, Any]]) -> str:
    examples = []
    for m in metrics[-5:]:
        examples.append(
            f"- time: {m.get('timestamp')}, sleep_hours: {m.get('sleep_hours')}, steps: {m.get('steps')}, "
            f"mood: {m.get('mood')}, heart_rate: {m.get('heart_rate')}"
        )
    prompt = (
        "You are a helpful medical-adjacent assistant (non-diagnostic). "
        "Given recent health metrics, produce:\n1) short summary (1 sentence)\n"
        "2) 3 practical recommendations\n3) any risk flags (as short labels).\n\n"
        "Recent metrics:\n" + "\n".join(examples) + "\n\nRespond in JSON with keys: summary, recommendations (list), risk_flags (list)."
    )
    return prompt

async def _call_gemini(prompt: str) -> Dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("No Gemini API key configured")
    # This is intentionally generic. Adapt headers/body for your specific LLM endpoint.
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GEMINI_MODEL,
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.6,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Replace URL below with provider-specific generation endpoint.
        url = os.environ.get("GEMINI_API_URL") or (GEMINI_ENDPOINT.rstrip("/") + "/completions")
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    # Attempt to extract text — provider-specific structure
    text = ""
    if isinstance(data, dict):
        # try common fields
        if "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
            text = data["choices"][0].get("text") or data["choices"][0].get("message", {}).get("content", "")
        else:
            text = data.get("text") or data.get("content") or str(data)
    return {"raw_text": text, "meta": data}

def _parse_llm_output(raw_text: str) -> Dict:
    # Try to parse JSON from the LLM output; if fails, fall back to heuristics.
    import json
    try:
        trimmed = raw_text.strip()
        # Some LLMs wrap JSON in triple backticks or plain text; attempt to find first { ... }
        start = trimmed.find("{")
        end = trimmed.rfind("}")
        if start != -1 and end != -1:
            json_text = trimmed[start:end+1]
            parsed = json.loads(json_text)
            # ensure types
            summary = parsed.get("summary", "")
            recommendations = parsed.get("recommendations", []) or []
            risk_flags = parsed.get("risk_flags", []) or []
            return {"summary": summary, "recommendations": recommendations, "risk_flags": risk_flags}
    except Exception:
        pass
    # fallback — rudimentary parsing by lines
    lines = raw_text.splitlines()
    summary = lines[0] if lines else ""
    recs = [l.strip("- ") for l in lines if l.lower().startswith("-")]
    return {"summary": summary, "recommendations": recs[:3], "risk_flags": []}

async def generate_insights(metrics: List[Dict]) -> Dict:
    """
    Asynchronous LLM-backed insights. If LLM fails or is not configured, falls back to the heuristic_insights.
    """
    try:
        prompt = _build_prompt(metrics)
        resp = await _call_gemini(prompt)
        raw_text = resp.get("raw_text", "")
        parsed = _parse_llm_output(raw_text)
        # ensure non-empty
        if parsed.get("summary"):
            return parsed
        # else fallback
    except Exception as e:
        # log in real app
        # print("LLM call failed:", e)
        pass
    # fallback synchronous heuristic
    return heuristic_insights(metrics)
