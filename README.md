# Fencing Drill

Fencing footwork training app that calls out French commands with configurable timing and modes. Practice solo like you have a coach.

## Features

- 4 training modes (Basic, Combination, Random, Interval)
- 3 weapon types with auto-adjusted tempo (Foil, Épée, Sabre)
- Authentic French fencing commands with audio
- Real-time command delivery via SSE
- PWA support for offline use in the gym
- Multi-language UI (Japanese, English, French)
- Mobile-friendly responsive design

## Training Modes

| Mode | Purpose |
|------|---------|
| **Basic** | Single command repetition for form practice |
| **Combination** | Preset patterns for movement coordination |
| **Random** | Unpredictable commands for reaction training |
| **Interval** | High-intensity intervals with rest periods |

## Commands

| French | Description |
|--------|-------------|
| En garde | Guard position |
| Marchez | Advance |
| Rompez | Retreat |
| Fendez | Lunge |
| Allongez le bras | Extend arm |
| Remise en garde | Return to guard |
| Balancez | Sway forward/back |
| Bond en avant | Jump forward |
| Bond en arrière | Jump backward |

## Weapons

| Weapon | Tempo | Notes |
|--------|-------|-------|
| **Foil** | Standard | Default weapon |
| **Épée** | Slower (0.8x) | More balancez emphasis |
| **Sabre** | Faster (1.3x) | Includes flèche, excludes balancez |

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Frontend:** htmx, Tailwind CSS, Jinja2
- **Audio:** Pre-recorded MP3 files
- **Communication:** Server-Sent Events (SSE)

## Getting Started

### Prerequisites

- Python 3.11 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/fencing-drill.git
cd fencing-drill

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
# Start the development server
uvicorn main:app --reload

# Open in browser
open http://localhost:8000
```

### Testing

```bash
pytest
```

## Project Structure

```
fencing-drill/
├── main.py              # FastAPI application
├── logic/
│   ├── commands.py      # Command definitions
│   ├── generator.py     # Command generation per mode
│   └── session.py       # Session state management
├── templates/           # Jinja2 + htmx templates
├── static/
│   ├── audio/           # Command audio files (MP3)
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript (audio, i18n)
└── tests/               # pytest test files
```

## License

MIT
