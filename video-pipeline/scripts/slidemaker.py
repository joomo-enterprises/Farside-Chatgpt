#!/usr/bin/env python3
"""
slidemaker.py — Render HTML slides to PNG images for video production.

Reads scenes.json and produces 1920x1080 PNG slides using headless Chrome.
Supports: title, hook, content, code, comparison, outro scene types.

Usage:
    python3 slidemaker.py <scenes.json> <output_dir>
"""

import json
import sys
import os
import subprocess
import tempfile

# Branding constants
BG = "#0f172a"
ORANGE = "#f97316"
WHITE = "#f8fafc"
GRAY = "#cbd5e1"
BLUE = "#3b82f6"
GREEN = "#22c55e"
YELLOW = "#eab308"
RED = "#ef4444"
RES_W = 1920
RES_H = 1080

# HTML template for a single slide
SLIDE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {w}px;
    height: {h}px;
    background: {bg};
    font-family: 'Inter', sans-serif;
    color: {white};
    overflow: hidden;
    position: relative;
}}

/* Orange accent bar on left */
.accent-bar {{
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 8px;
    background: {orange};
}}

/* Top-right series logo */
.series-logo {{
    position: absolute;
    top: 40px; right: 60px;
    font-size: 14px;
    font-weight: 600;
    color: {orange};
    letter-spacing: 2px;
    text-transform: uppercase;
}}

