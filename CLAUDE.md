# Fencing Drill

## What

AI-powered fencing footwork training assistant that calls out French commands (like a coach) with configurable timing and modes.

**Stack:** Python 3.11+, FastAPI, htmx, Tailwind CSS, Jinja2 templates

**Structure:**
```
fencing-drill/
├── main.py              # FastAPI app entry point
├── logic/
│   ├── commands.py      # Command definitions (French/Japanese)
│   ├── generator.py     # Command generation per mode
│   └── session.py       # Training session state
├── templates/           # Jinja2 + htmx templates
├── static/
│   ├── audio/           # Pre-recorded command audio files
│   └── css/
└── docs/                # Design docs (read when needed)
```

## Why

Fencers need to practice footwork drills with randomized commands at varying tempos. This app replaces a human coach for solo practice by generating commands and playing audio.

**4 Training Modes:**
1. **Basic** - Single command repetition (e.g., "Marchez" x20)
2. **Combination** - Preset patterns (e.g., advance-advance-lunge)
3. **Random** - Unpredictable commands for reaction training
4. **Interval** - High-intensity intervals with rest periods

## How

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn main:app --reload

# Run tests
pytest
```

**Key conventions:**
- Use SSE (`/session/stream`) for real-time command delivery
- Audio files are static assets, not generated at runtime
- All API responses for htmx return HTML fragments, not JSON

## Docs

Read these only when working on related features:
- `docs/commands.md` - Full list of fencing commands with French pronunciation
- `docs/modes.md` - Detailed logic for each training mode
- `docs/api.md` - API endpoint specifications