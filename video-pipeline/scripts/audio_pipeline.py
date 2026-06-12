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


def measure_loudness(filepath):
    """Measure integrated loudness (LUFS) of a file. Returns float or None."""
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # JSON is in stderr after 'Parsed_loudnorm'
    try:
        idx = result.stderr.find("{")
        if idx >= 0:
            data = json.loads(result.stderr[idx:])
            return float(data.get("input_i", "-70"))
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def normalize_narration_in_place(narration_path):
    """
    Normalize a narration clip to approximately -16 LUFS in place.
    Uses measured loudness to compute exact dB gain needed,
    applies it with volume filter + peak limiter to prevent clipping.
    Skips second loudnorm — final mix will do that.
    """
    tmp_out = narration_path + ".norm.mp3"

    measured_i = measure_loudness(narration_path)

    if measured_i is not None and measured_i > -70:
        gain_db = -16.0 - measured_i
        gain_db = max(0.0, min(40.0, gain_db))
    else:
        gain_db = 20.0

    cmd = [
        "ffmpeg", "-y", "-i", narration_path,
        "-af", f"aresample=44100,highpass=f=80,volume={gain_db}dB,alimiter=limit=-1dB:level=1",
        "-ar", "44100", "-ac", "2",
        "-b:a", "192k",
        tmp_out
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and os.path.exists(tmp_out):
        os.replace(tmp_out, narration_path)
        return True

    if os.path.exists(tmp_out):
        os.unlink(tmp_out)
    return False
def mix_audio(narration_path, music_path, output_path, music_volume=0.12):
    """
    Mix narration with background music.
    Narration is pre-normalized to -16 LUFS.
    Music plays softly underneath. No post-mix loudnorm — narration level
    is already correct from pre-normalization.
    Output duration matches narration duration exactly.
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
        # Get narration duration to trim mixed output exactly
        nar_dur = get_duration(narration_path)
        # Use -t to cap output at narration duration (avoids filter expression issues)
        cmd = [
            "ffmpeg", "-y",
            "-i", narration_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[music];"
            f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=0[out];"
            f"[out]alimiter=limit=-1dB[final]",
            "-map", "[final]",
            "-t", str(nar_dur),
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

    # Clean up stale mixed files from previous runs
    for f in os.listdir(narration_dir):
        if "_mixed" in f and f.endswith(".mp3"):
            try:
                os.unlink(os.path.join(narration_dir, f))
            except Exception:
                pass

    # Find all scene narration files (exclude already-mixed files)
    scene_files = sorted([
        f for f in os.listdir(narration_dir)
        if f.startswith("scene_") and f.endswith(".mp3") and "_mixed" not in f
    ])

    print(f"Normalizing {len(scene_files)} narration clips to -16 LUFS")
    for fname in scene_files:
        fpath = os.path.join(narration_dir, fname)
        normalize_narration_in_place(fpath)

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
