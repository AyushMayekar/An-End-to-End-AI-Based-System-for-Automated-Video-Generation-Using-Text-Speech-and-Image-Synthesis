"""
src/audio_gen.py
──────────────────
Module 2: Audio Generation via Text-to-Speech

WHAT:  Converts the narration script into an MP3 audio file.
WHY:   The audio is the timing master — video duration = audio duration.
       All images are stretched/compressed to match the audio length exactly.
HOW:   Primary: gTTS (Google TTS) — completely free, no API key, Indian English accent.
       Alt 1:  edge-tts (Microsoft) — free, higher quality, more natural prosody.
       Alt 2:  ElevenLabs — free tier 10k chars/month, most natural voice.

COMMON PITFALLS:
  - gTTS requires internet. Test early.
  - edge-tts is async — we use asyncio.run() to call it synchronously.
  - MP3 output may need conversion to WAV for MoviePy compatibility.
    We handle this with pydub if needed.
"""

import asyncio
import os
import time
from pathlib import Path
from config import settings
from utils.logger import log


def generate_audio(script: str, output_path: Path | None = None) -> Path:
    """
    Convert narration script to audio file.

    Args:
        script:      The narration text to convert.
        output_path: Where to save the audio. Defaults to settings.AUDIO_FILE.

    Returns:
        Path to the generated audio file (.mp3).
    """
    output_path = output_path or settings.AUDIO_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    log.info(f"🎙️  Generating audio via: {settings.TTS_PROVIDER}")
    log.debug(f"Script preview: {script[:80]}...")

    start = time.time()

    if settings.TTS_PROVIDER == "gtts":
        _generate_with_gtts(script, output_path)
    elif settings.TTS_PROVIDER == "edge_tts":
        _generate_with_edge_tts(script, output_path)
    elif settings.TTS_PROVIDER == "elevenlabs":
        _generate_with_elevenlabs(script, output_path)
    else:
        raise ValueError(f"Unknown TTS provider: {settings.TTS_PROVIDER}")

    elapsed = time.time() - start
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    log.info(f"✅ Audio saved → {output_path} ({size_mb:.2f} MB, {elapsed:.1f}s)")

    return output_path


def get_audio_duration(audio_path: Path) -> float:
    """
    Return duration of audio file in seconds.
    Uses mutagen (fast, no heavy dependencies) with pydub fallback.
    """
    try:
        from mutagen.mp3 import MP3
        audio = MP3(str(audio_path))
        return audio.info.length
    except Exception:
        pass

    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(str(audio_path))
        return len(audio) / 1000.0
    except Exception:
        log.warning("Could not determine audio duration. Defaulting to 10s.")
        return 10.0


# ── gTTS Implementation ────────────────────────────────────────────────────────

def _generate_with_gtts(script: str, output_path: Path) -> None:
    """
    gTTS: Google Text-to-Speech.
    - Zero API key required.
    - Uses co.in TLD for authentic Indian English accent.
    - slow=False for natural pace (~150 wpm).

    PITFALL: gTTS output can sound robotic. If quality is unacceptable,
             switch to edge_tts in your .env file.
    """
    try:
        from gtts import gTTS
    except ImportError:
        raise ImportError("gTTS not installed. Run: pip install gTTS")

    tts = gTTS(
        text=script,
        lang=settings.GTTS_LANGUAGE,
        tld=settings.GTTS_TLD,   # co.in = Indian English accent
        slow=False,
    )
    tts.save(str(output_path))
    log.debug("gTTS generation complete.")


# ── edge-tts Implementation ────────────────────────────────────────────────────

def _generate_with_edge_tts(script: str, output_path: Path) -> None:
    """
    edge-tts: Microsoft Edge's TTS engine.
    - Free, no API key.
    - Much more natural prosody than gTTS.
    - Uses en-IN-NeerjaNeural — Indian English female voice.
    - Async library, so we wrap with asyncio.run().

    Install: pip install edge-tts
    List all voices: edge-tts --list-voices
    """
    try:
        import edge_tts
    except ImportError:
        raise ImportError("edge-tts not installed. Run: pip install edge-tts")

    async def _async_generate():
        communicate = edge_tts.Communicate(
            text=script,
            voice=settings.EDGE_TTS_VOICE,
            rate="+0%",    # Normal speed
            volume="+0%",  # Normal volume
            pitch="+0Hz",  # Normal pitch
        )
        await communicate.save(str(output_path))

    # Handle event loop for Windows compatibility
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In Jupyter notebooks or async contexts
            import nest_asyncio
            nest_asyncio.apply()
            loop.run_until_complete(_async_generate())
        else:
            asyncio.run(_async_generate())
    except RuntimeError:
        asyncio.run(_async_generate())

    log.debug("edge-tts generation complete.")


# ── ElevenLabs Implementation ──────────────────────────────────────────────────

def _generate_with_elevenlabs(script: str, output_path: Path) -> None:
    """
    ElevenLabs: Most natural-sounding TTS available.
    Free tier: 10,000 characters/month — sufficient for this project.
    
    Install: pip install elevenlabs
    Get key: https://elevenlabs.io (no credit card for free tier)
    """
    try:
        from elevenlabs import ElevenLabs
    except ImportError:
        raise ImportError(
            "elevenlabs not installed. Run: pip install elevenlabs"
        )

    if not settings.ELEVENLABS_API_KEY:
        raise EnvironmentError(
            "ELEVENLABS_API_KEY not set. Add it to .env or switch TTS_PROVIDER to gtts."
        )

    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        voice_id=settings.ELEVENLABS_VOICE_ID,
        text=script,
        model_id="eleven_monolingual_v1",
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    log.debug("ElevenLabs generation complete.")


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_script = (
        "He was twenty-three years old when they hanged him. "
        "Bhagat Singh, revolutionary, martyr, and eternal flame of Indian independence. "
        "Born in 1907 in Punjab, he ignited a generation with his fearless defiance "
        "against British colonial rule. "
        "His sacrifice was not just death — it was a declaration. "
        "India would be free. Today, Bhagat Singh lives in every heart that beats for justice."
    )
    output = generate_audio(test_script)
    duration = get_audio_duration(output)
    print(f"Audio duration: {duration:.1f} seconds")
