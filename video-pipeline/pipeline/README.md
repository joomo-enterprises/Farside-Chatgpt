# On The FarSide Series — Video Production Pipeline

Automated video production system for turning SCRIPT.md files into
YouTube-ready MP4s with slides, voiceover, background music, and
branding.

## Requirements

**Hardware (RunPod A4000):**
- 128 cores, 503GB RAM, 16GB VRAM
- ffmpeg (already installed)
- Chrome/Chromium for slide rendering

**Python packages:**
- edge-tts (voiceover)
- pydub (audio manipulation)
- Pillow (already installed)
- scipy (already installed)

## Pipeline Stages

```
SCRIPT.md -> parse_scenes.py -> scenes.json
scenes.json -> slidemaker.py -> slides/*.png
scenes.json -> tts_engine.py -> audio/narrator/*.mp3
audio/narrator + music -> audio_pipeline.py -> audio/mixed/*.mp3
slides + mixed audio -> video_assembler.py -> output/episode-N.mp4
```

## Usage

```bash
# Install dependencies
pip install edge-tts pydub

# Render a single episode
./produce.sh 1

# Render all episodes
./produce.sh all

# Render specific episodes
./produce.sh 1 3 5
```

## Scene Types

| Type | Description | Visual |
|------|-------------|--------|
| title | Episode title card | Full-screen branded |
| hook | Opening hook | Speaker + key visual |
| content | Main content | Bullet points / diagrams |
| code | Code walkthrough | Syntax-highlighted code |
| comparison | Side-by-side comparison | Split layout |
| outro | End card | Subscribe + next episode |

## Branding

- Background: #0f172a (dark slate)
- Primary accent: #f97316 (orange)
- Text: #f8fafc (white)
- Font: Inter (titles), JetBrains Mono (code)
- Resolution: 1920x1080 (16:9)
- FPS: 30
- Audio: AAC 320kbps, -14 LUFS
