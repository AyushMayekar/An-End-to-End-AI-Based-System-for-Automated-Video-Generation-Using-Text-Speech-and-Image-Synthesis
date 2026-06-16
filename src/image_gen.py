"""
src/image_gen.py
──────────────────
Module 3: AI Image Generation

WHAT:  Generates 5 historically-styled images for the video frames.
WHY:   Images provide the visual narrative. Each image maps to a ~2-second
       "beat" in the video. Quality here directly impacts final output quality.
HOW:   Primary: Pollinations.ai — 100% free, no API key, no rate limit signup.
                Just a GET request with a text prompt. Incredible for free tier.
       Alt 1:  Stability AI free tier — higher quality, requires API key.
       Alt 2:  Hugging Face Inference API — free tier, slower, many models.

COMMON PITFALLS:
  - Pollinations.ai can be slow (5-15s per image). Add retries.
  - Generated faces can be inconsistent across frames. The prompts are designed
    to minimize this by including clear descriptor anchors.
  - Always save images with sequential numbered names for video assembly order.
"""

import time
import urllib.parse
from pathlib import Path
from config import settings
from prompts.prompt_templates import get_image_prompts
from utils.logger import log


def generate_images(fighter_name: str | None = None) -> list[Path]:
    """
    Generate all images for the video.

    Args:
        fighter_name: Name of the freedom fighter.

    Returns:
        List of Paths to generated image files, in frame order.
    """
    fighter_name = fighter_name or settings.FREEDOM_FIGHTER_NAME
    image_prompts = get_image_prompts(fighter_name, "", settings.IMAGE_COUNT)

    log.info(f"🎨 Generating {len(image_prompts)} images via: {settings.IMAGE_PROVIDER}")
    image_paths = []

    for i, prompt_data in enumerate(image_prompts, 1):
        log.info(f"  Image {i}/{len(image_prompts)}: {prompt_data['beat']}")
        output_path = settings.IMAGES_DIR / f"frame_{i:02d}.jpg"

        if settings.IMAGE_PROVIDER == "pollinations":
            path = _generate_with_pollinations(
                prompt_data["positive"],
                output_path,
                attempt=i,
            )
        elif settings.IMAGE_PROVIDER == "stability":
            path = _generate_with_stability(
                prompt_data["positive"],
                prompt_data["negative"],
                output_path,
            )
        elif settings.IMAGE_PROVIDER == "huggingface":
            path = _generate_with_huggingface(
                prompt_data["positive"],
                output_path,
            )
        else:
            raise ValueError(f"Unknown image provider: {settings.IMAGE_PROVIDER}")

        image_paths.append(path)
        log.info(f"  ✅ Saved → {path.name}")

    log.info(f"✅ All {len(image_paths)} images generated.")
    return image_paths


# ── Pollinations.ai Implementation ────────────────────────────────────────────

def _generate_with_pollinations(
    prompt: str,
    output_path: Path,
    attempt: int = 1,
    max_retries: int = 3,
) -> Path:
    """
    Pollinations.ai: Completely free image generation via HTTP GET.
    URL format: https://image.pollinations.ai/prompt/{encoded_prompt}

    Parameters appended as query string:
      - width, height: Image dimensions
      - seed: For reproducibility (use frame number for variety)
      - model: "flux" gives best quality on Pollinations
      - nologo: Remove Pollinations watermark
      - enhance: Auto-enhance prompt quality

    PITFALL: Sometimes returns a 503. Retry with exponential backoff.
    """
    import requests

    encoded_prompt = urllib.parse.quote(prompt)
    url = (
        f"{settings.POLLINATIONS_BASE_URL}/{encoded_prompt}"
        f"?width={settings.IMAGE_WIDTH}"
        f"&height={settings.IMAGE_HEIGHT}"
        f"&seed={attempt * 42}"
        f"&model=flux"
        f"&nologo=true"
        f"&enhance=true"
    )

    for retry in range(max_retries):
        try:
            log.debug(f"  Pollinations request (try {retry + 1}/{max_retries})...")
            response = requests.get(url, timeout=60)

            if response.status_code == 200 and response.headers.get(
                "content-type", ""
            ).startswith("image/"):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(response.content)
                return output_path
            else:
                log.warning(
                    f"  Pollinations returned {response.status_code}. Retrying..."
                )
                time.sleep(2 ** retry)  # Exponential backoff: 1s, 2s, 4s

        except requests.exceptions.Timeout:
            log.warning(f"  Pollinations timed out (try {retry + 1}). Retrying...")
            time.sleep(2 ** retry)
        except Exception as e:
            log.error(f"  Pollinations error: {e}")
            time.sleep(2 ** retry)

    # If all retries fail, create a placeholder image
    log.warning(f"  All retries failed. Creating placeholder image for frame {attempt}.")
    return _create_placeholder_image(output_path, attempt)


