#!/usr/bin/env python3
"""
music_generator.py — Generate background music using a simple synth approach.

Since we can't download copyrighted music and AudioCraft is heavy,
we generate ambient background tones using ffmpeg's audio synthesis.
Produces a royalty-free ambient pad suitable for voiceover backing.

Usage:
    python3 music_generator.py <output_path> [duration_seconds]

Requires: ffmpeg
"""

import sys
import os
import subprocess


def generate_ambient_music(output_path, duration=120):
    """
    Generate a soft ambient music track using ffmpeg's synth.
    Creates a layered pad: low drone + mid chord + gentle high shimmer.
    Very low-key, designed to sit under voiceover.
    """
    # Key: C minor (C, Eb, G)
    # Layer 1: Low drone (C2 = 65.41Hz, Eb2 = 77.78Hz)
    # Layer 2: Mid chord pad (C3 = 130.81Hz, Eb3 = 155.56Hz, G3 = 196.00Hz)
    # Layer 3: High shimmer (C4 = 261.63Hz, very quiet)
    # All with slow attack/release via volume envelopes

    filter_complex = (
        # Low drone
        "sine=frequency=65.41:volume=0.15[sine1];"
        "sine=frequency=77.78:volume=0.10[sine2];"
        # Mid pad
        "sine=frequency=130.81:volume=0.08[sine3];"
        "sine=frequency=155.56:volume=0.07[sine4];"
        "sine=frequency=196.00:volume=0.06[sine5];"
        # High shimmer (pulsing)
        "sine=frequency=523.25:volume=0.03[sine6];"
        # Layer all
        "[sine1][sine2][sine3][sine4][sine5][sine6]"
        "amix=inputs=6:duration=first:normalize=0[mixed];"
        # Add gentle LFO tremolo for movement
        "[mixed]tremolo=f=0.3:d=0.02[ modulated];"
        # Soft low-pass to avoid harshness
        "[modulated]lowpass=f=800[filtered];"
        # Normalize to -20 LUFS (background level, narration will be louder)
        "[filtered]loudnorm=I=-20:TP=-2.5:LRA=11[normalized];"
        # Add slight reverb feel
        "[normalized]aecho=0.5:0.7:40:0.3[final]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-t", str(duration),
        "-ar", "44100", "-ac", "2",
        "-b:a", "192k",
        output_path
    ]

    print(f"Generating {duration}s ambient music track...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)

    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"OK: {output_path} ({size:.1f}MB)")
        return True
    else:
        print(f"FAIL: {result.stderr[:300]}")
        return False


def generate_energetic_music(output_path, duration=120):
    """
    Generate more upbeat background music for hooks and transitions.
    Uses higher tempo feel, slightly brighter tones.
    """
    filter_complex = (
        # Bass line
        "sine=frequency=82.41:volume=0.18[bass1];"
        "sine=frequency=98.00:volume=0.12[bass2];"
        # Chord
        "sine=frequency=164.81:volume=0.10[mid1];"
        "sine=frequency=196.00:volume=0.09[mid2];"
        "sine=frequency=246.94:volume=0.07[mid3];"
        # Bright top
        "sine=frequency=329.63:volume=0.04[top1];"
        "sine=frequency=392.00:volume=0.03[top2];"
        # Arpeggio-like pulse
        "sine=frequency=659.25:volume=0.015[arp];"
        "[bass1][bass2][mid1][mid2][mid3][top1][top2][arp]"
        "amix=inputs=8:duration=first:normalize=0[mixed];"
        # Movement
        "[mixed]tremolo=f=0.5:d=0.03[modulated];"
        # Keep it warm
        "[modulated]lowpass=f=1200[filtered];"
        "[filtered]loudnorm=I=-20:TP=-2.5:LRA=11[normalized];"
        "[normalized]aecho=0.5:0.7:60:0.25[final]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-t", str(duration),
        "-ar", "44100", "-ac", "2",
        "-b:a", "192k",
        output_path
    ]

    print(f"Generating {duration}s energetic music track...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)

    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"OK: {output_path} ({size:.1f}MB)")
        return True
    else:
        print(f"FAIL: {result.stderr[:300]}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 music_generator.py <output_path> [duration] [style]")
        print("Styles: ambient (default), energetic")
        sys.exit(1)

    output_path = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    style = sys.argv[3] if len(sys.argv) > 3 else "ambient"

    if style == "energetic":
        generate_energetic_music(output_path, duration)
    else:
        generate_ambient_music(output_path, duration)


if __name__ == "__main__":
    main()
