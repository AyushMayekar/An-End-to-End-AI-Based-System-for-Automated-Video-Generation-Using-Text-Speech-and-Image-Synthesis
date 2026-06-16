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
    - Explicit word count (70-85 words) maps precisely to ~10 seconds of TTS
      at average English speaking pace (130-150 words/minute).
    - Emotional arc instruction (intro → achievement → legacy) gives the
      script a three-act mini-structure even in 10 seconds.
    - "No bullet points, no headers" prevents the model from defaulting to
      its training bias of structured output.
    """
    system_prompt = """You are a world-class documentary narrator and scriptwriter 
specializing in Indian history and independence movements. 
You write in the style of BBC historical documentaries — authoritative, 
emotionally resonant, and deeply respectful.

STRICT OUTPUT RULES:
- Output ONLY the narration script text. No titles, no notes, no explanations.
- Exactly 70 to 85 words. Not one word more. Not one word less.
- No bullet points, no headers, no markdown formatting.
- Present tense for timeless facts, past tense for historical events.
- End with a powerful, memorable closing sentence about legacy."""

    user_prompt = f"""Write a 10-second video narration script introducing the Indian freedom fighter: {fighter_name}.

Structure your script with this emotional arc:
1. HOOK (1 sentence): Start with a powerful statement about their impact or a dramatic fact
2. IDENTITY (1-2 sentences): Who they were — birth, background, role in independence movement  
3. ACHIEVEMENT (2-3 sentences): Their most significant contribution or sacrifice for India's freedom
4. LEGACY (1 sentence): How India remembers them today — end on an inspiring, timeless note

Tone: Inspiring, dignified, cinematic. Suitable for a patriotic short film.
Target audience: Young Indians and history enthusiasts globally."""

    return {
        "system": system_prompt,
        "user": user_prompt,
    }


def get_image_prompts(fighter_name: str, script: str, count: int = 5) -> list[dict]:
    """
    Returns a list of structured image prompts for the video frames.

    WHY THIS STRUCTURE:
    - Each prompt targets a specific visual "beat" in the video timeline.
    - Subject → Setting → Mood → Style → Technical quality (5-layer prompt structure)
      is proven to produce consistent, high-quality AI images.
    - The "negative_prompt" key signals what to AVOID — critical for free models
      like Pollinations that can drift toward stock-photo aesthetics.
    - Prompts progress from iconic portrait → action → symbolic — giving the
      video a visual narrative even without motion.

    VISUAL TIMELINE MAPPING (5 images × 2 seconds each = 10 seconds):
      Frame 1 (0-2s):   Iconic portrait — establish the person
      Frame 2 (2-4s):   Historical context — their era, environment
      Frame 3 (4-6s):   Key moment — their defining action/sacrifice
      Frame 4 (6-8s):   Symbol/legacy — what they stood for
      Frame 5 (8-10s):  Tribute/memorial — how India honors them
    """

    era = "1920s-1940s British colonial India"
    base_style = (
        "highly detailed oil painting, cinematic lighting, historical realism, "
        "dramatic chiaroscuro, award-winning portrait photography style, "
        "Indian independence era aesthetic, 8K resolution, masterpiece quality"
    )
    negative = (
        "cartoon, anime, blurry, low quality, modern clothing, "
        "watermark, text overlay, western aesthetic, distorted face"
    )

    prompts = [
        {
            "frame": 1,
            "beat": "Iconic Portrait",
            "positive": (
                f"Majestic portrait of {fighter_name}, Indian freedom fighter, "
                f"{era}, determined eyes full of courage and conviction, "
                f"traditional Indian attire, dramatic side lighting, "
                f"painted against backdrop of Indian tricolor flag, {base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0,
        },
        {
            "frame": 2,
            "beat": "Historical Context",
            "positive": (
                f"{fighter_name} standing tall among Indian freedom fighters, "
                f"colonial {era} setting, crowded public rally scene, "
                f"Indian masses in background raising fists, powerful composition, "
                f"sepia-toned with golden hour lighting, {base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0,
        },
        {
            "frame": 3,
            "beat": "Defining Moment",
            "positive": (
                f"Dramatic scene of {fighter_name} in their most courageous moment, "
                f"intense emotion, {era} India, resistance against oppression, "
                f"cinematic wide shot, golden and saffron color palette, "
                f"motion blur suggesting action and sacrifice, {base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0,
        },
        {
            "frame": 4,
            "beat": "Symbol of Freedom",
            "positive": (
                f"Symbolic artwork of {fighter_name}'s legacy — "
                f"Indian tricolor flag unfurling in the wind, lotus flowers, "
                f"Ashoka Chakra, rays of golden light breaking through darkness, "
                f"{fighter_name}'s silhouette against a dawn sky, "
                f"freedom and hope symbolism, epic composition, {base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0,
        },
        {
            "frame": 5,
            "beat": "Timeless Tribute",
            "positive": (
                f"Memorial tribute to {fighter_name}, eternal flame, "
                f"Indian independence monument, marigold flowers, "
                f"people paying respects, evening golden light, "
                f"emotional and reverential atmosphere, "
                f"India's gratitude and remembrance, {base_style}"
            ),
            "negative": negative,
            "duration_seconds": 2.0,
        },
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
        "outro": "Jai Hind 🇮🇳",
        "outro_subtitle": "India Remembers",
        "font_color": "white",
        "stroke_color": "saffron",  # #FF9933
    }
