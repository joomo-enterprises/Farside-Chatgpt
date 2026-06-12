#!/usr/bin/env python3
"""
video_assembler.py — Assemble slides + mixed audio into final video.

Takes slide PNGs and mixed audio MP3s, produces MP4 per scene,
then concatenates into final episode video.

Usage:
    python3 video_assembler.py <slides_dir> <audio_dir> <output_path>

Requires: ffmpeg
"""

import sys
import os
import subprocess
import json


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
    # d = total number of output frames = duration * fps
    total_frames = max(1, int(duration * 30))
    vf = f"zoompan=z='1.0+0.0005*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1920x1080:fps=30"

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

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=max(60, int(duration * 2)))

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
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=max(60, int(duration * 2)))
        if result2.returncode != 0:
            print(f"  ERROR assembling scene: {result2.stderr[:200]}", file=sys.stderr)
            return False

    return os.path.exists(output_path)


def add_transition(clip1_path, clip2_path, output_path, transition_type="fade", duration=0.5):
    """Add a transition between two video clips."""
    # For concat demuxer approach, transitions are complex
    # Simpler: just use xfade filter
    # We'll handle this during concat instead
    return False


def concatenate_clips(clip_paths, output_path):
    """Concatenate video clips into final video using concat demuxer."""
    # Create concat list file in the same dir as output for relative path resolution
    concat_dir = os.path.dirname(os.path.abspath(output_path))
    concat_list = os.path.join(concat_dir, "concat_list.txt")
    with open(concat_list, 'w') as f:
        for clip_path in clip_paths:
            # Use absolute paths to avoid relative path issues
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


def add_intro_outro(episode_num, title, output_path):
    """Generate intro branded clip."""
    # We'll handle this as part of the slide set
    pass


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 video_assembler.py <slides_dir> <audio_dir> <output_path>")
        sys.exit(1)

    slides_dir = sys.argv[1]
    audio_dir = sys.argv[2]
    output_path = sys.argv[3]

    # Get slide and audio files
    slides = get_files_sorted(slides_dir, "slide_", ".png")
    audio_files = get_files_sorted(audio_dir, "scene_", "_mixed.mp3")

    if not slides:
        print("ERROR: No slide PNGs found")
        sys.exit(1)
    if not audio_files:
        print("ERROR: No mixed audio files found")
        sys.exit(1)

    # Create temp dir for individual clips
    clips_dir = output_path + "_clips"
    os.makedirs(clips_dir, exist_ok=True)

    print(f"Assembling video: {len(slides)} slides, {len(audio_files)} audio tracks")
    print(f"Output: {output_path}")

    # Map audio to slides by scene number
    audio_map = {}
    for af in audio_files:
        # scene_003_mixed.mp3 -> 003
        num = af.replace("scene_", "").replace("_mixed.mp3", "")
        audio_map[num] = os.path.join(audio_dir, af)

    clip_paths = []
    for i, slide in enumerate(slides):
        slide_num = slide.replace("slide_", "").replace(".png", "")
        slide_path = os.path.join(slides_dir, slide)
        audio_path = audio_map.get(slide_num)

        if not audio_path:
            # No mixed audio - try raw narration
            raw_audio = os.path.join(audio_dir.replace("_mixed", ""), f"scene_{slide_num}.mp3")
            if os.path.exists(raw_audio):
                audio_path = raw_audio
            else:
                print(f"  [{i+1:3d}/{len(slides)}] SKIP  slide_{slide_num} (no audio)")
                continue

        clip_path = os.path.join(clips_dir, f"clip_{slide_num}.mp4")

        print(f"  [{i+1:3d}/{len(slides)}] slide_{slide_num} ...", end="", flush=True)
        ok = slide_to_video(slide_path, audio_path, clip_path)
        status = "OK" if ok else "FAIL"
        print(f"\r  [{i+1:3d}/{len(slides)}] slide_{slide_num} -> {status}")

        if ok:
            clip_paths.append(clip_path)

    if not clip_paths:
        print("ERROR: No clips assembled")
        sys.exit(1)

    # Final audio normalization pass on assembly
    print(f"\nConcatenating {len(clip_paths)} clips...")
    ok = concatenate_clips(clip_paths, output_path)

    if ok:
        size = os.path.getsize(output_path) / (1024 * 1024)
        # Get duration
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        dur = float(result.stdout.strip()) if result.stdout.strip() else 0

        print(f"\nDONE: {output_path}")
        print(f"  Duration: {dur:.0f}s  Size: {size:.1f}MB")

        # Cleanup clips
        import shutil
        shutil.rmtree(clips_dir, ignore_errors=True)
    else:
        print("FAILED to create final video")
        sys.exit(1)


if __name__ == "__main__":
    main()
