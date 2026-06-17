"""
tests/test_pipeline.py
───────────────────────
Phase 7: Testing and Validation

Run with: python tests/test_pipeline.py

Tests each module independently so you can identify failures before
running the full pipeline. Each test is self-contained and minimal.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# Test Utilities
# ─────────────────────────────────────────────────────────────────────────────

PASSED = 0
FAILED = 0
SKIPPED = 0


def test(name: str):
    """Decorator for test functions."""
    def decorator(func):
        def wrapper():
            global PASSED, FAILED, SKIPPED
            print(f"\n  🧪 {name}...", end="", flush=True)
            try:
                result = func()
                if result == "SKIP":
                    print(f" ⏭️  SKIPPED")
                    SKIPPED += 1
                else:
                    print(f" ✅ PASSED")
                    PASSED += 1
            except Exception as e:
                print(f" ❌ FAILED")
                print(f"     Error: {e}")
                FAILED += 1
        return wrapper
    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# Config Tests
# ─────────────────────────────────────────────────────────────────────────────

@test("Config: settings load without errors")
def test_config_loads():
    from config import settings
    assert settings.FREEDOM_FIGHTER_NAME, "Fighter name should not be empty"
    assert settings.VIDEO_RESOLUTION == (1280, 720) or settings.VIDEO_RESOLUTION in [
        (854, 480), (1920, 1080)
    ], "Invalid resolution"


@test("Config: asset directories exist")
def test_directories_exist():
    from config import settings
    for d in [settings.IMAGES_DIR, settings.AUDIO_DIR, settings.OUTPUT_DIR]:
        assert d.exists(), f"Directory missing: {d}"


@test("Config: GROQ_API_KEY is set")
def test_groq_key():
    from config import settings
    if not settings.GROQ_API_KEY:
        raise AssertionError(
            "GROQ_API_KEY not set in .env. "
            "Get a free key at https://console.groq.com"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Import Tests
# ─────────────────────────────────────────────────────────────────────────────

@test("Imports: groq package available")
def test_groq_import():
    try:
        import groq
    except ImportError:
        raise ImportError("groq not installed. Run: pip install groq")


@test("Imports: gTTS package available")
def test_gtts_import():
    try:
        from gtts import gTTS
    except ImportError:
        raise ImportError("gTTS not installed. Run: pip install gTTS")


@test("Imports: moviepy package available")
def test_moviepy_import():
    try:
        from moviepy import ImageClip, AudioFileClip
    except ImportError:
        raise ImportError("moviepy not installed. Run: pip install moviepy")


@test("Imports: Pillow (PIL) package available")
def test_pillow_import():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise ImportError("Pillow not installed. Run: pip install Pillow")


@test("Imports: requests package available")
def test_requests_import():
    try:
        import requests
    except ImportError:
        raise ImportError("requests not installed. Run: pip install requests")


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Tests
# ─────────────────────────────────────────────────────────────────────────────

@test("Prompts: script prompt generates correctly")
def test_script_prompt():
    from prompts.prompt_templates import get_script_prompt
    prompt = get_script_prompt("Bhagat Singh")
    assert "system" in prompt, "Missing system key"
    assert "user" in prompt, "Missing user key"
    assert "Bhagat Singh" in prompt["user"], "Fighter name not in prompt"
    assert len(prompt["system"]) > 50, "System prompt too short"
    assert len(prompt["user"]) > 50, "User prompt too short"


@test("Prompts: image prompts generate 5 items")
def test_image_prompts():
    from prompts.prompt_templates import get_image_prompts
    prompts = get_image_prompts("Rani Lakshmibai", "", count=5)
    assert len(prompts) == 5, f"Expected 5 prompts, got {len(prompts)}"
    for p in prompts:
        assert "positive" in p, "Missing positive prompt"
        assert "negative" in p, "Missing negative prompt"
        assert "Rani Lakshmibai" in p["positive"], "Fighter name not in image prompt"


@test("Prompts: image prompts scale to custom count")
def test_image_prompts_custom_count():
    from prompts.prompt_templates import get_image_prompts
    for count in [3, 4, 7]:
        prompts = get_image_prompts("Test", "", count=count)
        assert len(prompts) == count, f"Expected {count} prompts, got {len(prompts)}"


# ─────────────────────────────────────────────────────────────────────────────
# API Connectivity Tests
# ─────────────────────────────────────────────────────────────────────────────

@test("Network: Groq API connectivity")
def test_groq_connectivity():
    from config import settings
    if not settings.GROQ_API_KEY:
        return "SKIP"

    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": "Say 'test passed' and nothing else."}],
        max_tokens=10,
    )
    assert response.choices[0].message.content.strip(), "Empty response from Groq"


@test("Network: Pollinations.ai connectivity")
def test_pollinations_connectivity():
    import requests
    # Test with a tiny 64x64 image to check connectivity
    url = "https://image.pollinations.ai/prompt/test?width=64&height=64&model=flux"
    response = requests.get(url, timeout=30)
    assert response.status_code == 200, f"Pollinations returned {response.status_code}"
    assert "image" in response.headers.get("content-type", ""), "Response is not an image"


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests (lightweight)
# ─────────────────────────────────────────────────────────────────────────────

@test("Integration: script generation (real API call)")
def test_script_generation():
    from config import settings
    if not settings.GROQ_API_KEY:
        return "SKIP"

    from src.text_gen import generate_script
    script = generate_script("Bhagat Singh")
    word_count = len(script.split())
    assert 50 <= word_count <= 120, (
        f"Script word count {word_count} is outside acceptable range 50-120"
    )
    assert "Bhagat Singh" in script or "Singh" in script, (
        "Fighter name not mentioned in script"
    )


@test("Integration: audio generation (gTTS)")
def test_audio_generation():
    import tempfile
    from pathlib import Path
    from src.audio_gen import generate_audio, get_audio_duration

    test_script = "He was a revolutionary hero of India."
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = Path(f.name)

    try:
        audio_path = generate_audio(test_script, tmp_path)
        assert audio_path.exists(), "Audio file not created"
        assert audio_path.stat().st_size > 1000, "Audio file too small (probably empty)"
        duration = get_audio_duration(audio_path)
        assert duration > 0, "Audio duration is 0"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@test("Integration: placeholder image creation")
def test_placeholder_image():
    import tempfile
    from pathlib import Path
    from src.image_gen import _create_placeholder_image

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        tmp_path = Path(f.name)

    try:
        result = _create_placeholder_image(tmp_path, frame_num=1)
        assert result.exists(), "Placeholder image not created"
        assert result.stat().st_size > 1000, "Placeholder image too small"

        from PIL import Image
        with Image.open(result) as img:
            assert img.size[0] > 0, "Invalid image width"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ─────────────────────────────────────────────────────────────────────────────
# Run All Tests
# ─────────────────────────────────────────────────────────────────────────────

def run_all_tests():
    print("\n" + "═" * 60)
    print("  FREEDOM FIGHTER VIDEO GENERATOR — TEST SUITE")
    print("═" * 60)

    # Config tests
    print("\n📁 Configuration Tests")
    test_config_loads()
    test_directories_exist()
    test_groq_key()

    # Import tests
    print("\n📦 Package Import Tests")
    test_groq_import()
    test_gtts_import()
    test_moviepy_import()
    test_pillow_import()
    test_requests_import()

    # Prompt tests
    print("\n🖊️  Prompt Engineering Tests")
    test_script_prompt()
    test_image_prompts()
    test_image_prompts_custom_count()

    # API tests
    print("\n🌐 API Connectivity Tests")
    test_groq_connectivity()
    test_pollinations_connectivity()

    # Integration tests
    print("\n⚙️  Integration Tests")
    test_script_generation()
    test_audio_generation()
    test_placeholder_image()

    # Summary
    total = PASSED + FAILED + SKIPPED
    print(f"\n{'═' * 60}")
    print(f"  Results: {PASSED}/{total} passed | {FAILED} failed | {SKIPPED} skipped")
    print("═" * 60)

    if FAILED > 0:
        print(f"\n⚠️  {FAILED} test(s) failed. Fix these before running the full pipeline.")
        print("   See TROUBLESHOOTING in README.md for solutions.")
        return False
    else:
        print(f"\n✅ All tests passed! Ready to run: python main.py \"Bhagat Singh\"")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
