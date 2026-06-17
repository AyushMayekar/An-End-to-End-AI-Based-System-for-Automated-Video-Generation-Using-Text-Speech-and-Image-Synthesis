"""
src/video_gen.py
──────────────────
Module 4: Video Assembly via MoviePy

WHAT:  Assembles images + audio + text overlays into the final MP4 video.

"""

from __future__ import annotations 
import os
import time
from pathlib import Path

from config import settings
from utils.logger import log
from utils.file_utils import list_images
from moviepy import ( AudioFileClip, CompositeVideoClip, ImageClip, VideoClip, concatenate_videoclips, vfx )


def assemble_video(
    image_paths: list[Path],
    audio_path: Path,
    output_path: Path | None = None,
    fighter_name: str | None = None,
) -> Path:
    """
    Assemble the final video from images and audio.

    Args:
        image_paths:  List of image file paths in frame order.
        audio_path:   Path to the narration audio file.
        output_path:  Where to save the output MP4.
        fighter_name: Name for the title card overlay.

    Returns:
        Path to the final generated video.
    """
    output_path = output_path or settings.OUTPUT_VIDEO
    fighter_name = fighter_name or settings.FREEDOM_FIGHTER_NAME

    log.info("🎬 Assembling final video...")
    log.info(f"  Images: {len(image_paths)} frames")
    log.info(f"  Audio:  {audio_path}")
    log.info(f"  Output: {output_path}")


    start = time.time()

    # ── Step 1: Load audio and determine total duration ────────────────────────
    log.debug("Loading audio clip...")
    audio_clip = AudioFileClip(str(audio_path))
    total_duration = audio_clip.duration
    log.info(f"  Audio duration: {total_duration:.1f}s")
    CROSSFADE_DURATION = 0.3  # seconds
    video_duration = total_duration + settings.VIDEO_END_BUFFER

    # ── Step 2: Calculate per-image duration ──────────────────────────────────
    n_images = len(image_paths)
    effective_duration = (
    video_duration
    + CROSSFADE_DURATION * (n_images - 1)
    )
    seconds_per_image = effective_duration/ n_images
    log.debug(f"  Duration per image: {seconds_per_image:.2f}s")

    # ── Step 3: Create image clips with Ken Burns effect ──────────────────────
    log.debug("Creating image clips with Ken Burns effect...")
    image_clips = []

    for i, img_path in enumerate(image_paths):
        clip = _create_image_clip_with_kenburns(
            img_path=img_path,
            duration=seconds_per_image,
            frame_index=i,
            resolution=settings.VIDEO_RESOLUTION,
        )
        image_clips.append(clip)

    # ── Step 4: Concatenate with crossfade transitions ─────────────────────────
    log.debug("Concatenating clips with crossfade transitions...")

    final_clips = []
    for i, clip in enumerate(image_clips):
        effects = []
        if i == 0: 
            effects.append(vfx.FadeIn(0.05)) 
        if i == len(image_clips) - 1: 
            effects.append(vfx.FadeOut(0.5)) 
        if i > 0: 
            effects.append(vfx.CrossFadeIn(CROSSFADE_DURATION)) 
        if effects: 
            clip = clip.with_effects(effects)

        final_clips.append(clip)

    # Use crossfade-aware concatenation
    video = concatenate_videoclips(
        final_clips,
        method="compose",
        padding=-CROSSFADE_DURATION,  # Negative padding creates crossfade overlap
    )

    # ── Step 5: Add title card overlay ────────────────────────────────────────
    log.debug("Adding title card overlays...")
    title_overlay = _create_title_overlay(
        fighter_name=fighter_name,
        resolution=settings.VIDEO_RESOLUTION,
        show_start=0.3,
        show_duration=2.5,
    )

    # ── Step 6: Add outro overlay ─────────────────────────────────────────────
    outro_overlay = _create_outro_overlay(
        resolution=settings.VIDEO_RESOLUTION,
        video_duration=video.duration,
        show_duration=2.0,
    )

    # ── Step 7: Composite all layers ──────────────────────────────────────────
    log.debug("Compositing all layers...")
    all_layers = [video]
    if title_overlay:
        all_layers.append(title_overlay)
    if outro_overlay:
        all_layers.append(outro_overlay)

    log.debug(f"video.duration = {video.duration}")

    if title_overlay:
        log.debug(f"title_overlay.duration = {title_overlay.duration}")

    if outro_overlay:
        log.debug(f"outro_overlay.duration = {outro_overlay.duration}")


    final_video = CompositeVideoClip(all_layers)
    final_video = final_video.with_duration(video.duration)
    log.debug(f"final_video.duration = {final_video.duration}")

    # ── Step 8: Attach audio ───────────────────────────────────────────────────
    log.debug("Attaching audio...")

    required_duration = (
        audio_clip.duration + settings.VIDEO_END_BUFFER
    )

    if final_video.duration < required_duration:
        log.warning(
            f"Extending video duration from "
            f"{final_video.duration:.2f}s to "
            f"{required_duration:.2f}s"
        )

        final_video = final_video.with_duration(required_duration)

    final_video = final_video.with_audio(audio_clip)
    # ── Step 9: Export ─────────────────────────────────────────────────────────
    log.info("Exporting final video (this may take 1-3 minutes on CPU)...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_video.write_videofile(
        str(output_path),
        fps=settings.VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",        # Balance between speed and quality
        ffmpeg_params=[
            "-crf", "23",       # Quality level (18=best, 28=worst, 23=default)
            "-movflags", "+faststart",  # Enable streaming/web playback
        ],
        logger=None,            # Suppress MoviePy's verbose ffmpeg logs
    )

    elapsed = time.time() - start
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    log.info(f"✅ Video exported!")
    log.info(f"   Path:     {output_path}")
    log.info(f"   Size:     {file_size_mb:.1f} MB")
    log.info(f"   Duration: {final_video.duration:.1f}s")
    log.info(f"   Time:     {elapsed:.0f}s to render")

    # Cleanup MoviePy clips to free memory
    audio_clip.close()
    final_video.close()

    return output_path


