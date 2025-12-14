# Fencing Drill - Project Plan

## Overview

フェンシングのフットワーク練習をサポートするAIコーチアプリ。フランス語の掛け声を自動で発声し、練習者は号令に従って動く。

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI |
| Frontend | htmx, Tailwind CSS, Jinja2 |
| Audio | Pre-recorded MP3 files |
| Communication | SSE (Server-Sent Events) |

---

## Training Modes

### Mode 1: 基礎反復 (Basic)

**目的**: 単一動作のフォーム定着

**設定項目**:
- 動作の種類（マルシェ / ロンペ / ファンドゥ など）
- 反復回数（5〜50回）
- テンポ（30〜120 BPM）

**フロー**:
```
[アンギャルド] → [選択した動作] × N回 → [終了通知]
```

---

### Mode 2: コンビネーション (Combination)

**目的**: 決まったパターンの動作連携を習得

**設定項目**:
- プリセットパターン選択
- 繰り返し回数
- テンポ

**プリセット例**:

| パターン | 内容 |
|---------|------|
| A (前進攻撃) | マルシェ → マルシェ → アロンジェ・ル・ブラ → ファンドゥ → ルミーズ・アンギャルド |
| B (後退からの反撃) | ロンペ → ロンペ → マルシェ → ファンドゥ → ルミーズ・アンギャルド |
| C (フットワーク強化) | マルシェ → マルシェ → ロンペ → マルシェ → ロンペ → ロンペ |

---

### Mode 3: ランダム (Random)

**目的**: 反応速度向上、実戦対応力

**設定項目**:
- 使用コマンドセット（初級/中級/上級）
- 練習時間（1分〜10分）
- テンポ範囲（最小〜最大間隔）
- 不規則度（タイミングのばらつき）

**コマンドセット**:

| Level | Commands |
|-------|----------|
| 初級 | マルシェ、ロンペ |
| 中級 | + ファンドゥ、ルミーズ・アンギャルド |
| 上級 | + ボンナバン、ボンナリエール、バランセ |

**制約ロジック**:
- 同方向に5回以上連続しない（壁対策）
- ファンドゥの後は必ずルミーズ・アンギャルド
- ボンナバン/ボンナリエールの後は少し長めの間隔

---

### Mode 4: インターバル (Interval)

**目的**: 持久力・瞬発力強化

**設定項目**:
- 高強度時間（15秒〜60秒）
- 休憩時間（10秒〜30秒）
- セット数（3〜10セット）
- 高強度時のテンポ

**フロー**:
```
[準備] 3秒カウントダウン
  ↓
[高強度] 速いテンポでランダムコマンド
  ↓
[休憩] 「休憩」→ カウントダウン表示
  ↓
(繰り返し)
  ↓
[終了] 「終了」
```

---

## Commands (Fencing French)

| French | Japanese | Description |
|--------|----------|-------------|
| En garde | アンギャルド | 構えの姿勢 |
| Marchez | マルシェ | 前進 |
| Rompez | ロンペ | 後退 |
| Allongez le bras | アロンジェ・ル・ブラ | 腕を伸ばせ |
| Fendez | ファンドゥ | 突け（ランジ動作） |
| Remise en garde | ルミーズ・アンギャルド | 構えに戻れ |
| Balancez | バランセ | 前後に揺れる動作 |
| Double marchez | ドゥブル・マルシェ | 二歩前進 |
| Bond en avant | ボンナバン | 跳躍前進 |
| Bond en arrière | ボンナリエール | 跳躍後退 |

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│  ┌───────────────────────────────────────────────┐  │
│  │  htmx + HTML/CSS                              │  │
│  │  - UI interaction                             │  │
│  │  - Receive commands via SSE                   │  │
│  │  - Play audio (JavaScript Audio API)          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         ↕ HTTP / SSE
┌─────────────────────────────────────────────────────┐
│              Python Backend (FastAPI)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Command     │  │ Session     │  │ Audio File  │  │
│  │ Generator   │  │ Manager     │  │ Server      │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Static Audio Files                     │
│  /static/audio/en_garde.mp3, marche.mp3, ...       │
└─────────────────────────────────────────────────────┘
```

---

## API Design

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET | `/settings/{mode}` | Settings panel HTML fragment for htmx |
| POST | `/session/start` | Start training session |
| POST | `/session/stop` | Stop training session |
| GET | `/session/stream` | SSE endpoint for real-time commands |
| GET | `/static/audio/{name}` | Serve audio files |

### SSE Event Format

```
event: command
data: {"id": "marche", "fr": "Marchez", "jp": "マルシェ", "audio": "/static/audio/marche.mp3"}

event: status
data: {"remaining": "2:34", "rep": 5, "total": 20}

