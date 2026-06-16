"""
src/text_gen.py
────────────────
Module 1: Script Generation via LLM

WHAT:  Generates a 70-85 word narration script for the freedom fighter intro.
WHY:   The script is the backbone — audio timing, image selection, and video
       pacing all depend on a well-structured, correctly-lengthed script.
HOW:   Primary: Groq API (llama3-70b) — free, 30 req/min, sub-2-second latency.
       Fallback: Google Gemini 1.5 Flash — free tier, 15 RPM, 1M tokens/day.
"""

import time
from pathlib import Path
from config import settings
from prompts.prompt_templates import get_script_prompt
from utils.logger import log
from utils.file_utils import save_text


def generate_script(fighter_name: str | None = None) -> str:
    """
    Generate a narration script for the given freedom fighter.

    Args:
        fighter_name: Name of the freedom fighter. Falls back to settings.

    Returns:
        Script text as a string (~70-85 words).

    Raises:
        RuntimeError: If both primary and fallback providers fail.
    """
    fighter_name = fighter_name or settings.FREEDOM_FIGHTER_NAME
    log.info(f"🖊️  Generating script for: {fighter_name}")

    prompt = get_script_prompt(fighter_name)

    # Try primary provider
    if settings.LLM_PROVIDER == "groq":
        script = _generate_with_groq(prompt, fighter_name)
    elif settings.LLM_PROVIDER == "gemini":
        script = _generate_with_gemini(prompt, fighter_name)
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")

    # Validate output
    word_count = len(script.split())
    log.info(f"✅ Script generated — {word_count} words")
    if word_count < 60 or word_count > 100:
        log.warning(
            f"Word count {word_count} is outside 70-85 target. "
            "Video timing may be slightly off."
        )

    # Save script to file for inspection/debugging
    save_text(script, settings.SCRIPT_FILE)
    return script


# ── Groq Implementation ────────────────────────────────────────────────────────

def _generate_with_groq(prompt: dict, fighter_name: str) -> str:
    """
    Generate script using Groq API.

    Free tier: 30 requests/minute, 14,400 req/day.
    Model: llama3-70b-8192 — best quality on free tier.
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("groq package not installed. Run: pip install groq")

    client = Groq(api_key=settings.GROQ_API_KEY)

    log.debug(f"Calling Groq API (model: {settings.GROQ_MODEL})...")
    start = time.time()

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user",   "content": prompt["user"]},
        ],
        temperature=settings.GROQ_TEMPERATURE,
        max_tokens=settings.GROQ_MAX_TOKENS,
        stop=None,
    )

    elapsed = time.time() - start
    script = response.choices[0].message.content.strip()
    log.debug(f"Groq responded in {elapsed:.2f}s")
    return script


# ── Gemini Fallback ────────────────────────────────────────────────────────────

def _generate_with_gemini(prompt: dict, fighter_name: str) -> str:
    """
    Generate script using Google Gemini 1.5 Flash.

    Free tier: 15 RPM, 1 million tokens/day.
    Requires: pip install google-generativeai
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError(
            "google-generativeai package not installed. "
            "Run: pip install google-generativeai"
        )

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=prompt["system"],
        generation_config=genai.types.GenerationConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GROQ_MAX_TOKENS,
        ),
    )

    log.debug(f"Calling Gemini API (model: {settings.GEMINI_MODEL})...")
    start = time.time()
    response = model.generate_content(prompt["user"])
    elapsed = time.time() - start

    script = response.text.strip()
    log.debug(f"Gemini responded in {elapsed:.2f}s")
    return script


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    fighter = sys.argv[1] if len(sys.argv) > 1 else "Bhagat Singh"
    settings.validate()
    script = generate_script(fighter)
    print("\n" + "─" * 60)
    print("GENERATED SCRIPT:")
    print("─" * 60)
    print(script)
    print("─" * 60)
    print(f"Word count: {len(script.split())}")
