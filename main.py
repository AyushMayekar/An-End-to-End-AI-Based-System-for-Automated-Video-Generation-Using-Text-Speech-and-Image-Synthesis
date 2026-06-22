"""
Entry point for the complete pipeline. Runs all 4 modules in sequence
with progress tracking, error handling, and final summary.

Usage:
    uv run python main.py                          # Uses .env settings
    uv run python main.py "Rani Lakshmibai"        # Override fighter name
    uv run python main.py --list-fighters          # Show example fighters
"""

import argparse
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 10-second AI video introducing an Indian freedom fighter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python main.py
  uv run python main.py "Bhagat Singh"
  uv run python main.py "Subhas Chandra Bose" --images 4
  uv run python main.py --list-fighters
        """,
    )
    parser.add_argument(
        "fighter_name",
        nargs="?",
        default=None,
        help="Name of the Indian freedom fighter (default: from .env)",
    )
    parser.add_argument(
        "--tts",
        choices=["gtts"],
        default=None,
        help="Override TTS provider",
    )
    parser.add_argument(
        "--images",
        type=int,
        default=None,
        help="Override number of images to generate (default: 5)",
    )
    parser.add_argument(
        "--llm",
        choices=["groq"],
        default=None,
        help="Override LLM provider",
    )
    parser.add_argument(
        "--image-provider",
        choices=["pollinations"],
        default=None,
        help="Override image generation provider",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip image generation (use existing images in assets/images/)",
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip audio generation (use existing audio in assets/audio/)",
    )
    parser.add_argument(
        "--list-fighters",
        action="store_true",
        help="Print a list of suggested Indian freedom fighters and exit",
    )
    return parser.parse_args()


def list_suggested_fighters() -> None:
    fighters = [
        "Bhagat Singh       — Revolutionary, martyr, hanged at 23",
        "Rani Lakshmibai    — Warrior queen of Jhansi",
        "Subhas Chandra Bose — Netaji, INA founder",
        "Bal Gangadhar Tilak — 'Swaraj is my birthright'",
        "Sarojini Naidu     — Nightingale of India",
        "Mangal Pandey      — Spark of the 1857 revolt",
        "Ashfaqulla Khan    — Kakori conspiracy hero",
        "Udham Singh        — Avenged Jallianwala Bagh",
        "Lala Lajpat Rai    — Punjab Kesari",
        "Chandra Shekhar Azad — 'Never be caught alive'",
    ]
    print("\nSuggested Indian Freedom Fighters:")
    print("─" * 55)
    for f in fighters:
        print(f"  {f}")
    print("─" * 55)
    print("\nUsage: uv run python main.py \"Fighter Name\"\n")


def print_banner() -> None:
    print("""
╔══════════════════════════════════════════════════════════╗
║     Freedom Fighter Video Generator                      ║
║     AI-Powered | CPU-Friendly | Zero Cost                ║
╚══════════════════════════════════════════════════════════╝
    """)


def print_step(step_num: int, total: int, name: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  Step {step_num}/{total}: {name}")
    print(f"{'─' * 60}")


def print_summary(
    fighter_name: str,
    script: str,
    audio_path: Path,
    image_paths: list[Path],
    video_path: Path,
    total_time: float,
) -> None:
    from utils.file_utils import file_size_mb

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                  ✅  Pipeline Complete!                  ║
╚══════════════════════════════════════════════════════════╝

  Subject:    {fighter_name}
  Script:     {len(script.split())} words
  Audio:      {audio_path.name}
  Images:     {len(image_paths)} frames
  Video:      {video_path.name}
  Size:       {file_size_mb(video_path):.1f} MB
  Total time: {total_time:.0f} seconds

  📁 Output: {video_path}

  🎬 Your video is ready! Open it to review.
    """)


