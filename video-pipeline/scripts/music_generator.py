#!/usr/bin/env python3
"""
music_generator.py — Generate melodious background music, intros, and outros using ffmpeg synth.

Creates high-quality, themed audio:
- melodic: Warm ambient background track with chord progressions and arpeggios (Am - F - C - G - Am)
- intro: High-impact melodic tech stinger (motif: C5-E5-A5-G5-A5) with a rising sweep and echo ring-out
- outro: Reflective resolving theme (motif: E5-D5-C5-B4-A4) with descending chimes and long fade
- ambient: Original low-key drone pad
- energetic: Upbeat bass/high pad pattern

Usage:
    python3 music_generator.py <output_path> [duration] [style]
    Styles: melodic (default), intro, outro, ambient, energetic
"""

import sys
import os
import subprocess


def generate_intro_music(output_path, duration=8):
    """
    Generate a short, modern, high-impact musical stinger for channel intros.
    Motif (C5 -> E5 -> A5 -> G5 -> A) with a rising power chord and beautiful delay ring-out.
    """
    filter_parts = []
    labels = []

    # 1. Warm base swell (Chord: Am)
    # Raising volume to create a dramatic entry, resolving on a sweet spot
    bass_freqs = [(110.00, "base_a"), (130.81, "base_c"), (164.81, "base_e"), (220.00, "base_a2")]
    for freq, name in bass_freqs:
        filter_parts.append(f"sine=frequency={freq}:duration={duration}:sample_rate=44100[{name}_raw]")
        # SBF (Slow build fade in, then long ring out)
        filter_parts.append(
            f"[{name}_raw]volume=0.08,afade=t=in:st=0:d=1.5,afade=t=out:st={duration-3.0}:d=3.0[{name}]"
        )
        labels.append(f"[{name}]")

    # 2. Modern High Signature Chime Motif
    # Sequence of notes: C5 (0.5s), E5 (1.0s), A5 (1.5s), G5 (2.2s), A5 (3.0s -> end)
    chimes = [
        (523.25, 0.5, 0.5, "chime_c"),  # C5
        (659.25, 1.0, 0.5, "chime_e"),  # E5
        (880.00, 1.5, 0.7, "chime_a1"), # A5
        (783.99, 2.2, 0.8, "chime_g"),  # G5
        (880.00, 3.0, duration - 3.0, "chime_a2")  # A5 resolving ring out
    ]

    for freq, start, note_dur, name in chimes:
        filter_parts.append(f"sine=frequency={freq}:duration={duration}:sample_rate=44100[{name}_raw]")
        # Trim / gate the sound so it only plays during its note window
        filter_parts.append(
            f"[{name}_raw]volume=0.04,aselect='between(t,{start},{start+note_dur})',afade=t=in:st={start}:d=0.05,afade=t=out:st={start+note_dur-0.1}:d=0.1[{name}]"
        )
        labels.append(f"[{name}]")

    # Mix elements
    mix_inputs = "".join(labels)
    filter_parts.append(f"{mix_inputs}amix=inputs={len(labels)}:normalize=0[mixed]")

    # Effects: Tremolo + Chorus + Stereo Echo Reverb
    filter_parts.append("[mixed]tremolo=f=4:d=0.02[modulated]")
    filter_parts.append("[modulated]aecho=0.8:0.7:150:0.3[echo1]")
    filter_parts.append("[echo1]aecho=0.6:0.5:280:0.25[echo2]")
    filter_parts.append("[echo2]loudnorm=I=-16:TP=-1.5:LRA=10[final]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-t", str(duration),
        "-ar", "44100", "-ac", "2",
        "-b:a", "192k",
        output_path
    ]

    print(f"Generating {duration}s musical intro stinger...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)

    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"OK: {output_path} ({size:.2f}MB)")
        return True
    else:
        print(f"FAIL: {result.stderr[:500]}")
        return False


