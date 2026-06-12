#!/usr/bin/env python3
"""
video_assembler.py — Assemble slides + mixed audio into final video.

Takes slide PNGs and mixed audio MP3s, produces MP4 per scene,
then concatenates into final episode video.

Usage:
    python3 video_assembler.py <slides_dir> <audio_dir> <output_path> [options]

Options:
    --intro-audio <path>   Optional intro music track (MP3)
    --intro-slide <path>   Optional intro slide PNG (default: slide_intro.png in slides_dir)
    --outro-audio <path>   Optional outro music track (MP3)
    --outro-slide <path>   Optional outro slide PNG (default: slide_outro_card.png in slides_dir)
    --outro-fade <sec>     Outro fade-out duration in seconds (default: 4)

Requires: ffmpeg
"""

import sys
import os
import subprocess
import argparse
import shutil


def get_files_sorted(directory, prefix, suffix):
    """Get sorted list of files matching prefix+suffix."""
    files = [f for f in os.listdir(directory)
             if f.startswith(prefix) and f.endswith(suffix)]
    files.sort()
    return files


def slide_to_video(slide_path, audio_path, output_path, duration=None):
    """Combine a single slide + audio into a video clip."""
    # Get audio duration if not specified
    if duration is None:
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        try:
            duration = float(result.stdout.strip())
        except (ValueError, IndexError):
            duration = 5.0

    # Ken Burns: slow zoom from 1.0 to 1.08 over the clip duration
    total_frames = max(1, int(duration * 30))
    vf = (f"zoompan=z='1.0+0.0005*in':x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':d={total_frames}:s=1920x1080:fps=30")

    cmd = [
        "ffmpeg", "-y",
        "-f", "image2", "-loop", "1", "-i", slide_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "320k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=max(60, int(duration * 2)))

    if result.returncode != 0:
        # Fallback: no Ken Burns, just static slide
        cmd2 = [
            "ffmpeg", "-y",
            "-f", "image2", "-loop", "1", "-i", slide_path,
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "320k",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            output_path
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True,
                                 timeout=max(60, int(duration * 2)))
        if result2.returncode != 0:
            print(f"  ERROR assembling scene: {result2.stderr[:200]}",
                  file=sys.stderr)
            return False

    return os.path.exists(output_path)


def make_silent_video(slide_path, duration, output_path):
    """Create a video from a slide with silent audio (for intro/outro cards)."""
    total_frames = max(1, int(duration * 30))
    vf = (f"zoompan=z='1.0+0.0005*in':x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':d={total_frames}:s=1920x1080:fps=30")

    cmd = [
        "ffmpeg", "-y",
        "-f", "image2", "-loop", "1", "-i", slide_path,
        "-f", "lavfi", "-i", f"anullsrc=cl=stereo:r=44100",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "320k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=max(60, int(duration * 2)))

    if result.returncode != 0:
        # Fallback: no Ken Burns
        cmd2 = [
            "ffmpeg", "-y",
            "-f", "image2", "-loop", "1", "-i", slide_path,
            "-f", "lavfi", "-i", f"anullsrc=cl=stereo:r=44100",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "320k",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            output_path
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True,
                                 timeout=max(60, int(duration * 2)))
        if result2.returncode != 0:
            print(f"  ERROR making silent clip: {result2.stderr[:200]}",
                  file=sys.stderr)
            return False

    return os.path.exists(output_path)


def mix_audio_on_clip(video_path, audio_path, output_path, fade_out=0):
    """Replace or mix audio on a video clip. Used for intro/outro music overlay."""
    af_filters = []
    if fade_out > 0:
        # Get audio duration for fade
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        try:
            dur = float(result.stdout.strip())
            af_filters.append(f"afade=t=out:st={dur - fade_out}:d={fade_out}")
        except (ValueError, IndexError):
            pass

    af_str = ",".join(af_filters) if af_filters else "anull"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex",
        "[1:a]volume=0.8[a1];[0:a][a1]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "320k",
        "-shortest",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        # Simpler approach: just replace audio
        cmd2 = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "320k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_path
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)
        if result2.returncode != 0:
            print(f"  ERROR mixing audio: {result2.stderr[:200]}", file=sys.stderr)
            return False

    return os.path.exists(output_path)


def concatenate_clips(clip_paths, output_path):
    """Concatenate video clips into final video using concat demuxer."""
    concat_dir = os.path.dirname(os.path.abspath(output_path))
    concat_list = os.path.join(concat_dir, "concat_list.txt")

    with open(concat_list, 'w') as f:
        for clip_path in clip_paths:
            abs_path = os.path.abspath(clip_path)
            f.write(f"file '{abs_path}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "320k",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        os.unlink(concat_list)
    except Exception:
        pass

    if result.returncode != 0:
        print(f"  Concat ERROR: {result.stderr[:300]}", file=sys.stderr)
        return False

    return os.path.exists(output_path)


def get_audio_duration(audio_path):
    """Get duration of an audio file in seconds."""
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        return float(result.stdout.strip())
    except (ValueError, IndexError):
        return 5.0


def main():
    parser = argparse.ArgumentParser(
        description="Assemble slides + audio into final video"
    )
    parser.add_argument("slides_dir", help="Directory containing slide PNGs")
    parser.add_argument("audio_dir", help="Directory containing mixed audio MP3s")
    parser.add_argument("output_path", help="Output MP4 path")
    parser.add_argument("--intro-audio", help="Intro music MP3 path")
    parser.add_argument("--intro-slide", help="Intro slide PNG path")
    parser.add_argument("--outro-audio", help="Outro music MP3 path")
    parser.add_argument("--outro-slide", help="Outro slide PNG path")
    parser.add_argument("--outro-fade", type=float, default=4.0,
                        help="Outro fade-out seconds (default: 4)")

    args = parser.parse_args()

    slides_dir = args.slides_dir
    audio_dir = args.audio_dir
    output_path = args.output_path

    # Get slide and audio files (exclude intro/outro cards from main set)
    all_slides = get_files_sorted(slides_dir, "slide_", ".png")
    main_slides = [s for s in all_slides
                   if s not in ("slide_intro.png", "slide_outro_card.png")]
    audio_files = get_files_sorted(audio_dir, "scene_", "_mixed.mp3")

    if not main_slides:
        print("ERROR: No slide PNGs found")
        sys.exit(1)
    if not audio_files:
        print("ERROR: No mixed audio files found")
        sys.exit(1)

    # Create temp dir for individual clips
    clips_dir = output_path + "_clips"
    os.makedirs(clips_dir, exist_ok=True)

    print(f"Assembling video: {len(main_slides)} slides, {len(audio_files)} audio tracks")
    if args.intro_audio:
        print(f"  Intro: {args.intro_audio}")
    if args.outro_audio:
        print(f"  Outro: {args.outro_audio}")
    print(f"Output: {output_path}")

    clip_paths = []

    # ── INTRO ──────────────────────────────────────────────────────
    if args.intro_audio and os.path.exists(args.intro_audio):
        intro_slide = args.intro_slide
        if not intro_slide:
            intro_slide = os.path.join(slides_dir, "slide_intro.png")
        if not os.path.exists(intro_slide):
            # Fallback: use first slide
            intro_slide = os.path.join(slides_dir, main_slides[0])

        intro_dur = get_audio_duration(args.intro_audio)
        intro_clip = os.path.join(clips_dir, "clip_intro.mp4")
        intro_mixed = os.path.join(clips_dir, "clip_intro_mixed.mp4")

        print(f"\n  [INTRO] {intro_dur:.1f}s intro music...")
        ok = make_silent_video(intro_slide, intro_dur, intro_clip)
        if ok:
            ok2 = mix_audio_on_clip(intro_clip, args.intro_audio, intro_mixed)
            if ok2:
                clip_paths.append(intro_mixed)
                print(f"  [INTRO] OK")
            else:
                clip_paths.append(intro_clip)
                print(f"  [INTRO] OK (silent, mix failed)")
        else:
            print(f"  [INTRO] FAIL — skipping")

    # ── MAIN SCENES ────────────────────────────────────────────────
    audio_map = {}
    for af in audio_files:
        num = af.replace("scene_", "").replace("_mixed.mp3", "")
        audio_map[num] = os.path.join(audio_dir, af)

    for i, slide in enumerate(main_slides):
        slide_num = slide.replace("slide_", "").replace(".png", "")
        slide_path = os.path.join(slides_dir, slide)
        audio_path = audio_map.get(slide_num)

        if not audio_path:
            raw_audio = os.path.join(
                audio_dir.replace("_mixed", ""),
                f"scene_{slide_num}.mp3"
            )
            if os.path.exists(raw_audio):
                audio_path = raw_audio
            else:
                print(f"  [{i+1:3d}/{len(main_slides)}] SKIP  slide_{slide_num} (no audio)")
                continue

        clip_path = os.path.join(clips_dir, f"clip_{slide_num}.mp4")

        print(f"  [{i+1:3d}/{len(main_slides)}] slide_{slide_num} ...", end="", flush=True)
        ok = slide_to_video(slide_path, audio_path, clip_path)
        status = "OK" if ok else "FAIL"
        print(f"\r  [{i+1:3d}/{len(main_slides)}] slide_{slide_num} -> {status}")

        if ok:
            clip_paths.append(clip_path)

    # ── OUTRO ─────────────────────────────────────────────────────
    if args.outro_audio and os.path.exists(args.outro_audio):
        outro_slide = args.outro_slide
        if not outro_slide:
            outro_slide = os.path.join(slides_dir, "slide_outro_card.png")
        if not os.path.exists(outro_slide):
            outro_slide = os.path.join(slides_dir, main_slides[-1])

        outro_dur = get_audio_duration(args.outro_audio)
        outro_clip = os.path.join(clips_dir, "clip_outro.mp4")
        outro_mixed = os.path.join(clips_dir, "clip_outro_mixed.mp4")

        print(f"\n  [OUTRO] {outro_dur:.1f}s outro music...")
        ok = make_silent_video(outro_slide, outro_dur, outro_clip)
        if ok:
            ok2 = mix_audio_on_clip(
                outro_clip, args.outro_audio, outro_mixed,
                fade_out=args.outro_fade
            )
            if ok2:
                clip_paths.append(outro_mixed)
                print(f"  [OUTRO] OK")
            else:
                clip_paths.append(outro_clip)
                print(f"  [OUTRO] OK (silent, mix failed)")
        else:
            print(f"  [OUTRO] FAIL — skipping")

    if not clip_paths:
        print("ERROR: No clips assembled")
        sys.exit(1)

    # ── CONCATENATE ───────────────────────────────────────────────
    print(f"\nConcatenating {len(clip_paths)} clips...")
    ok = concatenate_clips(clip_paths, output_path)

    if ok:
        size = os.path.getsize(output_path) / (1024 * 1024)
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        dur = float(result.stdout.strip()) if result.stdout.strip() else 0

        print(f"\nDONE: {output_path}")
        print(f"  Duration: {dur:.0f}s  Size: {size:.1f}MB")

        # Cleanup clips
        shutil.rmtree(clips_dir, ignore_errors=True)
    else:
        print("FAILED to create final video")
        sys.exit(1)


if __name__ == "__main__":
    main()
