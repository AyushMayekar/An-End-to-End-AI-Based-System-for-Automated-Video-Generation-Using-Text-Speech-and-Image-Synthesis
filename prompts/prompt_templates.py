"""
prompts/prompt_templates.py
─────────────────────────────
Centralized, reusable prompt templates for all generation tasks.

PROMPT ENGINEERING PHILOSOPHY:
  1. ROLE ASSIGNMENT     — Tell the model who it is before what to do
  2. CONTEXT ANCHORING   — Ground the model in specific historical facts
  3. FORMAT CONSTRAINTS  — Specify output format, length, and style explicitly
  4. NEGATIVE CONSTRAINTS— Tell the model what NOT to do
  5. QUALITY ANCHORS     — Reference known quality standards ("documentary quality")
"""


def get_script_prompt(fighter_name: str) -> dict:
    """
    Returns the full prompt payload for narration script generation.

    WHY THIS WORKS:
    - Role assignment ("world-class documentary narrator") shifts the model
      toward authoritative, cinematic language rather than encyclopedic text.
    - Explicit word count (10-20 words) maps precisely to ~10 seconds of TTS
      at average English speaking pace (130-150 words/minute).
    - Emotional arc instruction (intro → achievement → legacy) gives the
      script a three-act mini-structure even in 10 seconds.
    - "No bullet points, no headers" prevents the model from defaulting to
      its training bias of structured output.
    """
    system_prompt = """You are an award-winning documentary narrator specializing in Indian history and the freedom movement.

Write concise, cinematic narration for short-form videos.

STRICT RULES:
- Return ONLY the narration text.
- Output EXACTLY 15 words. Count carefully before responding.
- Never exceed or fall below the required word count.
- Use a SINGLE sentence only.
- No titles, notes, explanations, quotes, markdown, emojis, or bullet points.
- Include: identity, defining contribution, and enduring legacy.
- Use emotionally precise, high-impact language.
- Present tense for timeless facts; past tense for historical events.
- Maintain a respectful, authoritative BBC documentary tone.
- If the draft exceeds the word limit, rewrite it until the word count is exact."""

    user_prompt = f"""Create a narration script for a 10-second video about {fighter_name}.

Requirements:
- Exact word count: 15 words
- Audience: Young Indians and global history enthusiasts
- Tone: Inspiring, cinematic, dignified, patriotic
- Prioritize specificity over generic praise
- Focus on the person's most significant contribution
- End with a memorable phrase about their legacy"""

    return {
        "system": system_prompt,
        "user": user_prompt,
    }


def get_image_prompts(fighter_name: str, script: str, count: int = 5) -> list[dict]:
    era = "1920s-1940s British colonial India"

    base_style = (
        "historically accurate cinematic illustration, realistic textures, "
        "dramatic natural lighting, subtle chiaroscuro, period-authentic colors, "
        "high detail, consistent facial features, realistic anatomy, "
        "Indian independence movement aesthetic"
    )

    subject_priority = (
        f"{fighter_name} is the dominant focal point in every frame, occupying 50-70% of the composition. "
        "Maintain consistent facial features, age, attire, expression, and physical characteristics across all frames. "
        "Background elements must support the story without distracting from the subject."
    )

    negative = (
        "cartoon, anime, low quality, blurry, distorted face, duplicate person, "
        "extra limbs, inaccurate anatomy, modern clothing, modern objects, "
        "watermark, text, logo, western aesthetic, futuristic elements, "
        "oversaturated colors, cluttered background"
    )

    prompts = [
        {
            "frame": 1,
            "beat": "Iconic Portrait",
            "positive": (
                f"{subject_priority} "
                f"Close-up portrait of {fighter_name}, Indian freedom fighter from {era}, "
                "direct gaze with determination and conviction, traditional attire, "
                "dramatic side lighting highlighting facial features, "
                "subtle Indian tricolor tones in the distant background, "
                "minimal environment, focus on emotion and identity, "
                f"{base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0
        },
        {
            "frame": 2,
            "beat": "Historical Context",
            "positive": (
                f"{subject_priority} "
                f"{fighter_name} addressing or standing among a public gathering during India's independence movement, "
                f"{era}, crowds and colonial architecture softly blurred in the background, "
                "historically accurate clothing and setting, "
                "the environment provides context while the character remains the visual focus, "
                "cinematic depth of field, authentic historical atmosphere, "
                f"{base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0
        },
        {
            "frame": 3,
            "beat": "Defining Moment",
            "positive": (
                f"{subject_priority} "
                f"{fighter_name} during a defining historical moment, showing courage and sacrifice, "
                f"{era}, dynamic composition with subtle movement, "
                "expressive face and body language, "
                "historical context visible but secondary, "
                "natural environmental details emphasizing struggle and resilience, "
                f"{base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0
        },
        {
            "frame": 4,
            "beat": "Legacy",
            "positive": (
                f"{subject_priority} "
                f"Heroic portrayal of {fighter_name} symbolizing hope and freedom, "
                "Indian tricolor elements, Ashoka Chakra, and dawn light integrated subtly into the background, "
                "symbolism should enhance the narrative without overpowering the subject, "
                "uplifting and inspirational mood, "
                f"{base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0
        },
        {
            "frame": 5,
            "beat": "Remembrance",
            "positive": (
                f"{subject_priority} "
                f"Respectful tribute to {fighter_name}, shown as the central figure in a memorial setting, "
                "people paying respects in the background, eternal flame and flowers used sparingly, "
                "warm evening light, emotional yet dignified atmosphere, "
                "the tribute environment supports the character's legacy rather than dominating the scene, "
                f"{base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0
        }
    ]

    # If count differs from 5, trim or duplicate proportionally
    if count < len(prompts):
        return prompts[:count]
    elif count > len(prompts):
        # Cycle through prompts to reach desired count
        extended = prompts.copy()
        while len(extended) < count:
            extended.append(prompts[len(extended) % len(prompts)])
        return extended[:count]

    return prompts


def get_title_card_text(fighter_name: str) -> dict:
    """
    Text overlays for the video title card and end card.

    Returns dict with 'intro' and 'outro' text for MoviePy TextClip.
    """
    return {
        "intro": fighter_name.upper(),
        "intro_subtitle": "Indian Freedom Fighter",
        "outro": "JAI HIND!!!",
        "outro_subtitle": "India Remembers",
        "font_color": "white",
        "stroke_color": "saffron",  # #FF9933
    }