def generate_outro_music(output_path, duration=15):
    """
    Generate a satisfying, professional melodic theme for channel outros.
    Descending bell-like melody (E5 -> D5 -> C5 -> B4 -> A4) with a deep, emotional chord resolution and slow fadeout.
    """
    filter_parts = []
    labels = []

    # 1. Warm base chrods (F major -> G major -> A minor)
    # F maj (0-3s), G maj (3-6s), Am (6s-end)
    chords = [
        # F maj (F3=174.61, A3=220.00, C4=261.63)
        (174.61, 0, 3.5, "chord_f_r"), (220.00, 0, 3.5, "chord_f_3"), (261.63, 0, 3.5, "chord_f_5"),
        # G maj (G3=196.00, B3=246.94, D4=293.66)
        (196.00, 3.0, 3.5, "chord_g_r"), (246.94, 3.0, 3.5, "chord_g_3"), (293.66, 3.0, 3.5, "chord_g_5"),
        # Am resolving pad (A3=220.00, C4=261.63, E4=329.63, A4=440.00)
        (220.00, 6.0, duration-6.0, "chord_a_r"), (261.63, 6.0, duration-6.0, "chord_a_3"),
        (329.63, 6.0, duration-6.0, "chord_a_5"), (440.00, 6.0, duration-6.0, "chord_a_oct")
    ]

    for freq, start, note_dur, name in chords:
        filter_parts.append(f"sine=frequency={freq}:duration={duration}:sample_rate=44100[{name}_raw]")
        filter_parts.append(
            f"[{name}_raw]volume=0.06,aselect='between(t,{start},{start+note_dur})',afade=t=in:st={start}:d=0.5,afade=t=out:st={start+note_dur-0.5}:d=0.5[{name}]"
        )
        labels.append(f"[{name}]")

    # 2. Descending Chime Melody
    # Notes: E5 (0.5s), D5 (2.5s), C5 (4.5s), B4 (6.5s), A4 (8.5s -> fade)
    chime_seq = [
        (659.25, 0.5, 2.0, "m_e"),  # E5
        (587.33, 2.5, 2.0, "m_d"),  # D5
        (523.25, 4.5, 2.0, "m_c"),  # C5
        (493.88, 6.5, 2.0, "m_b"),  # B4
        (440.00, 8.5, duration - 8.5, "m_a")  # A4 (Resolving chimes rings into infinity)
    ]

    for freq, start, note_dur, name in chime_seq:
        filter_parts.append(f"sine=frequency={freq}:duration={duration}:sample_rate=44100[{name}_raw]")
        filter_parts.append(
            f"[{name}_raw]volume=0.035,aselect='between(t,{start},{start+note_dur})',afade=t=in:st={start}:d=0.1,afade=t=out:st={start+note_dur-0.2}:d=0.5[{name}]"
        )
        labels.append(f"[{name}]")

    # Combine everything
    mix_inputs = "".join(labels)
    filter_parts.append(f"{mix_inputs}amix=inputs={len(labels)}:normalize=0[mixed]")

    # Beautiful effects for space: Tremolo + dual Delay/Reverb + final slow fadeout
    filter_parts.append("[mixed]tremolo=f=1.5:d=0.02[modulated]")
    filter_parts.append("[modulated]aecho=0.7:0.6:200:0.35[echo1]")
    filter_parts.append("[echo1]aecho=0.5:0.4:450:0.25[echo2]")
    # Fade out completely in the last 4 seconds
    filter_parts.append(f"[echo2]afade=t=out:st={duration-4.0}:d=4.0[faded]")
    filter_parts.append("[faded]loudnorm=I=-18:TP=-2.0:LRA=12[final]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-t", str(duration),
        "-ar", "44100", "-ac", "2",
        "-b:a", "192k",
        output_path
    ]

    print(f"Generating {duration}s musical outro track...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)

    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"OK: {output_path} ({size:.2f}MB)")
        return True
    else:
        print(f"FAIL: {result.stderr[:500]}")
        return False