event: end
data: {"message": "終了"}
```

---

## Directory Structure

```
fencing-drill/
├── main.py                 # FastAPI application
├── CLAUDE.md               # AI assistant context
├── plan.md                 # This file
├── requirements.txt
├── logic/
│   ├── __init__.py
│   ├── commands.py         # Command definitions
│   ├── generator.py        # Command generation per mode
│   └── session.py          # Session state management
├── templates/
│   ├── index.html          # Main dashboard
│   └── components/
│       ├── settings_basic.html
│       ├── settings_combination.html
│       ├── settings_random.html
│       └── settings_interval.html
├── static/
│   ├── css/
│   │   └── style.css       # Additional styles (if needed)
│   ├── js/
│   │   └── audio.js        # Audio playback control
│   └── audio/
│       ├── en_garde.mp3
│       ├── marche.mp3
│       ├── rompe.mp3
│       ├── fendez.mp3
│       ├── allongez.mp3
│       ├── remise.mp3
│       ├── balancez.mp3
│       ├── bond_avant.mp3
│       ├── bond_arriere.mp3
│       ├── repos.mp3       # 休憩
│       └── termine.mp3     # 終了
└── docs/
    ├── commands.md
    ├── modes.md
    └── api.md
```

---

## Audio Strategy

**Approach**: Pre-recorded audio files (recommended)

**Reasons**:
- Accurate French pronunciation (critical for fencing)
- Clear audio quality for gym environments
- No network latency
- Consistent playback

**File Creation Options**:
1. Self-recording (most authentic)
2. Professional TTS services (Amazon Polly, Google Cloud TTS with French voice)
3. Free TTS for prototyping, replace later

**For MVP**: Use Google TTS or gTTS to generate placeholder audio files.

---

## Implementation Phases

### Phase 1: Core Infrastructure ✅ DONE
- [x] FastAPI app setup (`main.py`)
- [x] Command definitions (`logic/commands.py`)
- [x] Basic session management (`logic/session.py`)
- [x] SSE endpoint implementation
- [x] Tests (41 tests)

### Phase 2: Mode Implementation ✅ DONE
- [x] Basic mode generator (implemented in SSE stream)
- [x] Random mode generator (implemented in SSE stream)
- [x] Combination mode generator (`logic/generator.py`)
- [x] Interval mode generator (`logic/generator.py`)
- [x] Random mode constraints (壁対策、ファンドゥ後のルミーズ、ボンド後の遅延)
- [x] Tests (21 tests in `tests/test_generator.py`)

### Phase 3: Frontend Integration ✅ DONE
- [x] Dashboard HTML (`templates/index.html`)
- [x] Settings panel components per mode (4 files)
- [x] htmx + SSE integration
- [x] Audio playback JavaScript (`static/js/audio.js`)

### Phase 4: Audio Files ✅ DONE
- [x] Generate placeholder audio with TTS (19 audio files generated)
- [x] Test audio playback timing (43 tests in `tests/test_audio.py`)
- [ ] (Optional) Replace with professional recordings

### Phase 5: Polish ✅ DONE
- [x] Mobile responsiveness (touch-friendly, responsive layouts)
- [x] Error handling (input validation, SSE errors, 422/404/410 responses)
- [x] Session recovery on disconnect (pause/resume, status API)
- [x] PWA support (manifest, service worker, offline caching)

### Phase 6: Multi-language Support ✅ DONE
- [x] Translation data (`static/js/i18n.js`) for Japanese, English, French
- [x] Language selector in header with localStorage persistence
- [x] data-i18n attributes on all translatable UI elements
- [x] Localized command display during training sessions
- [x] Localized Command Reference section
- [x] Localized unit labels (times, seconds, minutes, sets)
- [x] Auto-apply translations after htmx content swaps
- [x] Tests (14 tests in `tests/test_i18n.py`)

---

## UI Design

**Theme**: Dark, steel/silver base with gold accents (inspired by fencing blades)

**Fonts**:
- Display: Bebas Neue
- Body: Noto Sans JP

**Key Components**:
- Mode selector cards (left column)
- Dynamic settings panel (updates via htmx)
- Large command display (center, highly visible)
- Start/Stop controls
- Command reference section

---

## Open Questions

1. **Audio file sourcing** — Record ourselves? Use TTS service? (Currently using TTS placeholder)
2. ~~**Offline support** — PWA for gym use without internet?~~ ✅ Implemented in Phase 5
3. **Multi-user** — Future support for class/group training?
4. **Custom patterns** — Allow users to create their own combination patterns?
5. ~~**Multi-language** — 日本語/English/Français切り替え?~~ ✅ Implemented in Phase 6

---

## Completed

- [x] Project concept and requirements
- [x] 4 training modes defined
- [x] System architecture design
- [x] API design
- [x] Directory structure
- [x] Dashboard HTML (Tailwind + htmx)
- [x] CLAUDE.md
- [x] **Phase 1: Core Infrastructure** (FastAPI, Commands, Session, SSE)
- [x] **Phase 2: Mode Implementation** (Combination, Interval, Random constraints)
- [x] **Phase 3: Frontend Integration** (htmx + SSE, Settings panels, Audio JS)
- [x] **Phase 4: Audio Files** (19 audio files, 43 tests)
- [x] **Phase 5: Polish** (mobile responsiveness, error handling, session recovery, PWA)
- [x] **Phase 6: Multi-language Support** (ja/en/fr, data-i18n attributes, language selector)
- [x] Tests: 149 tests passing (TDD)

## Next Steps

1. **Phase 7: Additional Features** — カスタムパターン作成、グループ練習対応など