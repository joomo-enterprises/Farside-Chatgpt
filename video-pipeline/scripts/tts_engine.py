#!/usr/bin/env python3
"""
tts_engine.py — Generate voiceover audio from scenes using edge-tts.

Reads scenes.json and produces MP3 files for each scene that has narration.
Uses edge-tts (free, no API key needed) with high-quality voices.

Usage:
    python3 tts_engine.py <scenes.json> <output_dir>

Requires: pip install edge-tts
"""

import json
import sys
import os
import asyncio
import subprocess

# Default voice — good quality, slightly warm American English
DEFAULT_VOICE = "en-US-GuyNeural"

# Alternative voices by feel:
VOICES = {
    "warm": "en-US-GuyNeural",
    "professional": "en-US-JennyNeural",
    "authoritative": "en-US-RogerNeural",
    "friendly": "en-US-AriaNeural",
}


async def generate_narration_async(text, output_path, voice=DEFAULT_VOICE):
    """Use edge-tts to generate narration MP3."""
    tmp_mp3 = output_path + ".tmp.mp3"
    try:
        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "edge_tts",
            "--voice", voice,
            "--text", text,
            "--write-media", tmp_mp3,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)

        if process.returncode != 0 or not os.path.exists(tmp_mp3):
            print(f"  TTS error: {stderr.decode()[:200]}", file=sys.stderr)
            return False

        # Normalize audio: convert to mono, 44.1kHz, normalize volume
        cmd = [
            "ffmpeg", "-y", "-i", tmp_mp3,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=summary",
            "-ar", "44100", "-ac", "2",
            "-b:a", "192k",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        os.unlink(tmp_mp3)

        if result.returncode != 0:
            print(f"  Normalize error: {result.stderr[:200]}", file=sys.stderr)
            # fallback: just copy the file
            os.rename(tmp_mp3 if os.path.exists(tmp_mp3) else output_path + ".tmp.mp3", output_path)
            return False

        return os.path.exists(output_path)

    except asyncio.TimeoutError:
        print(f"  TTS timeout for voice generation", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  TTS exception: {e}", file=sys.stderr)
        return False


def generate_narration(text, output_path, voice=DEFAULT_VOICE):
    """Sync wrapper for async TTS generation."""
    return asyncio.get_event_loop().run_until_complete(
        generate_narration_async(text, output_path, voice)
    )


def scene_to_narration(scene):
    """Extract narration text from a scene."""
    style = scene.get("narration_style", "warm")
    parts = []

    scene_type = scene.get("type", "content")

    if scene_type == "title":
        parts.append(scene.get("narration", ""))
    elif scene_type == "hook":
        q = scene.get("question", "")
        parts.append(f"Have you ever wondered: {q}")
        for b in scene.get("bullets", []):
            parts.append(b)
    elif scene_type == "content":
        parts.append(scene.get("heading", ""))
        for b in scene.get("bullets", []):
            parts.append(b)
        if scene.get("extra_narration"):
            parts.append(scene["extra_narration"])
    elif scene_type == "code":
        parts.append(scene.get("heading", ""))
        parts.append(scene.get("narration", ""))
        for note in scene.get("notes", []):
            parts.append(note)
    elif scene_type == "comparison":
        parts.append(scene.get("heading", ""))
        parts.append(scene.get("narration", ""))
    elif scene_type == "outro":
        parts.append(scene.get("narration", ""))

    return "\n\n".join(p for p in parts if p), VOICES.get(style, DEFAULT_VOICE)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 tts_engine.py <scenes.json> <output_dir> [voice]")
        sys.exit(1)

    scenes_path = sys.argv[1]
    output_dir = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_VOICE

    with open(scenes_path, 'r') as f:
        scenes = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    total = len(scenes)

    print(f"Generating narration for {total} scenes (voice: {voice})")

    count = 0
    for i, scene in enumerate(scenes):
        scene_type = scene.get("type", "content")

        # Title and outro usually don't need narration
        if scene_type in ("title", "outro") and not scene.get("narration"):
            print(f"  [{i+1:3d}/{total}] SKIP  {scene_type:12s} | no narration")
            continue

        text, scene_voice = scene_to_narration(scene)
        if not text.strip():
            print(f"  [{i+1:3d}/{total}] SKIP  {scene_type:12s} | empty text")
            continue

        out_file = os.path.join(output_dir, f"scene_{i:03d}.mp3")

        print(f"  [{i+1:3d}/{total}] TTS   {scene_type:12s} | {text[:60]}...", end="", flush=True)
        ok = generate_narration(text, out_file, scene_voice)
        status = "OK" if ok else "FAIL"
        size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
        size_str = f"{size/1024:.0f}KB" if size > 0 else "0"
        print(f"\r  [{i+1:3d}/{total}] {status}  {scene_type:12s} | {size_str:>8s} | scene_{i:03d}.mp3")
        count += 1

    print(f"\nDone. {count} narration files in {output_dir}/")


if __name__ == "__main__":
    main()