def generate_melodic_music(output_path, duration=120):
    """
    Generate a warm, melodic ambient track.
    Uses chord progressions and arpeggios for a more musical feel.
    Key: A minor (relative to C major) — warm, slightly melancholic, professional.
    """
    filter_parts = []
    labels = []

    # === LAYER 1: Warm bass drone (root notes, very slow) ===
    bass_freqs = [110.00, 87.31, 130.81, 98.00]  # Am, F, C, G roots (one octave down)
    bass_dur = duration / 4  # each chord lasts 1/4 of total

    for i, freq in enumerate(bass_freqs):
        label = f"bass{i}"
        filter_parts.append(
            f"sine=frequency={freq}:duration={bass_dur}:sample_rate=44100[{label}_raw]"
        )
        filter_parts.append(
            f"[{label}_raw]volume=0.12,afade=t=in:st=0:d=1,afade=t=out:st={bass_dur-1}:d=1[{label}]"
        )
        labels.append(f"[{label}]")

    # Concat bass segments
    bass_concat = "".join(labels)
    filter_parts.append(f"{bass_concat}concat=n={len(labels)}:v=0:a=1[bass_mix]")
    filter_parts.append("[bass_mix]volume=0.8[bass_final]")

    # === LAYER 2: Mid pad (chord tones, warm) ===
    mid_layers = [
        # Am chord tones (A3, C4, E4)
        (220.00, 0.06, "mid_a1"), (261.63, 0.05, "mid_c1"), (329.63, 0.05, "mid_e1"),
        # F chord tones (F3, A3, C4)
        (174.61, 0.06, "mid_f"), (220.00, 0.05, "mid_a2"), (261.63, 0.04, "mid_c2"),
        # C chord tones (C3, E3, G3)
        (130.81, 0.06, "mid_c3"), (164.81, 0.05, "mid_e2"), (196.00, 0.04, "mid_g1"),
        # G chord tones (G3, B3, D4)
        (196.00, 0.05, "mid_g2"), (246.94, 0.04, "mid_b"), (293.66, 0.04, "mid_d"),
    ]

    mid_labels = []
    for freq, vol, label in mid_layers:
        filter_parts.append(
            f"sine=frequency={freq}:duration={duration}:sample_rate=44100[{label}_raw]"
        )
        filter_parts.append(f"[{label}_raw]volume={vol}[{label}]")
        mid_labels.append(f"[{label}]")

    mid_inputs = "".join(mid_labels)
    filter_parts.append(f"{mid_inputs}amix={len(mid_labels)}:normalize=0[mid_raw]")
    filter_parts.append("[mid_raw]lowpass=f=600[mid_warm]")
    filter_parts.append("[mid_warm]volume=0.7[mid_final]")

    # === LAYER 3: Arpeggio (gentle, high, melodic) ===
    arp_notes = [440.00, 523.25, 659.25, 523.25, 392.00, 523.25, 440.00, 349.23]
    arp_dur = duration / len(arp_notes)

    arp_labels = []
    for i, freq in enumerate(arp_notes):
        label = f"arp{i}"
        filter_parts.append(
            f"sine=frequency={freq}:duration={arp_dur}:sample_rate=44100[{label}_raw]"
        )
        filter_parts.append(
            f"[{label}_raw]volume=0.025,afade=t=in:st=0:d=0.1,afade=t=out:st={arp_dur-0.1}:d=0.1[{label}]"
        )
        arp_labels.append(f"[{label}]")

    arp_concat = "".join(arp_labels)
    filter_parts.append(f"{arp_concat}concat=n={len(arp_labels)}:v=0:a=1[arp_mix]")
    filter_parts.append("[arp_mix]highpass=f=200[arp_hp]")
    filter_parts.append("[arp_hp]volume=1.5[arp_final]")

    # === LAYER 4: Shimmer (very high, very quiet) ===
    filter_parts.append(
        f"sine=frequency=880:duration={duration}:sample_rate=44100[shim_raw]"
    )
    filter_parts.append("[shim_raw]volume=0.015[shim_hp]")
    filter_parts.append("[shim_hp]highpass=f=400[shim_final]")

    # === MIX ALL LAYERS ===
    filter_parts.append(
        "[bass_final][mid_final][arp_final][shim_final]amix=4:normalize=0[pre_fx]"
    )

    # === EFFECTS ===
    filter_parts.append("[pre_fx]tremolo=f=0.15:d=0.01[tremolo]")
    filter_parts.append("[tremolo]lowpass=f=1500[warm]")
    filter_parts.append("[warm]aecho=0.6:0.5:80:0.2[reverb]")
    filter_parts.append("[reverb]loudnorm=I=-23:TP=-3:LRA=14[final]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-t", str(duration),
        "-ar", "44100", "-ac", "2",
        "-b:a", "192k",
        output_path
    ]

    print(f"Generating {duration}s melodic ambient track...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 60)

    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"OK: {output_path} ({size:.1f}MB)")
        return True
    else:
        print(f"FAIL: {result.stderr[:500]}")
        return False


