#!/usr/bin/env python3
"""
produce.sh — Main orchestrator for the video production pipeline.

Usage:
    ./produce.sh <episode_num>
    ./produce.sh <ep_num>
    ./produce.sh all
    ./produce.sh 1 2 3
    ./produce.sh install

Environment:
    WORKSPACE     — Working directory (default: ./workspace)
    SCRIPTS_DIR   — Location of SCRIPT.md files (default: auto-detect)
    PIPELINE_DIR  — Location of pipeline scripts (default: same dir as this script)
"""

import sys
import os
import subprocess
import json
import shutil

# Branding
ORANGE = "\033[38;5;208m"
GREEN = "\033[38;5;32m"
RESET = "\033[0m"
BOLD = "\033[1m"

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.environ.get("WORKSPACE", os.path.join(PIPELINE_DIR, "workspace"))

# Episode mapping: episode_num -> SCRIPT.md path
# Auto-detect from common locations
SCRIPT_SEARCH_PATHS = [
    "/mnt/c/k/author/farside-chatgpt-youtube/episodes",
    "/mnt/c/k/author/farside-chatgpt/.obsidian",
    "/mnt/c/k/author/farside-chatgpt/episodes",
]


def find_script(episode_num):
    """Find SCRIPT.md for an episode number."""
    for search_path in SCRIPT_SEARCH_PATHS:
        if not os.path.exists(search_path):
            continue
        for fname in os.listdir(search_path):
            # Look for files matching episode number patterns
            lower = fname.lower()
            if f"episode{episode_num}" in lower or f"episode_{episode_num}" in lower or f"episode-{episode_num}" in lower:
                full = os.path.join(search_path, fname)
                if fname.endswith(".md"):
                    return full
                # Check subdirectories
                if os.path.isdir(full):
                    for sub in os.listdir(full):
                        if sub.lower() == "script.md":
                            return os.path.join(full, sub)
    return None


def find_all_episodes():
    """Find all episode scripts and return {num: path} dict."""
    episodes = {}
    for search_path in SCRIPT_SEARCH_PATHS:
        if not os.path.exists(search_path):
            continue
        for fname in os.listdir(search_path):
            # Match episode numbers: episode_01, episode_02, etc.
            m = re.search(r'episode[_-]?(\d+)', fname.lower())
            if m:
                num = m.group(1)
                full = os.path.join(search_path, fname)
                if os.path.isdir(full):
                    for sub in os.listdir(full):
                        if sub.lower() == "script.md":
                            episodes[num] = os.path.join(full, sub)
                elif fname.endswith(".md"):
                    episodes[num] = full
    return episodes


def run_step(step_name, cmd, cwd=None):
    """Run a command and stream output."""
    print(f"\n{BOLD}{ORANGE}━━━ {step_name} ━━━{RESET}\n")
    result = subprocess.run(
        cmd,
        cwd=cwd or PIPELINE_DIR,
        capture_output=False
    )
    if result.returncode != 0:
        print(f"\n{ORANGE}FAILED: {step_name} (exit code {result.returncode}){RESET}")
        return False
    return True