def main() -> None:
    args = parse_args()

    if args.list_fighters:
        list_suggested_fighters()
        sys.exit(0)

    print_banner()

    # ── Apply CLI overrides to settings ───────────────────────────────────────
    import config.settings as cfg

    if args.fighter_name:
        cfg.FREEDOM_FIGHTER_NAME = args.fighter_name
        # Update dependent path settings
        safe_name = cfg._safe_name(args.fighter_name)
        cfg.SCRIPT_FILE = cfg.ASSETS_DIR / f"{safe_name}_script.txt"
        cfg.AUDIO_FILE = cfg.AUDIO_DIR / f"{safe_name}_narration.mp3"
        cfg.OUTPUT_VIDEO = cfg.OUTPUT_DIR / f"{safe_name}_intro.mp4"

    if args.tts:
        cfg.TTS_PROVIDER = args.tts
    if args.images:
        cfg.IMAGE_COUNT = args.images
    if args.llm:
        cfg.LLM_PROVIDER = args.llm
    if args.image_provider:
        cfg.IMAGE_PROVIDER = args.image_provider

    fighter_name = cfg.FREEDOM_FIGHTER_NAME
    print(f"  Subject: {fighter_name}")
    print(f"  LLM:     {cfg.LLM_PROVIDER} → {cfg.GROQ_MODEL}")
    print(f"  TTS:     {cfg.TTS_PROVIDER}")
    print(f"  Images:  {cfg.IMAGE_COUNT} frames via {cfg.IMAGE_PROVIDER}")
    print(f"  Output:  {cfg.VIDEO_RESOLUTION[0]}×{cfg.VIDEO_RESOLUTION[1]} @ {cfg.VIDEO_FPS}fps")

    # ── Validate config ────────────────────────────────────────────────────────
    try:
        cfg.validate()
    except EnvironmentError as e:
        print(f"\n❌ Configuration Error: {e}")
        sys.exit(1)

    from utils.logger import log

    pipeline_start = time.time()
    total_steps = 4

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 1: Generate Script
    # ═══════════════════════════════════════════════════════════════════════════
    print_step(1, total_steps, "Generating narration script")
    try:
        from src.text_gen import generate_script
        script = generate_script(fighter_name)
        print(f"\n📝 Generated Script Preview:")
        preview = " ".join(script.split()[:15])
        print(f"   {preview}...")
        print(f"   ({len(script.split())} words)")
    except Exception as e:
        log.error(f"Script generation failed: {e}")
        print(f"\n❌ Script generation failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your GROQ_API_KEY in .env")
        print("   2. Visit https://console.groq.com to verify your key")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 2: Generate Audio
    # ═══════════════════════════════════════════════════════════════════════════
    print_step(2, total_steps, f"Generating audio ({cfg.TTS_PROVIDER})")
    try:
        if args.skip_audio and cfg.AUDIO_FILE.exists():
            log.info(f"Skipping audio generation. Using: {cfg.AUDIO_FILE}")
            audio_path = cfg.AUDIO_FILE
        else:
            from src.audio_gen import generate_audio, get_audio_duration
            audio_path = generate_audio(script)
            duration = get_audio_duration(audio_path)
            print(f"   Duration: {duration:.1f} seconds")
    except Exception as e:
        log.error(f"Audio generation failed: {e}")
        print(f"\n❌ Audio generation failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure you have internet access (gTTS requires internet)")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3: Generate Images
    # ═══════════════════════════════════════════════════════════════════════════
    print_step(3, total_steps, f"Generating {cfg.IMAGE_COUNT} images ({cfg.IMAGE_PROVIDER})")
    try:
        if args.skip_images:
            from utils.file_utils import list_images
            image_paths = list_images(cfg.IMAGES_DIR)
            if not image_paths:
                raise FileNotFoundError(
                    f"No images found in {cfg.IMAGES_DIR}. "
                    "Remove --skip-images to generate them."
                )
            log.info(f"Skipping image generation. Found {len(image_paths)} existing images.")
        else:
            from src.image_gen import generate_images
            image_paths = generate_images(fighter_name)
    except Exception as e:
        log.error(f"Image generation failed: {e}")
        print(f"\n❌ Image generation failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Pollinations.ai may be slow or down. Try again in a minute.")
        print("   2. Check your internet connection.")
        print("   3. Placeholder images will be used if generation fails.")
        # Don't exit — placeholder images allow pipeline to continue
        from utils.file_utils import list_images
        image_paths = list_images(cfg.IMAGES_DIR)
        if not image_paths:
            sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 4: Assemble Video
    # ═══════════════════════════════════════════════════════════════════════════
    print_step(4, total_steps, "Assembling final video")
    print("   ⏳ This is the slowest step (~1-3 min on CPU). Please wait...")
    try:
        from src.video_gen import assemble_video
        video_path = assemble_video(
            image_paths=image_paths,
            audio_path=audio_path,
            fighter_name=fighter_name,
        )
    except Exception as e:
        log.error(f"Video assembly failed: {e}")
        print(f"\n❌ Video assembly failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure moviepy is installed: uv add moviepy")
        print("   2. Ensure ffmpeg is available: uv add imageio-ffmpeg")
        print("   3. Check that all images and audio files exist.")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════════
    # DONE
    # ═══════════════════════════════════════════════════════════════════════════
    total_time = time.time() - pipeline_start
    print_summary(fighter_name, script, audio_path, image_paths, video_path, total_time)


if __name__ == "__main__":
    main()
