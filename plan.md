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

1. **Audio file sourcing** — Record ourselves? Use TTS service?
2. **Offline support** — PWA for gym use without internet?
3. **Multi-user** — Future support for class/group training?
4. **Custom patterns** — Allow users to create their own combination patterns?

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
- [x] Tests: 135 tests passing (TDD)

## Next Steps

1. **Phase 6: Multi-language Support** — 日本語/English/Français切り替え

---

## Phase 6: Multi-language Support (計画中)

### 概要
ヘッダー右上に言語セレクターを配置し、UI全体を日本語・英語・フランス語に切り替え可能にする。

### 対応言語
| Code | Language | 表示名 |
|------|----------|--------|
| ja | 日本語 | 日本語 |
| en | English | English |
| fr | Français | Français |

### 翻訳対象

**1. UIラベル（静的テキスト）**
- ヘッダー: "Training Assistant", "準備完了"
- モード名: "基礎反復", "コンビネーション", "ランダム", "インターバル"
- モード説明: "単一動作の反復練習" など
- 設定パネル: "Settings", 各設定項目のラベル
- ボタン: "開始", "停止"
- ステータス: "Current Mode", "Session Active"
- コマンドリファレンス: "Command Reference", 各コマンドの日本語説明

**2. コマンド表示**
- コマンドの日本語名（マルシェ、ロンペ など）
- コマンドのフランス語名（Marchez, Rompez など）→ 全言語共通で表示

**3. メッセージ**
- "設定を確認して「開始」を押してください"
- "終了" など

### 実装アプローチ

**A. 翻訳データ構造**
```python
# logic/i18n.py
TRANSLATIONS = {
    "ja": {
        "header.assistant": "Training Assistant",
        "header.ready": "準備完了",
        "mode.basic": "基礎反復",
        "mode.basic.desc": "単一動作の反復練習",
        "mode.combination": "コンビネーション",
        "mode.combination.desc": "パターン練習",
        "mode.random": "ランダム",
        "mode.random.desc": "反応速度トレーニング",
        "mode.interval": "インターバル",
        "mode.interval.desc": "高強度トレーニング",
        "button.start": "開始",
        "button.stop": "停止",
        "status.idle": "設定を確認して「開始」を押してください",
        "status.finished": "終了",
        # ... 他のキー
    },
    "en": {
        "header.assistant": "Training Assistant",
        "header.ready": "Ready",
        "mode.basic": "Basic",
        "mode.basic.desc": "Single action repetition",
        # ...
    },
    "fr": {
        "header.assistant": "Assistant d'entraînement",
        "header.ready": "Prêt",
        "mode.basic": "Basique",
        "mode.basic.desc": "Répétition d'un mouvement",
        # ...
    }
}
```

**B. 言語切り替えUI（ヘッダー右上）**
```html
<select id="language-selector" class="...">
    <option value="ja">日本語</option>
    <option value="en">English</option>
    <option value="fr">Français</option>
</select>
```

**C. 言語保存**
- `localStorage` に選択言語を保存
- ページロード時に復元
- クッキーでサーバーサイドにも伝達（オプション）

**D. 翻訳適用方法**

*方法1: サーバーサイドレンダリング*
- Jinja2テンプレートで翻訳関数を使用
- `{{ t("mode.basic") }}` のような形式
- 言語切り替え時はページリロード

*方法2: クライアントサイド切り替え*
- JavaScript で DOM を更新
- `data-i18n="mode.basic"` 属性でマーキング
- リアルタイム切り替え（リロード不要）

**推奨: 方法2（クライアントサイド）**
- UXが良い（即座に切り替わる）
- htmxとの相性が良い
- SSEイベントの翻訳も容易

### 実装手順

**Step 1: 翻訳データ作成**
- [ ] `static/js/i18n.js` に翻訳データを定義
- [ ] 全UIテキストのキーを洗い出し
- [ ] 3言語分の翻訳を作成

**Step 2: HTML マーキング**
- [ ] 翻訳対象要素に `data-i18n` 属性を追加
- [ ] プレースホルダーテキストを設定

**Step 3: 言語セレクター実装**
- [ ] ヘッダーに言語ドロップダウンを追加
- [ ] localStorage で言語設定を保存/復元
- [ ] 言語変更イベントハンドラを実装

**Step 4: 翻訳適用ロジック**
- [ ] `applyTranslations(lang)` 関数を実装
- [ ] ページロード時に自動適用
- [ ] htmx更新後にも再適用

**Step 5: テスト**
- [ ] 各言語での表示確認
- [ ] 言語切り替えの動作確認
- [ ] localStorage永続化の確認

### 注意事項

1. **コマンド音声は変更しない**
   - フェンシング用語はフランス語が標準
   - 音声ファイルは全言語共通で使用

2. **コマンド表示の扱い**
   - フランス語名: 常に表示（Marchez, Rompez...）
   - ローカル名: 言語に応じて変更
     - ja: マルシェ, ロンペ...
     - en: Advance, Retreat...
     - fr: Marchez, Rompez...（フランス語と同じ）

3. **RTL言語は非対応**
   - 現時点ではLTR言語のみ対応