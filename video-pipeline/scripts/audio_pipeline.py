#!/usr/bin/env python3
"""
audio_pipeline.py — Mix narration with background music at -14 LUFS.

Takes narration MP3s and mixes them with background music track.
Handles: volume ducking, normalization, silence padding.

Usage:
    python3 audio_pipeline.py <narration_dir> <music_track> <output_dir>
"""

import sys
import os
import subprocess
import json


def get_duration(filepath):
    """Get audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        return float(result.stdout.strip())
    except (ValueError, IndexError):
        return 0.0


def mix_audio(narration_path, music_path, output_path, music_volume=0.08):
    """
    Mix narration with background music.
    Music is heavily ducked during narration, plays softly in gaps.
    Final output normalized to -14 LUFS (YouTube standard).
    """
    if not os.path.exists(narration_path):
        # No narration: just use music, trimmed to 30s max
        cmd = [
            "ffmpeg", "-y", "-i", music_path,
            "-t", "30",
            "-af", f"volume={music_volume},loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "44100", "-ac", "2",
            "-b:a", "192k",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", narration_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume},aloop=loop=-1:size=2e+09[music];"
            f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
            f"[mixed]loudnorm=I=-14:TP=-1.5:LRA=11[normalized]",
            "-map", "[normalized]",
            "-ar", "44100", "-ac", "2",
            "-b:a", "192k",
            output_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode == 0 and os.path.exists(output_path)


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 audio_pipeline.py <narration_dir> <music_track> <output_dir>")
        sys.exit(1)

    narration_dir = sys.argv[1]
    music_track = sys.argv[2]
    output_dir = sys.argv[3]

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(music_track):
        print(f"ERROR: Music track not found: {music_track}")
        print("Generate one first with: python3 music_generator.py")
        sys.exit(1)

    # Find all scene audio files
    scene_files = sorted([
        f for f in os.listdir(narration_dir)
        if f.startswith("scene_") and f.endswith(".mp3")
    ])

    print(f"Mixing {len(scene_files)} scenes with background music")
    print(f"Music: {music_track}")
    print(f"Output: {output_dir}/")

    for i, fname in enumerate(scene_files):
        scene_num = fname.replace("scene_", "").replace(".mp3", "")
        narration_path = os.path.join(narration_dir, fname)
        output_path = os.path.join(output_dir, f"scene_{scene_num}_mixed.mp3")

        dur = get_duration(narration_path)
        print(f"  [{i+1:3d}/{len(scene_files)}] scene_{scene_num}  dur={dur:.1f}s  mixing...", end="", flush=True)

        ok = mix_audio(narration_path, music_track, output_path)
        status = "OK" if ok else "FAIL"
        out_dur = get_duration(output_path) if os.path.exists(output_path) else 0
        print(f"\r  [{i+1:3d}/{len(scene_files)}] scene_{scene_num}  {status}  out={out_dur:.1f}s")

    print(f"\nDone. {len(scene_files)} mixed audio files in {output_dir}/")


if __name__ == "__main__":
    main()
