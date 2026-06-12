#!/usr/bin/env python3
"""
YouTube Thumbnail Generator for Farside Series
- 1280x720 YouTube standard
- Dark slate + orange branding
- Book cover image embedded
- Pixel-perfect text (no AI spelling errors)
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

# === CONFIG ===
WIDTH, HEIGHT = 1280, 720
BG_COLOR = (15, 23, 42)         # dark slate #0f172a
ORANGE = (249, 115, 22)        # orange #f97316
WHITE = (255, 255, 255)
LIGHT_GRAY = (203, 213, 225)   # slate-300
DARK_ORANGE = (194, 65, 12)    # orange-700

BOOK_COVER_PATH = "/mnt/c/k/author/farside-chatgpt/cover2.png"
OUTPUT_DIR = "/mnt/c/k/author/farside-chatgpt-youtube/thumbnails"

# Episode data: (number, title_line1, title_line2)
EPISODES = [
    ("01", "Why Beyond", "ChatGPT?"),
    ("02", "The Model", "Showdown"),
    ("03", "Multimodal", "AI"),
    ("04", "Setting Up Your", "Dev Environment"),
    ("05", "Build Your Own", "Local Chatbot"),
    ("06", "AI Ethics You", "Cannot Ignore"),
    ("07", "The Math Behind", "AI"),
    ("08", "ML Fundamentals", "80/20 Guide"),
]

def get_font(size, bold=False):
    """Try to load a system font, fall back to default."""
    font_dirs = [
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/dejavu",
        "/usr/share/fonts/TTF",
        "/usr/share/fonts",
    ]
    if bold:
        names = ["DejaVuSans-Bold.ttf", "DejaVuSans-Bold.otf"]
    else:
        names = ["DejaVuSans.ttf", "DejaVuSans.otf"]
    
    for d in font_dirs:
        for n in names:
            path = os.path.join(d, n)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    
    # Fallback to default
    return ImageFont.load_default()

def get_font_with_fallback(size, bold=False):
    """Try multiple font locations including Windows fonts on WSL."""
    # Try Windows fonts via WSL mount first (much better quality)
    win_font_dirs = [
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/dejavu",
    ]
    
    if bold:
        names = ["DejaVuSans-Bold.ttf", "DejaVuSans-Bold.otf"]
    else:
        names = ["DejaVuSans.ttf", "DejaVsans.otf"]
    
    for d in win_font_dirs:
        for n in names:
            path = os.path.join(d, n)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    
    return ImageFont.load_default()

def _wrap_text(draw, text, font, max_width):
    """Wrap text into lines that fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        tw = bbox[2] - bbox[0]
        if tw <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines if lines else [text]


def create_thumbnail(episode_num, line1, line2, cover_img, output_path):
    """Create a single thumbnail with guaranteed correct text."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # === LEFT ORANGE BAR ===
    bar_width = 8
    draw.rectangle([(0, 0), (bar_width, HEIGHT)], fill=ORANGE)

    # === ORANGE ACCENT TOP-RIGHT GLOW ===
    for i in range(200):
        alpha = max(0, 200 - i)
        x_start = WIDTH - 400 + i
        draw.rectangle(
            [(x_start, 0), (x_start + 1, HEIGHT)],
            fill=(ORANGE[0], ORANGE[1], ORANGE[2])
        )

    # === BOOK COVER (right side, circular) ===
    cover_size = 420
    try:
        cover = cover_img.copy()
        cover = cover.resize((cover_size, cover_size), Image.Resampling.LANCZOS)

        # Create circular mask
        mask = Image.new("L", (cover_size, cover_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, cover_size, cover_size], fill=255)

        # Orange border ring
        border = Image.new("RGBA", (cover_size + 16, cover_size + 16), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border)
        border_draw.ellipse([0, 0, cover_size + 15, cover_size + 15],
                           outline=ORANGE, width=6)

        # Paste cover
        cover_pos = (WIDTH - cover_size - 80, (HEIGHT - cover_size) // 2 - 30)
        border_pos = (cover_pos[0] - 8, cover_pos[1] - 8)

        img.paste(border, border_pos)
        img.paste(cover, cover_pos, mask)

        # Add subtle orange shadow under circle
        shadow = Image.new("RGBA", (cover_size + 40, 30), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.ellipse([10, 0, cover_size + 30, 30],
                           fill=(249, 115, 22, 40))
        img.paste(shadow, (cover_pos[0] - 20, cover_pos[1] + cover_size + 10), shadow)
    except Exception as e:
        print(f"  Warning: could not embed cover: {e}")

    # === EPISODE NUMBER (top-left, small) ===
    ep_label = f"EPISODE {episode_num}"
    font_ep = get_font_with_fallback(28, bold=True)
    draw.text((40, 40), ep_label, fill=ORANGE, font=font_ep)

    # === MAIN TITLE (left-center, big) ===
    # Constrict text to left zone: margin 40 to (cover_left - 40)
    left_margin = 40
    cover_left_edge = WIDTH - cover_size - 80  # same as cover_pos[0]
    text_max_w = cover_left_edge - left_margin - 40  # 40px gap from cover

    # Try big font first, scale down if needed
    for font_size in [88, 78, 68, 58]:
        font_title = get_font_with_fallback(font_size, bold=True)
        lines1 = _wrap_text(draw, line1, font_title, text_max_w)
        lines2 = _wrap_text(draw, line2, font_title, text_max_w)
        total_lines = len(lines1) + len(lines2)
        line_h = font_size + 12
        total_h = total_lines * line_h + 115  # +underline+padding
        if total_h <= HEIGHT - 160:
            break

    # Vertical centering
    total_block_h = (len(lines1) + len(lines2)) * line_h + 15  # +underline gap
    start_y = (HEIGHT - total_block_h) // 2 - 20

    # Draw line 1 (white)
    y = start_y
    for l in lines1:
        draw.text((left_margin, y), l, fill=WHITE, font=font_title)
        y += line_h

    # Draw line 2 (orange)
    for l in lines2:
        draw.text((left_margin, y), l, fill=ORANGE, font=font_title)
        y += line_h

    # === DECORATIVE UNDERLINE ===
    draw.line(
        [(left_margin, y + 5), (left_margin + 300, y + 5)],
        fill=ORANGE, width=4
    )

    # === BOOK TITLE (bottom-left, subtle) ===
    font_book = get_font_with_fallback(22, bold=False)
    draw.text(
        (left_margin, HEIGHT - 60),
        "FarSide ChatGPT — The Book",
        fill=LIGHT_GRAY, font=font_book
    )

    # === SERIES NAME (top-right, small) ===
    font_series = get_font_with_fallback(20, bold=True)
    draw.text(
        (WIDTH - 280, 42),
        "FARSIDE SERIES",
        fill=ORANGE, font=font_series
    )

    # === SAVE ===
    img.save(output_path, "PNG", quality=95)
    print(f"  Created: {output_path}")
    return output_path

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load book cover once
    print(f"Loading book cover from: {BOOK_COVER_PATH}")
    cover = Image.open(BOOK_COVER_PATH).convert("RGBA")
    print(f"Cover size: {cover.size}")
    
    # Get required fonts
    fonts_needed = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48),
    ]
    
    print("\nNote: Install DejaVu fonts for best results:")
    print("  sudo apt install fonts-dejavu  (on pod)")
    print()
    
    for ep_num, line1, line2 in EPISODES:
        fname = f"ep{ep_num}.png"
        output = os.path.join(OUTPUT_DIR, fname)
        create_thumbnail(ep_num, line1, line2, cover, output)
    
    print(f"\nAll {len(EPISODES)} thumbnails generated in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
