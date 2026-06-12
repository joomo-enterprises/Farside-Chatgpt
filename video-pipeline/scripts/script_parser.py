#!/usr/bin/env python3
"""
script_parser.py — Parse SCRIPT.md files into scenes.json for the video pipeline.

Reads a structured SCRIPT.md and converts it into a JSON array of scene objects
that the slidemaker, TTS engine, and video assembler can consume.

Usage:
    python3 script_parser.py <SCRIPT.md> <output.json> [episode_num]

The parser looks for structured markers in the script:
    ## SCENE: <type> | <heading> | <duration_sec>
    ### NARRATION: <text>
    ### BULLETS:
    - bullet 1
    - bullet 2
    ### CODE:
    ```python
    code here
    ```
    ### NOTES:
    - note 1

If no structured markers found, falls back to section-based parsing.
"""

import json
import sys
import re
import os


def parse_structured_script(content, episode_num="01"):
    """Parse a SCRIPT.md with structured scene markers."""
    scenes = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Scene header: ## SCENE: type | heading | duration
        scene_match = re.match(r'^##\s*SCENE:\s*(\w+)\s*\|\s*(.+?)\s*\|\s*(\d+)', line)
        if scene_match:
            scene_type = scene_match.group(1).lower()
            heading = scene_match.group(2).strip()
            duration = int(scene_match.group(3))

            scene = {
                "type": scene_type,
                "heading": heading,
                "duration": duration,
                "episode": episode_num,
                "bullets": [],
                "narration": "",
                "notes": [],
                "code": "",
                "section": "",
            }

            # Parse body until next ## SCENE or end
            i += 1
            code_block = False
            code_lang = ""
            while i < len(lines):
                body_line = lines[i].rstrip()

                if re.match(r'^##\s*SCENE:', body_line.strip()):
                    break

                # Sub-markers
                narr_match = re.match(r'^###\s*NARRATION:\s*(.+)', body_line)
                if narr_match:
                    scene["narration"] = narr_match.group(1).strip()
                    i += 1
                    continue

                if body_line.strip() == "### BULLETS:":
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith('- '):
                        scene["bullets"].append(lines[i].strip()[2:].strip())
                        i += 1
                    continue

                if body_line.strip().startswith("```"):
                    if not code_block:
                        code_block = True
                        code_lang = body_line.strip()[3:].strip()
                        i += 1
                        continue
                    else:
                        code_block = False
                        i += 1
                        continue

                if code_block:
                    scene["code"] += body_line + "\n"
                    i += 1
                    continue

                notes_match = re.match(r'^###\s*NOTES:', body_line)
                if notes_match:
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith('- '):
                        scene["notes"].append(lines[i].strip()[2:].strip())
                        i += 1
                    continue

                section_match = re.match(r'^###\s*SECTION:\s*(.+)', body_line)
                if section_match:
                    scene["section"] = section_match.group(1).strip()
                    i += 1
                    continue

                # Regular text becomes narration if no explicit narration
                if body_line.strip() and not body_line.startswith('#') and not body_line.startswith('---'):
                    if not scene["narration"]:
                        scene["narration"] = body_line.strip()
                    elif not scene["section"]:
                        scene["section"] = body_line.strip()

                i += 1

            # Clean up code
            scene["code"] = scene["code"].rstrip()
            if scene["code"]:
                scene["filename"] = f"{scene_type}_{len(scenes):02d}.py"

            scenes.append(scene)
        else:
            i += 1

    return scenes