/* Main content area */
.content {{
    position: absolute;
    left: 80px; right: 80px;
    top: 100px; bottom: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

/* Title scene */
.title-episode {{
    font-size: 22px;
    font-weight: 600;
    color: {orange};
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 20px;
}}
.title-main {{
    font-size: 64px;
    font-weight: 800;
    color: {white};
    line-height: 1.1;
    margin-bottom: 20px;
}}
.title-sub {{
    font-size: 28px;
    font-weight: 400;
    color: {gray};
    line-height: 1.4;
}}
.title-author {{
    position: absolute;
    bottom: 50px; left: 80px;
    font-size: 18px;
    color: {gray};
}}

/* Hook scene */
.hook-question {{
    font-size: 56px;
    font-weight: 800;
    color: {white};
    line-height: 1.2;
    margin-bottom: 30px;
}}
.hook-context {{
    font-size: 24px;
    color: {gray};
    line-height: 1.5;
    max-width: 900px;
}}

/* Content scene */
.section-label {{
    font-size: 18px;
    font-weight: 600;
    color: {orange};
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
}}
.content-heading {{
    font-size: 48px;
    font-weight: 800;
    color: {white};
    line-height: 1.2;
    margin-bottom: 30px;
}}
.content-bullets {{
    font-size: 26px;
    color: {gray};
    line-height: 1.8;
    list-style: none;
    padding: 0;
}}
.content-bullets li::before {{
    content: "→ ";
    color: {orange};
    font-weight: 800;
}}
.content-bullets li {{
    margin-bottom: 8px;
}}

/* Code scene */
.code-header {{
    background: #1e293b;
    border-radius: 12px 12px 0 0;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.code-dot {{
    width: 14px; height: 14px;
    border-radius: 50%;
}}
.code-filename {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    color: {gray};
    margin-left: 10px;
}}
.code-body {{
    background: #0d1117;
    border-radius: 0 0 12px 12px;
    padding: 24px 32px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    color: #e6edf3;
    line-height: 1.7;
    max-height: 700px;
    overflow: hidden;
}}
.code-comment {{ color: #8b949e; }}
.code-keyword {{ color: #ff7b72; }}
.code-string {{ color: #a5d6ff; }}
.code-function {{ color: #d2a8ff; }}
.code-number {{ color: #79c0ff; }}

/* Comparison scene */
.comparison-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-top: 20px;
}}
.comparison-card {{
    background: #1e293b;
    border-radius: 16px;
    padding: 32px;
    border: 2px solid #334155;
}}
.comparison-card.winner {{
    border-color: {orange};
}}
.comparison-card h3 {{
    font-size: 28px;
    font-weight: 800;
    color: {white};
    margin-bottom: 12px;
}}
.comparison-card .metric {{
    font-size: 18px;
    color: {gray};
    margin-bottom: 6px;
}}
.comparison-card .metric span {{
    color: {orange};
    font-weight: 600;
}}

/* Outro scene */
.outro-heading {{
    font-size: 56px;
    font-weight: 800;
    color: {white};
    line-height: 1.2;
    margin-bottom: 20px;
}}
.outro-sub {{
    font-size: 24px;
    color: {gray};
    margin-bottom: 40px;
}}
.outro-links {{
    display: flex;
    gap: 20px;
}}
.outro-btn {{
    background: {orange};
    color: {white};
    padding: 14px 32px;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 600;
    text-decoration: none;
}}

/* Progress bar at bottom */
.progress-bar {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 4px;
    background: #1e293b;
}}
.progress-fill {{
    height: 100%;
    background: {orange};
    width: {progress}%;
}}

/* Speaker name tag */
.speaker-tag {{
    position: absolute;
    bottom: 50px; right: 80px;
    font-size: 16px;
    color: {gray};
    letter-spacing: 1px;
}}
</style>
</head>
<body>
<div class="accent-bar"></div>
<div class="series-logo">On The FarSide Series</div>
{body}
<div class="progress-bar"><div class="progress-fill"></div></div>
</body>
</html>
"""


def make_title_slide(scene, total_scenes, scene_idx):
    progress = int((scene_idx / max(total_scenes - 1, 1)) * 100)
    body = f"""
<div class="content">
    <div class="title-episode">Episode {scene.get('episode', '01')}</div>
    <div class="title-main">{scene.get('title', '')}</div>
    <div class="title-sub">{scene.get('subtitle', '')}</div>
</div>
<div class="title-author">FarSide ChatGPT — NinjaTech AI Team</div>
<div class="speaker-tag">On The FarSide Series</div>
"""
    html = SLIDE_TEMPLATE.format(
        w=RES_W, h=RES_H, bg=BG, orange=ORANGE, white=WHITE, gray=GRAY,
        blue=BLUE, green=GREEN, progress=progress, body=body
    )
    return html


def make_hook_slide(scene, total_scenes, scene_idx):
    progress = int((scene_idx / max(total_scenes - 1, 1)) * 100)
    bullets_html = ""
    for b in scene.get("bullets", []):
        bullets_html += f"<li>{b}</li>\n"
    body = f"""
<div class="content">
    <div class="section-label">Hook</div>
    <div class="hook-question">{scene.get('question', '')}</div>
    <ul class="content-bullets">
        {bullets_html}
    </ul>
</div>
<div class="speaker-tag">On The FarSide Series</div>
"""
    html = SLIDE_TEMPLATE.format(
        w=RES_W, h=RES_H, bg=BG, orange=ORANGE, white=WHITE, gray=GRAY,
        blue=BLUE, green=GREEN, progress=progress, body=body
    )
    return html


def make_content_slide(scene, total_scenes, scene_idx):
    progress = int((scene_idx / max(total_scenes - 1, 1)) * 100)
    bullets_html = ""
    for b in scene.get("bullets", []):
        bullets_html += f"<li>{b}</li>\n"
    body = f"""
<div class="content">
    <div class="section-label">{scene.get('section', '')}</div>
    <div class="content-heading">{scene.get('heading', '')}</div>
    <ul class="content-bullets">
        {bullets_html}
    </ul>
</div>
<div class="speaker-tag">On The FarSide Series</div>
"""
    html = SLIDE_TEMPLATE.format(
        w=RES_W, h=RES_H, bg=BG, orange=ORANGE, white=WHITE, gray=GRAY,
        blue=BLUE, green=GREEN, progress=progress, body=body
    )
    return html


def make_code_slide(scene, total_scenes, scene_idx):
    progress = int((scene_idx / max(total_scenes - 1, 1)) * 100)
    code = scene.get("code", "")
    # Escape HTML
    code_escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = f"""
<div class="content" style="top:80px; bottom:80px;">
    <div class="section-label">{scene.get('section', 'Code')}</div>
    <div class="content-heading" style="font-size:36px; margin-bottom:20px;">{scene.get('heading', '')}</div>
    <div class="code-header">
        <div class="code-dot" style="background:#ff5f57;"></div>
        <div class="code-dot" style="background:#febc2e;"></div>
        <div class="code-dot" style="background:#28c840;"></div>
        <div class="code-filename">{scene.get('filename', 'main.py')}</div>
    </div>
    <div class="code-body"><pre>{code_escaped}</pre></div>
</div>
<div class="speaker-tag">On The FarSide Series</div>
"""
    html = SLIDE_TEMPLATE.format(
        w=RES_W, h=RES_H, bg=BG, orange=ORANGE, white=WHITE, gray=GRAY,
        blue=BLUE, green=GREEN, progress=progress, body=body
    )
    return html


def make_comparison_slide(scene, total_scenes, scene_idx):
    progress = int((scene_idx / max(total_scenes - 1, 1)) * 100)
    cards_html = ""
    for card in scene.get("cards", []):
        winner_class = " winner" if card.get("winner") else ""
        metrics_html = ""
        for m in card.get("metrics", []):
            metrics_html += f'<div class="metric">{m.get("label", "")}: <span>{m.get("value", "")}</span></div>\n'
        cards_html += f"""
<div class="comparison-card{winner_class}">
    <h3>{card.get('name', '')}</h3>
    {metrics_html}
</div>
"""
    body = f"""
<div class="content">
    <div class="section-label">{scene.get('section', 'Comparison')}</div>
    <div class="content-heading" style="font-size:40px;">{scene.get('heading', '')}</div>
    <div class="comparison-grid">
        {cards_html}
    </div>
</div>
<div class="speaker-tag">On The FarSide Series</div>
"""
    html = SLIDE_TEMPLATE.format(
        w=RES_W, h=RES_H, bg=BG, orange=ORANGE, white=WHITE, gray=GRAY,
        blue=BLUE, green=GREEN, progress=progress, body=body
    )
    return html


def make_outro_slide(scene, total_scenes, scene_idx):
    progress = 100
    body = f"""
<div class="content">
    <div class="section-label">Thanks for watching</div>
    <div class="outro-heading">{scene.get('heading', 'Go Beyond ChatGPT')}</div>
    <div class="outro-sub">{scene.get('subtitle', 'Build the Next Generation of AI')}</div>
    <div class="outro-links">
        <div class="outro-btn">Subscribe</div>
        <div class="outro-btn" style="background:#1e293b; border:2px solid {ORANGE};">Next Episode</div>
    </div>
</div>
<div class="title-author">FarSide ChatGPT — Available now from Joomo Enterprises Publishing</div>
<div class="speaker-tag">On The FarSide Series</div>
"""
    html = SLIDE_TEMPLATE.format(
        w=RES_W, h=RES_H, bg=BG, orange=ORANGE, white=WHITE, gray=GRAY,
        blue=BLUE, green=GREEN, progress=progress, body=body
    )
    return html


SLIDE_MAKERS = {
    "title": make_title_slide,
    "hook": make_hook_slide,
    "content": make_content_slide,
    "code": make_code_slide,
    "comparison": make_comparison_slide,
    "outro": make_outro_slide,
}


def render_slide_html(scene, total_scenes, scene_idx):
    scene_type = scene.get("type", "content")
    maker = SLIDE_MAKERS.get(scene_type, make_content_slide)
    return maker(scene, total_scenes, scene_idx)


def html_to_png(html_content, output_path):
    """Render HTML to PNG using headless Chrome."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        tmp_path = f.name

    try:
        cmd = [
            "google-chrome-stable", "--headless", "--disable-gpu",
            "--no-sandbox", "--disable-dev-shm-usage",
            "--window-size=1920,1080",
            "--screenshot=" + output_path,
            "file://" + tmp_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            # Try chromium-browser
            cmd[0] = "chromium-browser"
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            # Try chromium
            cmd[0] = "chromium"
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ERROR: Chrome render failed: {result.stderr[:200]}", file=sys.stderr)
            return False
        return os.path.exists(output_path)
    finally:
        os.unlink(tmp_path)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 slidemaker.py <scenes.json> <output_dir>")
        sys.exit(1)

    scenes_path = sys.argv[1]
    output_dir = sys.argv[2]

    with open(scenes_path, 'r') as f:
        scenes = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    total = len(scenes)

    print(f"Rendering {total} slides to {output_dir}/")

    for i, scene in enumerate(scenes):
        scene_type = scene.get("type", "content")
        html = render_slide_html(scene, total, i)
        out_file = os.path.join(output_dir, f"slide_{i:03d}.png")

        ok = html_to_png(html, out_file)
        status = "OK" if ok else "FAIL"
        heading = scene.get("heading", scene.get("title", scene.get("question", "")))[:50]
        print(f"  [{i+1:3d}/{total}] {status} {scene_type:12s} | {heading}")

    print(f"\nDone. {total} slides in {output_dir}/")


if __name__ == "__main__":
    main()
