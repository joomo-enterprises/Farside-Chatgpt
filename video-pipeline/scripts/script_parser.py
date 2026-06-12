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
    Handles the SCRIPT.md format with ## sections containing ### sub-sections.
    Each ### sub-section becomes a scene.
    """
    scenes = []
    lines = content.split('\n')

    # First pass: extract title from the very first # heading
    title_text = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            title_text = stripped.lstrip('#').strip()
            break

    # Add title scene
    scenes.append({
        "type": "title",
        "title": title_text or f"Episode {episode_num}",
        "subtitle": f"Farside Series — Episode {episode_num}",
        "episode": episode_num,
        "duration": 10,
        "narration": f"Welcome to episode {episode_num} of the Farside Series.",
    })

    # Split into ## sections
    sections = re.split(r'\n(?=## )', content)

    for section in sections:
        section_lines = section.split('\n')
        if not section_lines:
            continue

        section_heading = section_lines[0].strip().lstrip('#').strip()
        section_lower = section_heading.lower()

        # Skip non-content sections
        if any(skip in section_lower for skip in ['episode info', 'production notes', 'code for episode',
                                                     'timestamps', 'script outline']):
            # But script outline contains our scenes, so parse its ### sub-sections
            if 'script outline' not in section_lower:
                continue

        # Split section into ### sub-sections
        sub_sections = re.split(r'\n(?=### )', section)

        for sub in sub_sections:
            sub_lines = sub.split('\n')
            if not sub_lines:
                continue

            sub_heading = sub_lines[0].strip().lstrip('#').strip()
            sub_lower = sub_heading.lower()

            # Skip sub-sections that are metadata
            if any(skip in sub_lower for skip in ['production notes', 'screen recordings', 'graphics needed',
                                                     'b-roll', 'music:', 'code for episode', 'timestamps',
                                                     'files to create:']):
                continue

            # Determine scene type
            scene_type = "content"
            if "hook" in sub_lower:
                scene_type = "hook"
            elif "outro" in sub_lower:
                scene_type = "outro"
            elif "code" in sub_lower or "demo" in sub_lower or "walkthrough" in sub_lower:
                scene_type = "code"
            elif "comparison" in sub_lower or "vs" in sub_lower:
                scene_type = "comparison"

            # Extract content from sub-section
            narration_parts = []
            bullets = []
            code_text = ""
            notes = []
            screen_text = ""
            in_code = False
            in_key_point = False

            for line in sub_lines[1:]:
                stripped = line.strip()

                # Skip horizontal rules
                if stripped == '---':
                    continue

                # Skip screen markers but extract text
                screen_match = re.match(r'^\*\*\[SCREEN:\s*(.+?)\]\*\*', stripped)
                if screen_match:
                    screen_text = screen_match.group(1).strip()
                    continue

                # Skip screen markers in brackets
                screen_match2 = re.match(r'^\[SCREEN:\s*(.+?)\]', stripped)
                if screen_match2:
                    screen_text = screen_match2.group(1).strip()
                    continue

                # KEY POINT ON SCREEN block
                if '**KEY POINT ON SCREEN:**' in stripped or '[KEY POINT ON SCREEN]' in stripped:
                    in_key_point = True
                    continue

                if in_key_point:
                    if stripped.startswith('```'):
                        in_key_point = False
                        continue
                    # Parse key point lines like "Text:" or "✓ item"
                    clean = stripped.lstrip('✓').lstrip('- ').strip()
                    if clean:
                        bullets.append(clean)
                    continue

                # Code blocks
                if stripped.startswith('```'):
                    in_code = not in_code
                    continue
                if in_code:
                    code_text += line + '\n'
                    continue

                # Bullet points
                if stripped.startswith('- ') or stripped.startswith('* '):
                    bullet_text = stripped[2:].strip()
                    if bullet_text and not bullet_text.startswith('**'):
                        bullets.append(bullet_text)
                    continue

                # Bold narration lines (NARRATION:)
                narr_match = re.match(r'^\*\*NARRATION:\*\*\s*"?(.+?)"?$', stripped)
                if narr_match:
                    narration_parts.append(narr_match.group(1).strip().strip('"'))
                    continue

                if stripped.upper() == 'NARRATION:' or stripped == '### NARRATION:':
                    continue

                # Regular text → narration
                if stripped and not stripped.startswith('#') and not stripped.startswith('**['):
                    # Skip bold section markers within narration
                    clean = stripped.strip('*').strip()
                    if clean and len(clean) > 3:
                        narration_parts.append(clean)

            # Build scene
            narration = ' '.join(narration_parts).strip()
            code_text = code_text.rstrip()

            # Determine heading — strip timestamps and clean up
            heading = sub_heading
            # Remove timestamp patterns like "(0:45 - 2:30)" from heading
            heading = re.sub(r'\s*\(\d+:\d+\s*-\s*\d+:\d+\)\s*$', '', heading).strip()
            heading = re.sub(r'^\*\*|\*\*$', '', heading).strip()
            # Remove "SECTION N:" / "PROBLEM N:" prefix for cleaner display
            clean_heading = re.match(r'^(?:SECTION|PROBLEM)\s+\d+:\s*(.+)', heading)
            display_heading = clean_heading.group(1) if clean_heading else heading

            # Calculate duration: ~150 words per minute for narration
            word_count = len(narration.split())
            duration = max(10, word_count * 60 // 150 + len(bullets) * 3)

            scene = {
                "type": scene_type,
                "heading": display_heading[:80],
                "subtitle": heading[:80],
                "section": sub_heading[:60] if sub_heading != heading else "",
                "bullets": bullets[:8],
                "narration": narration[:2000],
                "notes": notes[:4],
                "code": code_text[:3000] if code_text else "",
                "screen": screen_text[:100],
                "episode": episode_num,
                "duration": min(duration, 120),  # Cap at 2 min per scene
            }

            if code_text:
                scene["filename"] = f"scene_{len(scenes):02d}.py"

            # Only add scenes with actual content
            if narration or bullets or code_text:
                scenes.append(scene)

    # Ensure outro exists
    if scenes and scenes[-1]["type"] != "outro":
        scenes.append({
            "type": "outro",
            "heading": "Go Beyond ChatGPT",
            "subtitle": "Build the Next Generation of AI",
            "narration": "Thanks for watching. If you found this helpful, subscribe and hit the bell. All the code from this episode is in the GitHub repo linked in the description. And if you want the deep dive, grab the FarSide ChatGPT book. Link below.",
            "episode": episode_num,
            "duration": 20,
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
