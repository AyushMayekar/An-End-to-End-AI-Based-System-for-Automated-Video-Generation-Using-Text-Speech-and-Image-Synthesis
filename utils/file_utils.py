"""
utils/file_utils.py
────────────────────
Reusable file I/O helpers used across modules.
"""

import os
import shutil
from pathlib import Path
from utils.logger import log


def ensure_dir(path: Path) -> Path:
    """Create directory (and parents) if it doesn't exist. Returns the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_text(content: str, filepath: Path) -> Path:
    """Write text content to a file. Returns the path."""
    ensure_dir(filepath.parent)
    filepath.write_text(content, encoding="utf-8")
    log.info(f"Text saved → {filepath}")
    return filepath


def load_text(filepath: Path) -> str:
    """Read text content from a file."""
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return filepath.read_text(encoding="utf-8")


def clean_assets(dirs: list[Path]) -> None:
    """Remove and recreate asset directories for a fresh run."""
    for d in dirs:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    log.info("Asset directories cleaned for fresh run.")


def list_images(images_dir: Path) -> list[Path]:
    """Return sorted list of image files from a directory."""
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    images = sorted(
        p for p in images_dir.iterdir()
        if p.suffix.lower() in extensions
    )
    return images


def file_size_mb(filepath: Path) -> float:
    """Return file size in megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)
