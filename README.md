# An-End-to-End-AI-Based-System-for-Automated-Video-Generation-Using-Text-Speech-and-Image-Synthesis

> An AI-powered Python pipeline that generates a 10-second video introducing an Indian freedom fighter.
---

## 📋 Table of Contents

1. [What It Does](#what-it-does)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Setup (5 Minutes)](#quick-setup)
5. [API Keys Setup](#api-keys)
6. [Running the Pipeline](#running)
7. [Configuration Reference](#config)
8. [Prompt Engineering Strategy](#prompts)
9. [Troubleshooting](#troubleshooting)
10. [Project Structure](#structure)

---

## What It Does

This pipeline automatically:

1. **Generates a narration script** — Uses Groq (free LLM API) to write a cinematic 70-85 word script about your chosen freedom fighter
2. **Converts script to speech** — Uses gTTS (Google TTS, free, no key needed) with Indian English accent
3. **Generates 5 AI images** — Uses Pollinations.ai (completely free, no sign-up) with cinematic prompts
4. **Assembles the video** — Uses MoviePy (CPU-only) with Ken Burns effects, crossfade transitions, and title overlays

**Total cost: ₹0 / $0**  
**Hardware requirement: Any Windows laptop with internet**

---

## Architecture

```
main.py (orchestrator)
├── src/text_gen.py   → Groq API → narration_script.txt
├── src/audio_gen.py  → gTTS    → narration.mp3
├── src/image_gen.py  → Pollinations.ai → frame_01-05.jpg
└── src/video_gen.py  → MoviePy → freedom_fighter_intro.mp4
```

---

## Prerequisites

- Python 3.10 or higher
- Windows 10/11
- Internet connection
- Free Groq API key (takes 2 minutes to get)

---

## Quick Setup

### Step 1: Clone / Download the project

```bash
# If you have git:
git clone <your-repo-url>
cd freedom_fighter_video

# Or just download and extract the ZIP
```

### Step 2: Create a virtual environment

```bash
# Open Command Prompt or PowerShell
python -m venv venv

# Activate it
venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **If moviepy installation is slow**, it's downloading ffmpeg. This is normal. Wait 2-5 minutes.

### Step 4: Set up API keys

```bash
# Copy the example file
copy .env.example .env

# Open .env in Notepad and fill in your keys
notepad .env
```

### Step 5: Run the pipeline

```bash
python main.py "Bhagat Singh"
```

---

## API Keys

### Groq API Key (Required — takes 2 minutes)

1. Go to **https://console.groq.com**
2. Click "Sign Up" — no credit card required
3. Go to **API Keys** → **Create API Key**
4. Copy the key and paste into `.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

### Other Keys (All Optional)

| Key | Service | Where to Get | Why Use It |
|-----|---------|-------------|-----------|
| `GEMINI_API_KEY` | Google Gemini | https://aistudio.google.com | Fallback LLM |
| `ELEVENLABS_API_KEY` | ElevenLabs | https://elevenlabs.io | Better voice quality |
| `STABILITY_API_KEY` | Stability AI | https://platform.stability.ai | Better images |

---

## Running the Pipeline

### Basic Usage

```bash
# Default fighter from .env
python main.py

# Specify a fighter
python main.py "Rani Lakshmibai"
python main.py "Subhas Chandra Bose"
python main.py "Chandra Shekhar Azad"
```

### Advanced Options

```bash
# Use better TTS voice (requires no extra key)
python main.py "Bhagat Singh" --tts edge_tts

# Generate more frames for smoother video
python main.py "Bhagat Singh" --images 8

# Use Gemini instead of Groq for script
python main.py "Bhagat Singh" --llm gemini

# Skip regenerating images (reuse existing ones)
python main.py "Bhagat Singh" --skip-images

# See list of suggested freedom fighters
python main.py --list-fighters
```

### Expected Output

```
Step 1/4: Generating narration script         (~3 seconds)
Step 2/4: Generating audio (gtts)             (~5 seconds)  
Step 3/4: Generating 5 images (pollinations)  (~60 seconds)
Step 4/4: Assembling final video              (~90 seconds)

Output: assets/output/bhagat_singh_intro.mp4
```

---

## Configuration Reference

Edit `.env` to customize behavior:

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `FREEDOM_FIGHTER_NAME` | `Bhagat Singh` | Any name | The subject of the video |
| `LLM_PROVIDER` | `groq` | `groq`, `gemini` | LLM for script generation |
| `TTS_PROVIDER` | `gtts` | `gtts`, `edge_tts`, `elevenlabs` | Text-to-speech engine |
| `IMAGE_PROVIDER` | `pollinations` | `pollinations`, `stability`, `huggingface` | Image generation service |
| `IMAGE_COUNT` | `5` | `3`-`10` | Number of video frames |
| `VIDEO_RESOLUTION` | `720p` | `480p`, `720p`, `1080p` | Output resolution |
| `VIDEO_DURATION` | `10` | `8`-`15` | Target duration (seconds) |

---

## Prompt Engineering Strategy

### Script Prompt Design

The narration script prompt uses a **5-layer engineering approach**:

1. **Role Assignment**: "You are a world-class documentary narrator..." — shifts the model toward authoritative, cinematic language
2. **Emotional Arc Constraint**: Explicitly defines a 3-part structure (Hook → Achievement → Legacy) for narrative coherence
3. **Format Constraint**: "Exactly 70-85 words" — maps to precisely ~10 seconds of TTS at 140 wpm
4. **Negative Constraint**: "No bullet points, no headers" — prevents the model's default structured-output bias
5. **Quality Anchor**: "BBC historical documentaries" — references a known quality standard the model can emulate

### Image Prompt Design

Each image prompt follows a **5-component structure**:
```
[Subject + Identity] + [Setting + Era] + [Mood + Emotion] + [Composition] + [Technical Style]
```

The 5 images map to a **visual timeline**:
- Frame 1 (0-2s): Iconic portrait — establish the person
- Frame 2 (2-4s): Historical context — their era
- Frame 3 (4-6s): Defining moment — their key action
- Frame 4 (6-8s): Symbol of freedom — what they stood for
- Frame 5 (8-10s): Timeless tribute — how India honors them

---

## Troubleshooting

### "GROQ_API_KEY is not set"
→ Add your key to `.env`. Get it free at https://console.groq.com

### "gTTS request failed"
→ Check your internet connection. gTTS requires internet access.
→ Try: `TTS_PROVIDER=edge_tts` in `.env`

### "Pollinations returned 503"
→ Pollinations.ai is sometimes slow. The code retries automatically.
→ Wait 30 seconds and try again.

### "moviepy not found" or video assembly fails
```bash
pip install moviepy imageio-ffmpeg
```

### "No module named 'PIL'"
```bash
pip install Pillow
```

### Video is too short or too long
→ Audio duration controls video duration. Adjust your TTS provider.
→ `edge_tts` typically produces more natural pacing than `gtts`.

### Images look wrong / placeholder images appear
→ Pollinations.ai may be rate-limiting. Wait 1-2 minutes and re-run with `--skip-audio`.
→ Or switch to `IMAGE_PROVIDER=stability` with a free Stability AI key.

---

## Project Structure

```
freedom_fighter_video/
├── .env                    ← Your API keys (never commit this!)
├── .env.example            ← Template for .env
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
├── main.py                 ← Entry point
│
├── config/
│   └── settings.py         ← All configuration in one place
│
├── src/
│   ├── text_gen.py         ← Module 1: Script generation (Groq/Gemini)
│   ├── audio_gen.py        ← Module 2: TTS audio (gTTS/edge-tts/ElevenLabs)
│   ├── image_gen.py        ← Module 3: Image generation (Pollinations.ai)
│   └── video_gen.py        ← Module 4: Video assembly (MoviePy)
│
├── prompts/
│   └── prompt_templates.py ← All LLM and image prompts
│
├── utils/
│   ├── logger.py           ← Colored logging
│   └── file_utils.py       ← File I/O helpers
│
└── assets/
    ├── images/             ← Generated frames (frame_01.jpg ... frame_05.jpg)
    ├── audio/              ← Generated narration (narration.mp3)
    ├── music/              ← Optional background music
    └── output/             ← Final video (freedom_fighter_intro.mp4)
```

---

## Tech Stack

| Component | Tool | Why Free |
|-----------|------|---------|
| Script LLM | Groq (llama-3.1-8b-instant) | 30 req/min free, no credit card |
| TTS | gTTS (Google) | Free, unlimited, no key needed |
| Image Gen | Pollinations.ai | 100% free, no sign-up, no key |
| Video Assembly | MoviePy | Open source, CPU-only |
| Python | 3.10+ | Open source |

---

*Built for the AI Video Generation Assignment — Zero cost, maximum quality.*