# ── Stability AI Implementation ────────────────────────────────────────────────

def _generate_with_stability(
    positive_prompt: str,
    negative_prompt: str,
    output_path: Path,
) -> Path:
    """
    Stability AI: Higher quality images, free tier available.
    Free tier: 25 credits/month (~25 images at default settings).
    API docs: https://platform.stability.ai/docs/api-reference

    Install: pip install stability-sdk  OR use requests directly
    """
    import requests

    if not settings.STABILITY_API_KEY:
        raise EnvironmentError(
            "STABILITY_API_KEY not set. "
            "Add it to .env or switch IMAGE_PROVIDER to pollinations."
        )

    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {
        "text_prompts": [
            {"text": positive_prompt, "weight": 1.0},
            {"text": negative_prompt, "weight": -1.0},  # Negative prompt
        ],
        "cfg_scale": 7,
        "width": min(settings.IMAGE_WIDTH, 1024),   # SDXL max is 1024
        "height": min(settings.IMAGE_HEIGHT, 1024),
        "samples": 1,
        "steps": 30,
    }

    response = requests.post(url, headers=headers, json=body, timeout=60)
    response.raise_for_status()

    import base64
    image_data = response.json()["artifacts"][0]["base64"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(image_data))
    return output_path


# ── Hugging Face Implementation ────────────────────────────────────────────────

def _generate_with_huggingface(prompt: str, output_path: Path) -> Path:
    """
    Hugging Face Inference API: Free tier available.
    Uses stabilityai/stable-diffusion-2-1 model.
    Free tier: Rate-limited but functional for occasional use.

    Get token: https://huggingface.co/settings/tokens (free account)
    """
    import requests

    hf_token = os.environ.get("HF_API_TOKEN", "")
    api_url = (
        "https://api-inference.huggingface.co/models/"
        "stabilityai/stable-diffusion-2-1"
    )
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    payload = {"inputs": prompt}

    response = requests.post(api_url, headers=headers, json=payload, timeout=90)

    if response.status_code == 503:
        # Model is loading — wait and retry
        log.warning("  HuggingFace model loading. Waiting 20s...")
        time.sleep(20)
        response = requests.post(api_url, headers=headers, json=payload, timeout=90)

    response.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    return output_path


# ── Placeholder Image Fallback ─────────────────────────────────────────────────

def _create_placeholder_image(output_path: Path, frame_num: int) -> Path:
    """
    Create a visually acceptable placeholder image when generation fails.
    Uses PIL/Pillow to create a gradient image with frame text.
    This ensures the video pipeline never breaks due to image failures.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        width, height = settings.IMAGE_WIDTH, settings.IMAGE_HEIGHT

        # Create gradient background (saffron to deep blue — Indian flag colors)
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            ratio = y / height
            # Saffron (#FF9933) to Navy (#000080)
            img_array[y, :, 0] = int(255 * (1 - ratio))   # R
            img_array[y, :, 1] = int(153 * (1 - ratio))   # G
            img_array[y, :, 2] = int(51 * (1 - ratio) + 128 * ratio)  # B

        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)

        # Add text
        text = f"Frame {frame_num}"
        draw.text(
            (width // 2, height // 2),
            text,
            fill=(255, 255, 255),
            anchor="mm",
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "JPEG", quality=95)
        log.info(f"  Placeholder image created: {output_path.name}")
        return output_path

    except Exception as e:
        log.error(f"  Could not create placeholder: {e}")
        raise


import os  # Needed for HuggingFace token lookup above


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    fighter = sys.argv[1] if len(sys.argv) > 1 else "Bhagat Singh"
    paths = generate_images(fighter)
    print(f"\nGenerated {len(paths)} images:")
    for p in paths:
        print(f"  {p}")
