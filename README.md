# An-End-to-End-AI-Based-System-for-Automated-Video-Generation-Using-Text-Speech-and-Image-Synthesis

> An AI-powered Python pipeline that generates a 10-second video introducing an Indian freedom fighter.
---

## 📋 Table of Contents

1. [What It Does](#what-it-does)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Demo Video](#demo)
4. [Prerequisites](#prerequisites)
5. [Quick Setup](#quick-setup)
6. [API Keys](#api-keys)
7. [Running the Pipeline](#running-the-pipeline)
8. [Configuration Reference](#configuration-reference)
9. [Prompt Engineering Strategy](#prompt-engineering-strategy)
10. [Troubleshooting](#troubleshooting)
11. [Project Structure](#project-structure)
12. [Testing](#testing)


---

## What It Does

This pipeline automatically:

1. **Generates a narration script**: Uses Groq (free LLM API) to write a cinematic 10-15 word script about your chosen freedom fighter
2. **Converts script to speech**: Uses gTTS (Google TTS, free, no key needed) with Indian English accent
3. **Generates 5 AI images**: Uses Pollinations.ai (completely free, no sign-up) with cinematic prompts
4. **Assembles the video**: Uses MoviePy (CPU-only) with Ken Burns effects, crossfade transitions, and title overlays

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

## Tech Stack

| Component | Tool | Why Free |
|-----------|------|---------|
| Script LLM | Groq (llama-3.1-8b-instant) | 30 req/min free, no credit card |
| TTS | gTTS (Google) | Free, unlimited, no key needed |
| Image Gen | Pollinations.ai | 100% free, no sign-up, no key |
| Video Assembly | MoviePy | Open source, CPU-only |
| Python | 3.12 | Open source |

---

## Demo

[![Watch Demo](docs/demo-thumbnail.png)](docs/sarojini_naidu_intro.mp4)

*Click the thumbnail to watch the generated video.*

---

## Prerequisites

- Python 3.12 
- Windows 10/11
- Internet connection
- Free Groq API key (takes 2 minutes to get)

---

## Quick Setup

### Step 1: Clone / Download the project

```bash
# If you have git:

git clone https://github.com/AyushMayekar/An-End-to-End-AI-Based-System-for-Automated-Video-Generation-Using-Text-Speech-and-Image-Synthesis.git

cd An-End-to-End-AI-Based-System-for-Automated-Video-Generation-Using-Text-Speech-and-Image-Synthesis

# Or just download and extract the ZIP
```

### Step 2: Create a virtual environment

```bash
# Open Command Prompt or PowerShell
pip install uv
uv venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
uv sync
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
uv run python main.py "Bhagat Singh"
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
---

## Running the Pipeline

### Basic Usage

```bash
# Default fighter from .env
uv run python main.py

# Specify a fighter
uv run python main.py "Rani Lakshmibai"
uv run python main.py "Subhas Chandra Bose"
uv run python main.py "Chandra Shekhar Azad"
```

### Advanced Options

```bash
# Generate more frames for smoother video
uv run python main.py "Bhagat Singh" --images 8

# Skip regenerating images (reuse existing ones)
uv run python main.py "Bhagat Singh" --skip-images

# See list of suggested freedom fighters
uv run python main.py --list-fighters
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
| `LLM_PROVIDER` | `groq` | `groq` | LLM for script generation |
| `TTS_PROVIDER` | `gtts` | `gtts` | Text-to-speech engine |
| `IMAGE_PROVIDER` | `pollinations` | `pollinations`| Image generation service |
| `IMAGE_COUNT` | `5` | `3`-`10` | Number of video frames |
| `VIDEO_RESOLUTION` | `720p` | `480p`, `720p`, `1080p` | Output video resolution |
| `VIDEO_FPS` | `24` | Any positive integer | Number of frames rendered per second |
| `VIDEO_END_BUFFER` | `0.5` | `0.0`–`2.0` seconds | Additional time added after narration completion for smoother endings and outro transitions |

---

## Prompt Engineering Strategy

### Script Prompt Design

The narration prompt uses a **5-layer engineering approach**:

1. **Role Assignment**: *"You are an award-winning documentary narrator specializing in Indian history..."*, shifts the model toward authoritative, cinematic storytelling instead of generic encyclopedic output.

2. **Context Anchoring**: Explicitly grounds the model in the Indian freedom movement and historical documentary domain, improving factual relevance and reducing hallucinations.

3. **Format Constraint**: *"Output EXACTLY 15 words"* and *"Use a SINGLE sentence only"*, maps precisely to a ~10-second narration window while enforcing concise, high-impact storytelling.

4. **Negative Constraint**: *"No titles, notes, explanations, quotes, markdown, emojis, or bullet points"*, prevents the model's default tendency toward structured or conversational responses.

5. **Quality Anchor**: *"Maintain a respectful, authoritative BBC documentary tone"*, references a recognizable narrative standard to improve consistency, emotional impact, and output quality.

### Image Prompt Design

Each image prompt follows a **5-component structure**:

```text
[Subject Priority] + [Historical Context] + [Narrative Beat] + [Composition & Mood] + [Technical Style]
```

Every prompt includes three global constraints:

* **Subject Consistency**: The freedom fighter remains the dominant focal point across all frames with consistent facial features, attire, age, and expression.
* **Historical Authenticity**: All visuals are grounded in 1920s–1940s British colonial India using period-accurate settings, clothing, and symbolism.
* **Negative Prompting**: Modern objects, text overlays, distorted anatomy, low-quality outputs, and stylistic inconsistencies are explicitly prohibited.

The 5 images map to a **visual narrative arc**:

* **Frame 1 (0–2s): Iconic Portrait**: establish identity and emotional connection.
* **Frame 2 (2–4s): Historical Context**: situate the subject within the Indian independence movement.
* **Frame 3 (4–6s): Defining Moment**: depict their most significant contribution or sacrifice.
* **Frame 4 (6–8s): Legacy**: symbolize the values and ideals they represent.
* **Frame 5 (8–10s): Remembrance**: conclude with a respectful tribute to their enduring impact.

---

This prompt architecture ensures that narration, visuals, and timing remain tightly aligned, producing historically grounded, emotionally engaging, and visually coherent short-form videos.


## Troubleshooting

### "GROQ_API_KEY is not set"
→ Add your key to `.env`. Get it free at https://console.groq.com

### "gTTS request failed"
→ Check your internet connection. gTTS requires internet access.

### "Pollinations returned 503"
→ Pollinations.ai is sometimes slow. The code retries automatically.
→ Wait 30 seconds and try again.

### "moviepy not found" or video assembly fails
```bash
uv add moviepy imageio-ffmpeg
```

### "No module named 'PIL'"
```bash
uv add Pillow
```

### Images look wrong / placeholder images appear
→ Pollinations.ai may be rate-limiting. Wait 1-2 minutes and re-run with `--skip-audio`.


---

## Project Structure

> Note: The `assets/` directory is created automatically during the first run if it does not already exist.

```text
An-End-to-End-AI-Based-System-for-Automated-Video-Generation-Using-Text-Speech-and-Image-Synthesis/
├── README.md                     ← Project overview, setup instructions, and usage guide
├── main.py                       ← Application entry point; orchestrates the entire pipeline
├── pyproject.toml                ← Project metadata and dependency definitions for uv
├── uv.lock                       ← Locked dependency versions for reproducible environments
├── .env.example                  ← Template for required environment variables
│
├── config/
│   ├── __init__.py
│   └── settings.py               ← Centralized configuration (API keys, paths, models, settings)
│
├── prompts/
│   ├── __init__.py
│   └── prompt_templates.py       ← All narration, image, and overlay prompt templates
│
├── src/
│   ├── __init__.py
│   ├── text_gen.py               ← Module 1: Narration script generation (Groq)
│   ├── audio_gen.py              ← Module 2: Text-to-speech generation (gTTS)
│   ├── image_gen.py              ← Module 3: Historical image generation (Pollinations.ai)
│   └── video_gen.py              ← Module 4: Video assembly and rendering (MoviePy)
│
├── tests/
│   └── test_pipeline.py          ← End-to-end validation and integration tests
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py             ← File system helpers and asset management utilities
│   └── logger.py                 ← Structured, colorized logging configuration
│
└── assets/
    ├── images/                   ← Generated image frames (frame_01.jpg ... frame_05.jpg)
    ├── audio/                    ← Generated narration audio files (.mp3)
    ├── music/                    ← Optional background music assets
    └── output/                   ← Final rendered videos (.mp4)
```
---

## Testing

Run the validation suite before generating videos:

```bash
uv run python tests/test_pipeline.py
```

The test suite verifies:

- Configuration loading
- API connectivity
- Dependency installation
- Audio generation
- Image generation
- End-to-end pipeline components
---

*Built for the AI Video Generation Assignment — Zero cost, maximum quality.*