def parse_fallback_script(content, episode_num="01"):
    """
    Fallback parser for scripts without structured markers.
    Splits on ## headings and creates content scenes.
    """
    scenes = []
    sections = re.split(r'\n(?=## )', content)

    # First section is usually the title/intro
    title_text = ""
    hook_text = ""

    for idx, section in enumerate(sections):
        lines = section.strip().split('\n')
        if not lines:
            continue

        heading = lines[0].strip().lstrip('#').strip()
        body_lines = [l.strip() for l in lines[1:] if l.strip() and not l.strip().startswith('---')]

        if idx == 0:
            # Title section
            scenes.append({
                "type": "title",
                "title": heading,
                "subtitle": body_lines[0] if body_lines else "",
                "episode": episode_num,
                "duration": 8,
                "narration": f"Welcome to episode {episode_num} of On The FarSide Series. {heading}",
            })
            continue

        # Detect section type from heading
        heading_lower = heading.lower()
        if "hook" in heading_lower or "intro" in heading_lower:
            scene_type = "hook"
            question = heading.replace("HOOK", "").replace("Hook", "").replace(":", "").strip()
            bullets = [l.lstrip('- ').strip() for l in body_lines if l.startswith('-')]
            narration = " ".join([l for l in body_lines if not l.startswith('-')])
            scenes.append({
                "type": "hook",
                "question": question or heading,
                "bullets": bullets[:5],
                "narration": narration,
                "episode": episode_num,
                "duration": max(15, len(bullets) * 5),
            })
        elif "outro" in heading_lower or "next" in heading_lower or "subscribe" in heading_lower:
            scenes.append({
                "type": "outro",
                "heading": heading,
                "subtitle": body_lines[0] if body_lines else "",
                "narration": " ".join(body_lines),
                "episode": episode_num,
                "duration": 15,
            })
        elif "code" in heading_lower or "walkthrough" in heading_lower:
            # Extract code blocks
            code_text = ""
            in_code = False
            for line in lines[1:]:
                if line.strip().startswith("```"):
                    in_code = not in_code
                    continue
                if in_code:
                    code_text += line + "\n"

            bullets = [l.lstrip('- ').strip() for l in body_lines if l.startswith('-')]
            narration = " ".join([l for l in body_lines if not l.startswith('-') and not l.startswith('```')])
            scenes.append({
                "type": "code",
                "heading": heading,
                "section": heading.split(":")[0].strip() if ":" in heading else "Code",
                "code": code_text.rstrip(),
                "bullets": bullets,
                "narration": narration,
                "notes": [l.lstrip('- ').strip() for l in body_lines if l.startswith('-')],
                "episode": episode_num,
                "duration": max(20, len(code_text.split('\n')) * 3),
            })
        elif "comparison" in heading_lower or "vs" in heading_lower or "round" in heading_lower:
            bullets = [l.lstrip('- ').strip() for l in body_lines if l.startswith('-')]
            narration = " ".join([l for l in body_lines if not l.startswith('-')])
            scenes.append({
                "type": "comparison",
                "heading": heading,
                "section": heading.split(":")[0].strip() if ":" in heading else "Comparison",
                "bullets": bullets,
                "narration": narration,
                "cards": [],
                "episode": episode_num,
                "duration": max(15, len(bullets) * 4),
            })
        else:
            # Content scene
            bullets = [l.lstrip('- ').strip() for l in body_lines if l.startswith('-')]
            narration = " ".join([l for l in body_lines if not l.startswith('-')])
            scenes.append({
                "type": "content",
                "heading": heading,
                "section": heading.split(":")[0].strip() if ":" in heading else "",
                "bullets": bullets[:6],
                "narration": narration,
                "extra_narration": "",
                "episode": episode_num,
                "duration": max(15, len(bullets) * 5 + len(narration.split()) * 0.4),
            })

    # Ensure we have an outro
    if scenes and scenes[-1]["type"] != "outro":
        scenes.append({
            "type": "outro",
            "heading": "Go Beyond ChatGPT",
            "subtitle": "Build the Next Generation of AI",
            "narration": "Thanks for watching. If you found this helpful, subscribe and hit the bell. Next episode, we go even deeper.",
            "episode": episode_num,
            "duration": 15,
        })

    return scenes


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 script_parser.py <SCRIPT.md> <output.json> [episode_num]")
        sys.exit(1)

    script_path = sys.argv[1]
    output_path = sys.argv[2]
    episode_num = sys.argv[3] if len(sys.argv) > 3 else "01"

    with open(script_path, 'r') as f:
        content = f.read()

    # Try structured parsing first
    scenes = parse_structured_script(content, episode_num)

    # Fallback if no structured scenes found
    if not scenes:
        print("  No structured markers found, using fallback parser...")
        scenes = parse_fallback_script(content, episode_num)

    if not scenes:
        print("ERROR: No scenes could be parsed from the script")
        sys.exit(1)

    # Round durations
    for s in scenes:
        s["duration"] = max(5, round(s["duration"]))

    with open(output_path, 'w') as f:
        json.dump(scenes, f, indent=2)

    print(f"Parsed {len(scenes)} scenes -> {output_path}")
    for i, s in enumerate(scenes):
        print(f"  [{i+1:3d}] {s['type']:12s} | {s['duration']:3d}s | {s.get('heading', s.get('title', ''))[:50]}")


if __name__ == "__main__":
    main()
