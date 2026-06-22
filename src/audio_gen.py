"""
src/audio_gen.py
──────────────────
Module 2: Audio Generation via Text-to-Speech

WHAT:  Converts the narration script into an MP3 audio file.
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
    log.debug(f"Script preview: {script[:10]}...")

    start = time.time()

    if settings.TTS_PROVIDER == "gtts":
        _generate_with_gtts(script, output_path)
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
    """
    try:
        from gtts import gTTS
    except ImportError:
        raise ImportError("gTTS not installed. Run: uv add gTTS")

    tts = gTTS(
        text=script,
        lang=settings.GTTS_LANGUAGE,
        tld=settings.GTTS_TLD,   # co.in = Indian English accent
        slow=False,
    )
    tts.save(str(output_path))
    log.debug("gTTS generation complete.")

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
