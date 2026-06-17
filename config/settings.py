"""
config/settings.py
──────────────────
Single source of truth for all configuration.
Reads from environment variables (.env file) with safe defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env file ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ── API Keys ───────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


# ── Subject ────────────────────────────────────────────────────────────────────
FREEDOM_FIGHTER_NAME: str = os.getenv("FREEDOM_FIGHTER_NAME", "Bhagat Singh")


# ── Provider Selection ─────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()
TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "gtts").lower()
IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "pollinations").lower()


# ── Video Settings ─────────────────────────────────────────────────────────────
VIDEO_DURATION: int = int(os.getenv("VIDEO_DURATION", "10"))
IMAGE_COUNT: int = int(os.getenv("IMAGE_COUNT", "5"))

_RESOLUTIONS = {
    "480p":  (854,  480),
    "720p":  (1280, 720),
    "1080p": (1920, 1080),
}
VIDEO_RESOLUTION: tuple[int, int] = _RESOLUTIONS.get(
    os.getenv("VIDEO_RESOLUTION", "720p"), (1280, 720)
)
VIDEO_FPS: int = 24
VIDEO_END_BUFFER = 0.5


# ── LLM Settings ──────────────────────────────────────────────────────────────
GROQ_MODEL: str = "llama-3.1-8b-instant"          # Fast, free, high quality
GROQ_TEMPERATURE: float = 0.7
GROQ_MAX_TOKENS: int = 300                   # ~150 words = ~10 sec narration


# ── TTS Settings ──────────────────────────────────────────────────────────────
GTTS_LANGUAGE: str = "en"
GTTS_TLD: str = "co.in"                      # Indian English accent


# ── Image Settings ─────────────────────────────────────────────────────────────
IMAGE_WIDTH: int = VIDEO_RESOLUTION[0]
IMAGE_HEIGHT: int = VIDEO_RESOLUTION[1]
POLLINATIONS_BASE_URL: str = "https://image.pollinations.ai/prompt"
IMAGE_STYLE_SUFFIX: str = (
    "oil painting style, highly detailed, dramatic lighting, "
    "historical portrait, Indian independence era, 8k quality"
)


# ── Paths ──────────────────────────────────────────────────────────────────────
ASSETS_DIR: Path = BASE_DIR / "assets"
IMAGES_DIR: Path = ASSETS_DIR / "images"
AUDIO_DIR: Path = ASSETS_DIR / "audio"
MUSIC_DIR: Path = ASSETS_DIR / "music"
OUTPUT_DIR: Path = ASSETS_DIR / "output"

# Ensure all directories exist at import time
for _d in [IMAGES_DIR, AUDIO_DIR, MUSIC_DIR, OUTPUT_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


# ── Output Filenames ───────────────────────────────────────────────────────────
def _safe_name(name: str) -> str:
    return name.lower().replace(" ", "_")

SCRIPT_FILE: Path = ASSETS_DIR / f"{_safe_name(FREEDOM_FIGHTER_NAME)}_script.txt"
AUDIO_FILE: Path = AUDIO_DIR / f"{_safe_name(FREEDOM_FIGHTER_NAME)}_narration.mp3"
OUTPUT_VIDEO: Path = OUTPUT_DIR / f"{_safe_name(FREEDOM_FIGHTER_NAME)}_intro.mp4"


# ── Validation ─────────────────────────────────────────────────────────────────
def validate() -> None:
    """Raise early if critical config is missing."""
    if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com and add it to .env"
        )