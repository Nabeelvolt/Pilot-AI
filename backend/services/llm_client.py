import os
import json
import time
import logging
from groq import Groq
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Initialise both clients at startup
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(settings.FALLBACK_LLM)
else:
    gemini_model = None

def call_llm(system_prompt: str, user_prompt: str,
             max_tokens: int = 3000, temperature: float = 0.0,
             require_json: bool = True) -> str:
    """
    Call Groq first. If rate-limited or unavailable, fall back to Gemini.
    Returns raw string (JSON string if require_json=True).
    Raises RuntimeError if both providers fail.
    """

    # ── ATTEMPT 1: Groq (primary — fastest free inference) ────────────────────
    if groq_client:
        try:
            logger.info(f"Calling Groq [{settings.PRIMARY_LLM}]")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            response = groq_client.chat.completions.create(
                model=settings.PRIMARY_LLM,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                # Groq supports response_format for JSON mode
                response_format={"type": "json_object"} if require_json else None,
            )
            content = response.choices[0].message.content
            logger.info(f"Groq success — {response.usage.total_tokens} tokens used")
            return content
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                logger.warning(f"Groq rate limit hit — falling back to Gemini: {e}")
            else:
                logger.warning(f"Groq error — falling back to Gemini: {e}")

    # ── ATTEMPT 2: Gemini (fallback — 1M context, generous free tier) ─────────
    if gemini_model:
        try:
            logger.info(f"Calling Gemini [{settings.FALLBACK_LLM}]")
            # Gemini takes a combined prompt
            combined = f"{system_prompt}\n\n---\n\n{user_prompt}"
            if require_json:
                combined += "\n\nRespond ONLY with valid JSON. No markdown, no preamble, no ```json fences."
            result = gemini_model.generate_content(combined)
            content = result.text.strip()
            # Strip markdown fences if Gemini adds them despite instructions
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            logger.info("Gemini success")
            return content
        except Exception as e:
            logger.error(f"Gemini also failed: {e}")
            raise RuntimeError(f"Both LLM providers failed. Last error: {e}")

    raise RuntimeError(
        "No LLM providers configured. Add GROQ_API_KEY or GEMINI_API_KEY to your .env file."
    )
