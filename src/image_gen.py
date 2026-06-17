"""
src/image_gen.py
──────────────────
Module 3: AI Image Generation

WHAT:  Generates 5 historically-styled images for the video frames.
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

    Parameters appended as query string:
      - width, height: Image dimensions
      - seed: For reproducibility (use frame number for variety)
      - model: "flux" gives best quality on Pollinations
      - nologo: Remove Pollinations watermark
      - enhance: Auto-enhance prompt quality

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


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    fighter = sys.argv[1] if len(sys.argv) > 1 else "Bhagat Singh"
    paths = generate_images(fighter)
    print(f"\nGenerated {len(paths)} images:")
    for p in paths:
        print(f"  {p}")