def generate_ambient_music(output_path, duration=120):
    """Original ambient pad (kept for compatibility)."""
    filter_parts = []
    labels = []

    layers = [
        (65.41, 0.15, "drone1"), (77.78, 0.10, "drone2"),
        (130.81, 0.08, "pad1"), (155.56, 0.07, "pad2"), (196.00, 0.06, "pad3"),
        (523.25, 0.03, "shimmer"),
    ]

    for freq, vol, label in layers:
        filter_parts.append(f"sine=frequency={freq}:duration={duration}[{label}_raw]")
        filter_parts.append(f"[{label}_raw]volume={vol}[{label}]")
        labels.append(f"[{label}]")

    mix_inputs = "".join(labels)
    filter_parts.append(f"{mix_inputs}amix=inputs={len(labels)}:normalize=0[mixed]")
    filter_parts.append("[mixed]tremolo=f=0.3:d=0.02[modulated]")
    filter_parts.append("[modulated]lowpass=f=800[filtered]")
    filter_parts.append("[filtered]loudnorm=I=-20:TP=-2.5:LRA=11[normalized]")
    filter_parts.append("[normalized]aecho=0.5:0.7:40:0.3[final]")

    filter_complex = ";".join(filter_parts)

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
    """Upbeat background music for hooks and transitions."""
    filter_parts = []
    labels = []

    layers = [
        (82.41, 0.18, "bass1"), (98.00, 0.12, "bass2"),
        (164.81, 0.10, "mid1"), (196.00, 0.09, "mid2"), (246.94, 0.07, "mid3"),
        (329.63, 0.04, "top1"), (392.00, 0.03, "top2"), (659.25, 0.015, "arp"),
    ]

    for freq, vol, label in layers:
        filter_parts.append(f"sine=frequency={freq}:duration={duration}[{label}_raw]")
        filter_parts.append(f"[{label}_raw]volume={vol}[{label}]")
        labels.append(f"[{label}]")

    mix_inputs = "".join(labels)
    filter_parts.append(f"{mix_inputs}amix=inputs={len(labels)}:normalize=0[mixed]")
    filter_parts.append("[mixed]tremolo=f=0.5:d=0.03[modulated]")
    filter_parts.append("[modulated]lowpass=f=1200[filtered]")
    filter_parts.append("[filtered]loudnorm=I=-20:TP=-2.5:LRA=11[normalized]")
    filter_parts.append("[normalized]aecho=0.5:0.7:60:0.25[final]")

    filter_complex = ";".join(filter_parts)

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
        print("Styles: melodic (default), intro, outro, ambient, energetic")
        sys.exit(1)

    output_path = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    style = sys.argv[3] if len(sys.argv) > 3 else "melodic"

    if style == "energetic":
        generate_energetic_music(output_path, duration)
    elif style == "ambient":
        generate_ambient_music(output_path, duration)
    elif style == "intro":
        generate_intro_music(output_path, duration)
    elif style == "outro":
        generate_outro_music(output_path, duration)
    else:
        generate_melodic_music(output_path, duration)


if __name__ == "__main__":
    main()