# ── Ken Burns Effect ───────────────────────────────────────────────────────────

def _create_image_clip_with_kenburns(
    img_path: Path,
    duration: float,
    frame_index: int,
    resolution: tuple[int, int],
) -> ImageClip:
    from PIL import Image
    import numpy as np

    width, height = resolution

    # Load and resize image to video resolution
    with Image.open(img_path) as img:
        img = img.convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
        img_array = np.array(img)

    zoom_direction = "in" if frame_index % 2 == 0 else "out"
    zoom_intensity = 0.05  # 5% zoom — subtle but visible

    def make_frame(t: float):
        """Generate frame at time t with zoom applied."""
        progress = t / duration  # 0.0 to 1.0

        if zoom_direction == "in":
            zoom = 1.0 + (zoom_intensity * progress)
        else:
            zoom = (1.0 + zoom_intensity) - (zoom_intensity * progress)

        # Calculate crop dimensions for zoom effect
        crop_w = int(width / zoom)
        crop_h = int(height / zoom)

        # Center crop
        x_offset = (width - crop_w) // 2
        y_offset = (height - crop_h) // 2

        # Crop and resize back to target size
        cropped = img_array[
            y_offset : y_offset + crop_h,
            x_offset : x_offset + crop_w,
        ]
        resized = np.array(
            Image.fromarray(cropped).resize((width, height), Image.LANCZOS)
        )
        return resized


    # Replace with animated version
    animated_clip = VideoClip( frame_function=make_frame, duration=duration, ).with_fps(settings.VIDEO_FPS)
    return animated_clip


# ── Text Overlay (PIL-based, no ImageMagick needed) ───────────────────────────