def produce_episode(episode_num, script_path=None):
    """Produce a single episode video."""

    # Find script
    if not script_path:
        script_path = find_script(episode_num)
    if not script_path or not os.path.exists(script_path):
        print(f"SCRIPT.md not found for Episode {episode_num}")
        print(f"Searched: {', '.join(SCRIPT_SEARCH_PATHS)}")
        return False

    print(f"\n{BOLD}╔══════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}║  Episode {episode_num}                         ║{RESET}")
    print(f"{BOLD}║  {script_path:<40s} ║{RESET}")
    print(f"{BOLD}╚══════════════════════════════════════════╝{RESET}")

    # Setup workspace dirs
    ep_workspace = os.path.join(WORKSPACE, f"episode-{episode_num}")
    slides_dir = os.path.join(ep_workspace, "slides")
    narration_dir = os.path.join(ep_workspace, "narration")
    mixed_dir = os.path.join(ep_workspace, "mixed")
    output_dir = os.path.join(WORKSPACE, "output")

    for d in [slides_dir, narration_dir, mixed_dir, output_dir]:
        os.makedirs(d, exist_ok=True)

    scenes_json = os.path.join(ep_workspace, "scenes.json")
    music_track = os.path.join(WORKSPACE, "music_ambient.mp3")
    music_energetic = os.path.join(WORKSPACE, "music_energetic.mp3")
    output_path = os.path.join(output_dir, f"episode-{episode_num}.mp4")

    pipeline = os.path.join(PIPELINE_DIR, "pipeline")
    scripts = os.path.join(PIPELINE_DIR, "scripts")

    # Step 1: Parse script to scenes
    if not run_step(
        "Step 1: Parse Script",
        [sys.executable, os.path.join(scripts, "script_parser.py"),
         script_path, scenes_json, episode_num]
    ):
        return False

    # Step 2: Generate slides
    if not run_step(
        "Step 2: Generate Slides",
        [sys.executable, os.path.join(scripts, "slidemaker.py"),
         scenes_json, slides_dir]
    ):
        return False

    # Step 3: Generate narration
    if not run_step(
        "Step 3: Generate Narration (TTS)",
        [sys.executable, os.path.join(scripts, "tts_engine.py"),
         scenes_json, narration_dir]
    ):
        return False

    # Step 4: Generate music (if not already cached)
    if not os.path.exists(music_track):
        run_step(
            "Step 4a: Generate Background Music",
            [sys.executable, os.path.join(scripts, "music_generator.py"),
             music_track, "180", "ambient"]
        )

    if not os.path.exists(music_energetic):
        run_step(
            "Step 4b: Generate Energetic Music",
            [sys.executable, os.path.join(scripts, "music_generator.py"),
             music_energetic, "60", "energetic"]
        )

    # Step 5: Mix audio (narration + music)
    if not run_step(
        "Step 5: Mix Audio",
        [sys.executable, os.path.join(scripts, "audio_pipeline.py"),
         narration_dir, music_track, mixed_dir]
    ):
        return False

    # Step 6: Assemble video
    if not run_step(
        "Step 6: Assemble Final Video",
        [sys.executable, os.path.join(scripts, "video_assembler.py"),
         slides_dir, mixed_dir, output_path]
    ):
        return False

    # Done
    if os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        # Get duration
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", output_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        dur = float(r.stdout.strip()) if r.stdout.strip() else 0

        print(f"\n{GREEN}{BOLD}✓ Episode {episode_num} complete!{RESET}")
        print(f"  Path: {output_path}")
        print(f"  Duration: {dur/60:.1f}min | Size: {size:.1f}MB")
        return True
    else:
        print(f"\n{ORANGE}✗ Output file not found: {output_path}{RESET}")
        return False


def install_deps():
    """Install Python dependencies."""
    print("Installing video pipeline dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "edge-tts", "pydub"], check=True)

    # Check for Chrome
    chrome_found = False
    for name in ["google-chrome-stable", "chromium-browser", "chromium"]:
        r = subprocess.run(["which", name], capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  Chrome: {name} ✓")
            chrome_found = True
            break
    if not chrome_found:
        print("  WARNING: No Chrome/Chromium found. Install with:")
        print("    sudo apt install chromium-browser")
        print("    OR")
        print("    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        print("    sudo dpkg -i google-chrome-stable_current_amd64.deb")

    # Check ffmpeg
    r = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
    if r.returncode == 0:
        print("  ffmpeg: ✓")
    else:
        print("  WARNING: ffmpeg not found. Install with: sudo apt install ffmpeg")

    print("\nDone.")


def main():
    import re as _re
    global re
    re = _re

    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./produce.sh <episode_num>     Produce one episode")
        print("  ./produce.sh <ep_num>    Produce one episode")
        print("  ./produce.sh 1 2 3     Produce multiple episodes")
        print("  ./produce.sh all         Produce all episodes")
        print("  ./produce.sh install     Install dependencies")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "install":
        install_deps()
        return

    if cmd == "all":
        episodes = find_all_episodes()
        if not episodes:
            print("No episode scripts found!")
            sys.exit(1)
        print(f"Found {len(episodes)} episodes: {', '.join(sorted(episodes.keys()))}")
        for num in sorted(episodes.keys()):
            produce_episode(num, episodes[num])
        return

    # One or more episode numbers
    for ep_str in sys.argv[1:]:
        if not ep_str.isdigit():
            print(f"Invalid episode number: {ep_str}")
            continue
        produce_episode(ep_str)


if __name__ == "__main__":
    main()
