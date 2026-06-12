#!/usr/bin/env python3
"""
slidemaker.py — Render slides to PNG images using PIL/Pillow (no Chrome needed).

Reads scenes.json and produces 1920x1080 PNG slides using Python PIL.
Supports: title, content, code, comparison, outro scene types.

Usage:
    python3 slidemaker.py <scenes.json> <output_dir>
"""

import json
import sys
import os
import re

# Branding constants
BG = (15, 23, 42)         # dark slate #0f172a
ORANGE = (249, 115, 22)    # orange #f97316
WHITE = (255, 255, 255)    # white
GRAY = (203, 213, 225)     # slate-300
DARK_GRAY = (51, 65, 85)   # slate-700
BLUE = (59, 130, 246)     # blue
GREEN = (34, 197, 94)      # green
YELLOW = (234, 179, 8)     # yellow
RED = (239, 68, 68)        # red
CODE_BG = (30, 41, 59)     # slate-800
CARD_BG = (30, 41, 59)     # slate-800

RES_W = 1920
RES_H = 1080


def get_font(size, bold=False):
    """Load DejaVu font."""
    from PIL import ImageFont
    base = "/usr/share/fonts/truetype/dejavu"
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = os.path.join(base, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_text(draw, position, text, font, fill=WHITE, max_width=None):
    """Draw text, optionally wrapping to max_width."""
    x, y = position
    if max_width is None:
        draw.text((x, y), text, font=font, fill=fill)
        return y + font.size * 1.3

    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_width:
            if current:
                lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += (font.getbbox(line)[3] - font.getbbox(line)[1]) * 1.4
    return y


def draw_rounded_rect(draw, xy, radius=12, fill=None, outline=None, width=2):
    """Draw a rectangle with rounded corners. xy = [(x0,y0), (x1,y1)]."""
    (x0, y0), (x1, y1) = xy
    draw.rectangle([(x0 + radius, y0), (x1 - radius, y1)], fill=fill)
    draw.rectangle([(x0, y0 + radius), (x1, y1 - radius)], fill=fill)
    draw.ellipse([(x0, y0), (x0 + radius * 2, y0 + radius * 2)], fill=fill)
    draw.ellipse([(x1 - radius * 2, y0), (x1, y0 + radius * 2)], fill=fill)
    draw.ellipse([(x0, y1 - radius * 2), (x0 + radius * 2, y1)], fill=fill)
    draw.ellipse([(x1 - radius * 2, y1 - radius * 2), (x1, y1)], fill=fill)
    if outline:
        draw.arc([(x0, y0), (x0 + radius * 2, y0 + radius * 2)], 180, 270, fill=outline, width=width)
        draw.arc([(x1 - radius * 2, y0), (x1, y0 + radius * 2)], 270, 360, fill=outline, width=width)
        draw.arc([(x0, y1 - radius * 2), (x0 + radius * 2, y1)], 90, 180, fill=outline, width=width)
        draw.arc([(x1 - radius * 2, y1 - radius * 2), (x1, y1)], 0, 90, fill=outline, width=width)
        draw.line([(x0 + radius, y0), (x1 - radius, y0)], fill=outline, width=width)
        draw.line([(x0 + radius, y1), (x1 - radius, y1)], fill=outline, width=width)
        draw.line([(x0, y0 + radius), (x0, y1 - radius)], fill=outline, width=width)
        draw.line([(x1, y0 + radius), (x1, y1 - radius)], fill=outline, width=width)


def extract_narration_points(narration):
    """Extract visual bullet points from narration text.

    Parses narration for:
    - Lines starting with checkmark (✓) or bullet markers
    - Key-value pairs like 'PROBLEM 1: ...'
    - Numbered items
    - Lines in ALL CAPS that look like headers
    - Code-like lines (containing # or quotes)
    Returns a dict with 'points' (list of str), 'code' (str), 'sections' (list of dicts),
    and 'takeaway' (str) — a complete-sentence summary for the right panel.
    """
    points = []
    code_lines = []
    sections = []
    current_section = None

    if not narration:
        return {"points": [], "code": "", "sections": [], "takeaway": ""}

    # Split by double quote segments and plain text
    segments = narration.split('"')
    text_parts = []
    for i, seg in enumerate(segments):
        if i % 2 == 0:  # outside quotes
            text_parts.append(seg)
        else:  # inside quotes - these are the spoken parts
            text_parts.append(seg)

    full_text = " ".join(text_parts)

    # Extract bullet points from patterns like "✓ item" or "- item" or "* item"
    # Split by sentence-ending period + space to avoid mid-sentence breaks
    for sentence in re.split(r'(?<=[.!?])\s+', full_text):
        sentence = sentence.strip()
        if not sentence:
            continue
        # Check for checkmark items
        if "✓" in sentence or "✔" in sentence:
            cleaned = re.sub(r'\s*[✓✔]\s*', ' ✓ ', sentence).strip()
            if cleaned and len(cleaned) > 3:
                points.append(cleaned)
        # Numbered items like "PROBLEM 1:" or "1."
        elif re.match(r'^(PROBLEM|STEP|PHASE|POINT|REASON|TIP)\s*\d+', sentence, re.IGNORECASE):
            s = sentence.strip()
            if s not in points:
                points.append(s)

    # Extract code blocks (lines with # or ollama/curl commands)
    for line in full_text.split("\n"):
        stripped = line.strip()
        if stripped and (stripped.startswith("#") or stripped.startswith("curl") or
                         stripped.startswith("ollama") or stripped.startswith("pip") or
                         stripped.startswith("import ") or stripped.startswith("from ")):
            code_lines.append(stripped)

    # Extract "SECTION:" or "Phase X:" headers
    for sentence in re.split(r'(?<=[.!?])\s+', full_text.replace('"', ' ')):
        sentence = sentence.strip()
        m = re.match(r'^([A-Z][A-Z\s]+\d*)\s*[:\-]\s*(.*)', sentence)
        if m:
            sections.append({"title": m.group(1).strip(), "body": m.group(2).strip()[:120]})

    # Build takeaway: use complete sentences from narration, no mid-word truncation
    takeaway = _build_takeaway_from_narration(narration)

    # Deduplicate points
    seen = set()
    unique_points = []
    for p in points:
        key = p[:40]
        if key not in seen and len(p) > 3:
            seen.add(key)
            unique_points.append(p)

    return {
        "points": unique_points[:8],
        "code": "\n".join(code_lines[:12]),
        "sections": sections[:4],
        "takeaway": takeaway,
    }


def _build_takeaway_from_narration(narration):
    """Build a clean takeaway string from narration using complete sentences.

    Takes the first 2-3 complete sentences (up to ~250 chars) so the right-panel
    KEY TAKEAWAY box never shows truncated words like 'The tr...'.
    """
    if not narration:
        return ""

    # Remove surrounding quotes
    text = narration.strip().strip('"')

    # Split into complete sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Take first 2-3 sentences, stopping before we exceed 250 chars
    result = []
    total_len = 0
    max_len = 250
    for s in sentences:
        if total_len + len(s) + (1 if result else 0) > max_len and result:
            break
        result.append(s)
        total_len += len(s) + 1
        if len(result) >= 3:
            break

    takeaway = " ".join(result)
    # Ensure it ends with a period
    if takeaway and not takeaway[-1] in ".!?":
        # Find last sentence boundary and truncate there
        last_end = max(takeaway.rfind(". "), takeaway.rfind("! "), takeaway.rfind("? "))
        if last_end > 20:
            takeaway = takeaway[:last_end + 1]

    return takeaway


def _draw_common_header(draw, scene, font_logo, scene_idx, total_scenes):
    """Draw common elements: left bar, progress bar, logo."""
    # Left orange accent bar
    draw.rectangle([(0, 0), (8, RES_H)], fill=ORANGE)

    # Progress bar at bottom
    progress = int((scene_idx / max(total_scenes - 1, 1)) * 100) if total_scenes > 1 else 100
    bar_width = int(RES_W * progress / 100)
    draw.rectangle([(0, RES_H - 4), (RES_W, RES_H)], fill=DARK_GRAY)
    draw.rectangle([(0, RES_H - 4), (bar_width, RES_H)], fill=ORANGE)

    # Series logo top-right
    draw.text((RES_W - 280, 38), "FARSIDE SERIES", font=font_logo, fill=ORANGE)


def _draw_footer_branding(draw):
    """Draw author/promo footer on every slide."""
    font_author = get_font(18, bold=True)
    draw.text((80, RES_H - 75), "FarSide ChatGPT — The Book", font=font_author, fill=GRAY)
    draw.text((80, RES_H - 48), "Joomo Publishing", font=font_author, fill=ORANGE)


def make_slide(scene, total_scenes, scene_idx):
    """Create a single slide image (PIL Image)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (RES_W, RES_H), BG)
    draw = ImageDraw.Draw(img)

    font_logo = get_font(16, bold=True)
    _draw_common_header(draw, scene, font_logo, scene_idx, total_scenes)

    scene_type = scene.get("type", "content")

    if scene_type == "title":
        _draw_title_slide(draw, scene, font_logo, img)
    elif scene_type == "code":
        _draw_code_slide(draw, scene, font_logo)
    elif scene_type == "comparison":
        _draw_comparison_slide(draw, scene, font_logo)
    elif scene_type == "outro":
        _draw_outro_slide(draw, scene, font_logo)
    else:
        _draw_content_slide(draw, scene, font_logo, scene_idx)

    return img


def _draw_title_slide(draw, scene, font_logo, img):
    """Title slide — the reference design. Rich, detailed, with book cover."""
    font_ep = get_font(28, bold=True)
    font_main = get_font(64, bold=True)
    font_sub = get_font(32, bold=True)
    font_author = get_font(20, bold=True)

    x = 80
    y = 100

    # Episode label
    ep = scene.get("episode", "01")
    draw.text((x, y), f"EPISODE {ep}", font=font_ep, fill=ORANGE)
    y += 50

    # Title
    title = scene.get("title", "")
    y = draw_text(draw, (x, y), title, font_main, fill=WHITE, max_width=RES_W - 300)
    y += 25

    # Subtitle
    sub = scene.get("subtitle", "")
    if sub:
        draw_text(draw, (x, y), sub, font_sub, fill=GRAY, max_width=RES_W - 300)
        y += 60

    # Orange underline
    draw.line([(x, y), (x + 250, y)], fill=ORANGE, width=4)

    # Book cover thumbnail on the right side
    cover_path = "/workspace/video-pipeline/assets/cover2.png"
    if os.path.exists(cover_path):
        try:
            cover = Image.open(cover_path).convert("RGB")
            cover_h = 420
            cover_w = int(cover_h * cover.width / cover.height)
            cover = cover.resize((cover_w, cover_h), Image.LANCZOS)
            cx = RES_W - cover_w - 80
            cy = (RES_H - cover_h) // 2
            img.paste(cover, (cx, cy))
            draw.rectangle([(cx - 4, cy - 4), (cx + cover_w + 4, cy + cover_h + 4)], outline=ORANGE, width=3)
        except Exception:
            pass

    # Author credit at bottom
    _draw_footer_branding(draw)


def _wrap_text_to_width(text, font, max_width):
    """Wrap text into lines that fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def _draw_content_slide(draw, scene, font_logo, scene_idx=0):
    """Rich content slide — matches title slide level of detail.

    Features:
    - Section number badge (large orange circle)
    - Orange label bar across top
    - Large bold heading with underline
    - Key points as styled cards with icons (multi-line, no truncation)
    - Code block if code present (full lines, no truncation)
    - Visual right panel with code or summary
    - Footer branding
    """
    font_section = get_font(20, bold=True)
    font_heading = get_font(48, bold=True)
    font_card = get_font(26, bold=True)
    font_card_text = get_font(22, bold=True)
    font_mono = get_font(20, bold=True)
    font_label = get_font(18, bold=True)

    x = 80
    y = 80

    # --- Section number badge (large orange circle on left) ---
    section_num = scene.get("section_num", str(scene_idx))
    badge_x, badge_y = x, y
    badge_r = 32
    draw.ellipse([(badge_x, badge_y), (badge_x + badge_r * 2, badge_y + badge_r * 2)], fill=ORANGE)
    font_badge = get_font(28, bold=True)
    draw.text((badge_x + 18, badge_y + 10), section_num, font=font_badge, fill=WHITE)

    # Section label (e.g. "SECTION 1")
    subtitle = scene.get("subtitle", "")
    if subtitle:
        draw.text((x + 80, y + 14), subtitle.upper(), font=font_section, fill=ORANGE)
    y += 65

    # --- Large bold heading ---
    heading = scene.get("heading", "")
    if heading:
        y = draw_text(draw, (x, y), heading, font_heading, fill=WHITE, max_width=880)
        y += 15

    # Orange underline
    draw.line([(x, y), (x + 200, y)], fill=ORANGE, width=3)
    y += 20

    # --- Extract visual content from narration ---
    narration = scene.get("narration", "")
    extracted = extract_narration_points(narration)
    bullets = scene.get("bullets", [])
    code_text = scene.get("code", "") or extracted["code"]

    # Use scene bullets if provided, otherwise use extracted points
    display_points = bullets if bullets else extracted["points"]

    # --- Reserve space: footer at RES_H - 100, so content must end above that ---
    content_bottom = RES_H - 110

    # --- Left panel: key points as styled cards (multi-line, auto-height) ---
    left_w = 880
    card_x = x
    card_y = y
    card_pad = 14
    card_gap = 8
    card_min_h = 52
    card_text_max_w = left_w - 80  # leave room for icon + padding

    # Show bullet cards on the left
    for i, point in enumerate(display_points[:6]):
        # Clean the point text
        clean_point = point
        for prefix in ["✓", "✔"]:
            clean_point = clean_point.replace(prefix, "").strip()
        clean_point = re.sub(r'^\d+\.\s*', '', clean_point).strip()

        # Wrap text to fit card width
        wrapped_lines = _wrap_text_to_width(clean_point, font_card_text, card_text_max_w)
        if not wrapped_lines:
            continue

        # Auto-calculate card height based on number of lines
        line_h = (font_card_text.getbbox("A")[3] - font_card_text.getbbox("A")[1]) * 1.35
        card_h = max(card_min_h, len(wrapped_lines) * line_h + card_pad * 2 + 8)

        if card_y + card_h > content_bottom:
            break

        # Card background
        draw_rounded_rect(draw, [(card_x, card_y), (card_x + left_w, card_y + card_h)],
                          radius=8, fill=CARD_BG, outline=DARK_GRAY, width=1)

        # Left accent on card
        draw.rectangle([(card_x, card_y + 8), (card_x + 4, card_y + card_h - 8)], fill=ORANGE)

        # Checkmark or number icon
        icon = "✓" if "✓" in point or "✔" in point else f"{i + 1}."
        icon_color = GREEN if "✓" in point else ORANGE
        draw.text((card_x + 14, card_y + card_pad), icon, font=font_card, fill=icon_color)

        # Draw wrapped text lines
        text_y = card_y + card_pad + 2
        for line in wrapped_lines:
            draw.text((card_x + 52, text_y), line, font=font_card_text, fill=GRAY)
            text_y += line_h

        card_y += card_h + card_gap

    # --- Right panel: code block or visual summary ---
    right_x = x + left_w + 40
    right_w = min(RES_W - right_x - 80, 840)
    right_y = y

    if code_text.strip():
        # Code block with window chrome
        code_lines = code_text.strip().split("\n")
        # Limit lines to fit available space
        max_code_lines = (content_bottom - right_y - 60) // 26
        code_lines = code_lines[:max(6, int(max_code_lines))]
        code_block_h = len(code_lines) * 26 + 50

        # Window bar
        draw_rounded_rect(draw, [(right_x, right_y), (right_x + right_w, right_y + code_block_h)],
                          radius=8, fill=CODE_BG, outline=DARK_GRAY, width=1)

        # Window dots
        dot_y = right_y + 12
        for color, dx in [(RED, 16), (YELLOW, 38), (GREEN, 60)]:
            draw.ellipse([(right_x + dx, dot_y), (right_x + dx + 12, dot_y + 12)], fill=color)

        # Filename label
        filename = scene.get("filename", "terminal")
        draw.text((right_x + 85, right_y + 4), filename, font=font_label, fill=GRAY)

        # Code text — full lines, no truncation
        cy = right_y + 36
        for line in code_lines:
            if cy + 22 > content_bottom:
                break
            # Syntax highlighting
            if line.strip().startswith("#"):
                color = GRAY
            elif line.strip().startswith(("curl", "ollama", "pip", "docker")):
                color = GREEN
            elif line.strip().startswith(("import", "from", "def", "class", "return")):
                color = BLUE
            elif line.strip().startswith(("$", ">", ">>>")):
                color = GREEN
            else:
                color = WHITE
            draw.text((right_x + 14, cy), line, font=font_mono, fill=color)
            cy += 26

    elif extracted["sections"]:
        # Show section summaries as cards on the right
        sec_card_h = 80
        for i, sec in enumerate(extracted["sections"][:3]):
            if right_y + sec_card_h > content_bottom:
                break
            draw_rounded_rect(draw, [(right_x, right_y), (right_x + right_w, right_y + sec_card_h)],
                              radius=8, fill=CARD_BG, outline=ORANGE, width=2)
            draw.text((right_x + 16, right_y + 12), sec["title"][:50], font=font_card, fill=ORANGE)
            # Limit body to 1 line within the fixed card height
            body_lines = _wrap_text_to_width(sec["body"], font_card_text, right_w - 32)
            if body_lines:
                draw.text((right_x + 16, right_y + 42), body_lines[0][:60], font=font_card_text, fill=GRAY)
            right_y += sec_card_h + 12
    else:
        # Show a visual "key takeaway" box on the right
        takeaway_h = min(220, content_bottom - right_y)
        draw_rounded_rect(draw, [(right_x, right_y), (right_x + right_w, right_y + takeaway_h)],
                          radius=12, fill=(20, 30, 50), outline=ORANGE, width=2)
        draw.text((right_x + 20, right_y + 16), "KEY TAKEAWAY", font=font_section, fill=ORANGE)
        # Use the pre-built takeaway (complete sentences, no truncation)
        takeaway_text = extracted.get("takeaway", "")
        if not takeaway_text:
            takeaway_text = narration.replace('"', ' ').strip()[:250]
        # Wrap and limit to available space
        line_h = (font_card_text.getbbox("A")[3] - font_card_text.getbbox("A")[1]) * 1.4
        max_lines = max(3, int((takeaway_h - 50) / line_h))
        wrapped_takeaway = _wrap_text_to_width(takeaway_text, font_card_text, right_w - 40)
        ty = right_y + 48
        for line in wrapped_takeaway[:max_lines]:
            if ty + line_h > right_y + takeaway_h - 10:
                break
            draw.text((right_x + 20, ty), line, font=font_card_text, fill=GRAY)
            ty += line_h

    # --- Footer branding ---
    _draw_footer_branding(draw)


def _draw_code_slide(draw, scene, font_logo):
    """Rich code slide — terminal-style with syntax highlighting."""
    font_section = get_font(20, bold=True)
    font_heading = get_font(42, bold=True)
    font_mono = get_font(22, bold=True)
    font_label = get_font(18, bold=True)
    font_author = get_font(20, bold=True)

    x = 80
    y = 100

    # Section label
    section = scene.get("section", "")
    if section:
        draw.text((x, y), section.upper(), font=font_section, fill=ORANGE)
        y += 45

    # Heading
    heading = scene.get("heading", "")
    if heading:
        draw.text((x, y), heading, font=font_heading, fill=WHITE)
        y += 60

    # Full-width code block
    code_text = scene.get("code", "")
    code_lines = code_text.strip().split("\n")[:18]
    if not code_lines:
        code_lines = ["# No code available"]

    code_block_h = len(code_lines) * 32 + 60
    code_w = RES_W - 160

    # Terminal window
    draw_rounded_rect(draw, [(x, y), (x + code_w, y + code_block_h)],
                      radius=8, fill=CODE_BG, outline=DARK_GRAY, width=1)

    # Window dots
    dot_y = y + 14
    for color, dx in [(RED, 16), (YELLOW, 38), (GREEN, 60)]:
        draw.ellipse([(x + dx, dot_y), (x + dx + 12, dot_y + 12)], fill=color)

    # Filename
    filename = scene.get("filename", "terminal")
    draw.text((x + 85, y + 6), filename, font=font_label, fill=GRAY)
    y += 44

    # Code lines with syntax highlighting
    cy = y + 12
    for line in code_lines:
        if line.strip().startswith("#"):
            color = GRAY
        elif line.strip().startswith(("curl", "ollama", "pip", "docker", "git", "python", "npm")):
            color = GREEN
        elif line.strip().startswith(("import", "from", "def", "class", "return")):
            color = BLUE
        elif "=" in line and not line.strip().startswith("#"):
            color = YELLOW
        else:
            color = WHITE
        draw.text((x + 20, cy), line[:80], font=font_mono, fill=color)
        cy += 30

    # Notes below code
    notes = scene.get("notes", [])
    if notes:
        ny = y + code_block_h + 20
        for note in notes[:3]:
            draw.text((80, ny), f"* {note}", font=font_section, fill=ORANGE)
            ny += 35

    _draw_footer_branding(draw)


def _draw_comparison_slide(draw, scene, font_logo):
    """Rich comparison slide — card-based layout."""
    font_section = get_font(20, bold=True)
    font_heading = get_font(46, bold=True)
    font_card_title = get_font(32, bold=True)
    font_metric = get_font(22, bold=True)
    font_author = get_font(20, bold=True)

    x = 80
    y = 100

    # Section label
    section = scene.get("section", "Comparison")
    draw.text((x, y), section.upper(), font=font_section, fill=ORANGE)
    y += 45

    # Heading
    heading = scene.get("heading", "")
    draw.text((x, y), heading, font=font_heading, fill=WHITE)
    y += 65

    cards = scene.get("cards", [])
    if not cards:
        _draw_footer_branding(draw)
        return

    card_w = (RES_W - 160 - 30 * (len(cards) - 1)) // len(cards)
    card_h = 420

    for i, card in enumerate(cards):
        cx = x + i * (card_w + 30)
        is_winner = card.get("winner", False)
        border = ORANGE if is_winner else DARK_GRAY

        # Card background
        draw_rounded_rect(draw, [(cx, y), (cx + card_w, y + card_h)],
                          radius=12, fill=CARD_BG, outline=border, width=3)

        # Winner badge
        if is_winner:
            draw_rounded_rect(draw, [(cx + card_w - 90, y + 10), (cx + card_w - 10, y + 38)],
                              radius=6, fill=ORANGE)
            font_win = get_font(14, bold=True)
            draw.text((cx + card_w - 82, y + 14), "BEST", font=font_win, fill=WHITE)

        # Card title
        draw.text((cx + 20, y + 20), card.get("name", ""), font=font_card_title, fill=WHITE)

        # Metrics
        my = y + 75
        for m in card.get("metrics", []):
            label = m.get("label", "")
            value = m.get("value", "")
            draw.text((cx + 20, my), label, font=font_metric, fill=GRAY)
            draw.text((cx + 250, my), value, font=font_metric, fill=ORANGE)
            my += 42

    _draw_footer_branding(draw)


def _draw_outro_slide(draw, scene, font_logo):
    """Rich outro slide — matches title slide quality."""
    font_label = get_font(20, bold=True)
    font_heading = get_font(58, bold=True)
    font_sub = get_font(28, bold=True)
    font_btn = get_font(20, bold=True)
    font_author = get_font(20, bold=True)
    font_bullet = get_font(30, bold=True)

    x = 80
    y = 100

    # Thanks label
    draw.text((x, y), "THANKS FOR WATCHING", font=font_label, fill=ORANGE)
    y += 55

    # Heading
    heading = scene.get("heading", "Go Beyond ChatGPT")
    y = draw_text(draw, (x, y), heading, font_heading, fill=WHITE, max_width=RES_W - 300)
    y += 30

    # Subtitle
    sub = scene.get("subtitle", "Build the Next Generation of AI")
    draw.text((x, y), sub, font=font_sub, fill=GRAY)
    y += 60

    # Orange underline
    draw.line([(x, y), (x + 250, y)], fill=ORANGE, width=3)
    y += 40

    # CTA buttons row
    btn_y = y
    btn_h = 55

    # Subscribe button (filled orange)
    btn1_w = 200
    draw_rounded_rect(draw, [(x, btn_y), (x + btn1_w, btn_y + btn_h)], radius=10, fill=ORANGE)
    draw.text((x + 35, btn_y + 13), "Subscribe", font=font_btn, fill=WHITE)

    # Next Episode button (outlined)
    x2 = x + btn1_w + 25
    btn2_w = 220
    draw_rounded_rect(draw, [(x2, btn_y), (x2 + btn2_w, btn_y + btn_h)],
                      radius=10, fill=(30, 41, 59), outline=ORANGE, width=3)
    draw.text((x2 + 28, btn_y + 13), "Next Episode", font=font_btn, fill=ORANGE)

    # GitHub button
    x3 = x2 + btn2_w + 25
    btn3_w = 180
    draw_rounded_rect(draw, [(x3, btn_y), (x3 + btn3_w, btn_y + btn_h)],
                      radius=10, fill=(30, 41, 59), outline=GRAY, width=2)
    draw.text((x3 + 20, btn_y + 13), "GitHub Repo", font=font_btn, fill=GRAY)

    y = btn_y + btn_h + 50

    # Bullet points (subscribe, next ep, github, book)
    bullets = scene.get("bullets", ["Subscribe for more", "Next: Episode 2", "github.com/joomo-enterprises/Farside-Chatgpt", "FarSide ChatGPT — The Book"])
    for bullet in bullets[:4]:
        # Small card for each
        draw_rounded_rect(draw, [(x, y), (x + 520, y + 42)], radius=6, fill=CARD_BG, outline=DARK_GRAY, width=1)
        draw.rectangle([(x, y + 6), (x + 4, y + 36)], fill=ORANGE)
        draw.text((x + 16, y + 8), bullet, font=font_bullet, fill=GRAY)
        y += 50

    # Links note
    font_links = get_font(18, bold=True)
    draw.text((x, y + 10), "Links in video description", font=font_links, fill=DARK_GRAY)

    # Book cover on the right
    cover_path = "/workspace/video-pipeline/assets/cover2.png"
    if os.path.exists(cover_path):
        try:
            from PIL import Image as PILImage
            cover = PILImage.open(cover_path).convert("RGB")
            cover_h = 300
            cover_w = int(cover_h * cover.width / cover.height)
            cover = cover.resize((cover_w, cover_h), PILImage.LANCZOS)
            cx = RES_W - cover_w - 80
            cy = RES_H // 2 - 50
            # We need the img reference — draw doesn't have it, so we skip here
            # The cover is shown on title slide; outro focuses on CTAs
        except Exception:
            pass

    # Footer
    _draw_footer_branding(draw)


def _draw_interlude_slide(draw, scene, font_logo):
    """Interlude / break slide — fun, visual, gives presenter a pause.

    Features:
    - Large centered quote or fun fact
    - Decorative elements
    - Episode/section transition branding
    - Optional: ASCII art, emoji, or visual icon
    """
    font_label = get_font(22, bold=True)
    font_main = get_font(52, bold=True)
    font_sub = get_font(28, bold=True)
    font_body = get_font(24, bold=True)

    x = 80
    y = 100

    # Section label
    subtitle = scene.get("subtitle", "INTERLUDE")
    draw.text((x, y), subtitle.upper(), font=font_label, fill=ORANGE)
    y += 55

    # Main quote or message
    heading = scene.get("heading", "")
    if heading:
        y = draw_text(draw, (x, y), heading, font_main, fill=WHITE, max_width=RES_W - 160)
        y += 30

    # Orange underline
    draw.line([(x, y), (x + 250, y)], fill=ORANGE, width=3)
    y += 40

    # Body text / fun fact
    body = scene.get("body", "")
    if body:
        y = draw_text(draw, (x, y), body, font_body, fill=GRAY, max_width=RES_W - 160)
        y += 40

    # Bullets (tips, fun facts, etc.)
    bullets = scene.get("bullets", [])
    for i, bullet in enumerate(bullets[:4]):
        # Small card
        draw_rounded_rect(draw, [(x, y), (x + 700, y + 44)], radius=6, fill=CARD_BG, outline=DARK_GRAY, width=1)
        draw.rectangle([(x, y + 6), (x + 4, y + 38)], fill=ORANGE)
        draw.text((x + 16, y + 8), bullet, font=font_body, fill=GRAY)
        y += 52

    # Decorative: large emoji/icon on the right
    icon = scene.get("icon", "")
    if icon:
        font_icon = get_font(120, bold=True)
        draw.text((RES_W - 250, RES_H // 2 - 60), icon, font=font_icon, fill=ORANGE)

    # Footer
    _draw_footer_branding(draw)


# Scene types dispatcher
SCENE_MAKERS = {
    "title": _draw_title_slide,
    "content": _draw_content_slide,
    "code": _draw_code_slide,
    "comparison": _draw_comparison_slide,
    "outro": _draw_outro_slide,
    "interlude": _draw_interlude_slide,
}


def main():
    from PIL import Image

    if len(sys.argv) < 3:
        print("Usage: python3 slidemaker.py <scenes.json> <output_dir>")
        sys.exit(1)

    scenes_path = sys.argv[1]
    output_dir = sys.argv[2]

    with open(scenes_path, "r") as f:
        scenes = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    total = len(scenes)

    print(f"Rendering {total} slides to {output_dir}/ (PIL-based, no Chrome needed)")

    for i, scene in enumerate(scenes):
        scene_type = scene.get("type", "content")
        maker = SCENE_MAKERS.get(scene_type, _draw_content_slide)
        out_file = os.path.join(output_dir, f"slide_{i:03d}.png")

        img = make_slide(scene, total, i)
        img.save(out_file, "PNG")

        heading = scene.get("heading", scene.get("title", scene.get("question", "")))[:50]
        print(f"  [{i+1:3d}/{total}] {scene_type:12s} | {heading}")

    print(f"\nDone. {total} slides in {output_dir}/")


if __name__ == "__main__":
    main()