def _create_title_overlay(
    fighter_name: str,
    resolution: tuple[int, int],
    show_start: float,
    show_duration: float,
) -> ImageClip | None:
    """
    Create a title card overlay using PIL — no ImageMagick dependency.

    Shows fighter name in large text at the bottom of the frame,
    with a semi-transparent background strip for readability.
    Fades in and fades out gracefully.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        width, height = resolution

        # Create transparent RGBA canvas
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # Semi-transparent bottom strip
        strip_height = int(height * 0.18)
        strip_y = height - strip_height - int(height * 0.05)
        draw.rectangle(
            [(0, strip_y), (width, strip_y + strip_height)],
            fill=(0, 0, 0, 160),  # Black, 63% opacity
        )

        # Load font — try system fonts, fall back to default
        font_size = int(height * 0.06)
        subtitle_size = int(height * 0.03)
        main_font = _get_font(font_size)
        sub_font = _get_font(subtitle_size)

        # Main title text
        title_text = fighter_name.upper()
        text_bbox = draw.textbbox((0, 0), title_text, font=main_font)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = (width - text_w) // 2
        text_y = strip_y + int(strip_height * 0.1)

        # Text shadow for readability
        draw.text((text_x + 2, text_y + 2), title_text, font=main_font, fill=(0, 0, 0, 200))
        draw.text((text_x, text_y), title_text, font=main_font, fill=(255, 153, 51, 255))  # Saffron

        # Subtitle
        subtitle_text = "Indian Freedom Fighter"
        sub_bbox = draw.textbbox((0, 0), subtitle_text, font=sub_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_x = (width - sub_w) // 2
        sub_y = text_y + int(font_size * 1.1)
        draw.text((sub_x, sub_y), subtitle_text, font=sub_font, fill=(220, 220, 220, 200))

        # Convert to numpy array for MoviePy
        rgba_array = np.array(canvas)

        clip = ImageClip(rgba_array, transparent=True)

        clip = clip.with_duration(show_duration)
        clip = clip.with_start(show_start)
        clip = clip.with_opacity(0.95)

        clip = clip.with_effects([
            vfx.FadeIn(0.4),
            vfx.FadeOut(0.4),
        ])

        log.debug(f"title clip duration: {clip.duration}")
        log.debug("Title overlay created successfully.")
        return clip

    except Exception as e:
        log.warning(f"Could not create title overlay: {e}. Skipping.")
        return None


def _create_outro_overlay(
    resolution: tuple[int, int],
    video_duration: float,
    show_duration: float,
) -> ImageClip | None:
    """
    Create 'Jai Hind 🇮🇳' outro text overlay for the final seconds.
    """
    try:
        from PIL import Image, ImageDraw
        import numpy as np

        width, height = resolution
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        font_size = int(height * 0.05)
        font = _get_font(font_size)

        text = "JAI HIND!!!"
        font_size = int(height * 0.2)
        text_bbox = draw.textbbox((0, 0), text, font=font)

        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        text_x = (width - text_w) // 2
        text_y = (height - text_h) // 2

        draw.text((text_x + 2, text_y + 2), text, font=font, fill=(0, 0, 0, 150))
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 230))

        rgba_array = np.array(canvas)
        show_start = max(0, video_duration - show_duration - 0.2)
        clip = ImageClip(rgba_array, transparent=True)

        clip = clip.with_duration(show_duration)
        clip = clip.with_start(show_start)
        clip = clip.with_opacity(0.95)

        clip = clip.with_effects([
            vfx.FadeIn(0.4),
            vfx.FadeOut(0.4),
        ])

        log.debug(f"outro clip duration: {clip.duration}")
        return clip

    except Exception as e:
        log.warning(f"Could not create outro overlay: {e}. Skipping.")
        return None


def _get_font(size: int):
    """Try to load a good font. Fall back to PIL default if none available."""
    from PIL import ImageFont

    font_candidates = [
        "arialbd.ttf",   # Windows Arial Bold
        "arial.ttf",     # Windows Arial
        "calibrib.ttf",  # Windows Calibri Bold
        "DejaVuSans-Bold.ttf",  # Linux
        "Helvetica.ttc", # macOS
    ]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except (IOError, OSError):
            continue

    # Ultimate fallback — PIL built-in default font
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    print("Testing video assembly with existing assets...")
    images = list_images(settings.IMAGES_DIR)
    if not images:
        print("No images found. Run image_gen.py first.")
        sys.exit(1)

    if not settings.AUDIO_FILE.exists():
        print("No audio file found. Run audio_gen.py first.")
        sys.exit(1)

    output = assemble_video(images, settings.AUDIO_FILE)
    print(f"Video created: {output}")
