"""FastAPI application for Fencing Drill."""
import asyncio
import logging
import time
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError, field_validator, model_validator
from sse_starlette.sse import EventSourceResponse

from logic.commands import COMMAND_SETS, COMMANDS, DRILL_PAIRS
from logic.generator import PATTERNS
from logic.session import (
    BasicConfig,
    CombinationConfig,
    IntervalConfig,
    RandomConfig,
    Session,
    SessionLimitExceeded,
    SessionManager,
    SessionStatus,
    TrainingMode,
)


# Validation constants
MIN_TEMPO_BPM = 30
MAX_TEMPO_BPM = 120
MIN_REPETITIONS = 1
MAX_REPETITIONS = 50
MIN_DURATION_SECONDS = 1
MAX_DURATION_SECONDS = 600
MIN_INTERVAL_MS = 100
MAX_INTERVAL_MS = 10000
MIN_SETS = 1
MAX_SETS = 10
MIN_WORK_SECONDS = 5
MAX_WORK_SECONDS = 120
MIN_REST_SECONDS = 5
MAX_REST_SECONDS = 60


class SessionStartRequest(BaseModel):
    """Validated request for starting a session."""

    mode: str
    weapon: str = "foil"
    pair_id: str = "marche_rompe"
    repetitions: int = 10
    tempo_bpm: int = 60
    command_set: str = "beginner"
    duration_seconds: int = 60
    min_interval_ms: int = 1000
    max_interval_ms: int = 3000
    pattern_id: str = "A"
    work_seconds: int = 30
    rest_seconds: int = 15
    sets: int = 5

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        valid_modes = [m.value for m in TrainingMode]
        if v not in valid_modes:
            raise ValueError(f"Invalid mode: {v}. Must be one of {valid_modes}")
        return v

    @field_validator("weapon")
    @classmethod
    def validate_weapon(cls, v: str) -> str:
        from logic.weapons import WEAPON_PROFILES

        valid_weapons = list(WEAPON_PROFILES.keys())
        if v not in valid_weapons:
            raise ValueError(f"Invalid weapon: {v}. Must be one of {valid_weapons}")
        return v

    @field_validator("pair_id")
    @classmethod
    def validate_pair_id(cls, v: str) -> str:
        if v not in DRILL_PAIRS:
            raise ValueError(f"Invalid pair_id: {v}")
        return v

    @field_validator("command_set")
    @classmethod
    def validate_command_set(cls, v: str) -> str:
        if v not in COMMAND_SETS:
            raise ValueError(f"Invalid command_set: {v}")
        return v

    @field_validator("pattern_id")
    @classmethod
    def validate_pattern_id(cls, v: str) -> str:
        if v not in PATTERNS:
            raise ValueError(f"Invalid pattern_id: {v}")
        return v

    @field_validator("repetitions")
    @classmethod
    def validate_repetitions(cls, v: int) -> int:
        if v < MIN_REPETITIONS or v > MAX_REPETITIONS:
            raise ValueError(
                f"repetitions must be between {MIN_REPETITIONS} and {MAX_REPETITIONS}"
            )
        return v

    @field_validator("tempo_bpm")
    @classmethod
    def validate_tempo_bpm(cls, v: int) -> int:
        if v < MIN_TEMPO_BPM or v > MAX_TEMPO_BPM:
            raise ValueError(
                f"tempo_bpm must be between {MIN_TEMPO_BPM} and {MAX_TEMPO_BPM}"
            )
        return v

    @field_validator("duration_seconds")
    @classmethod
    def validate_duration_seconds(cls, v: int) -> int:
        if v < MIN_DURATION_SECONDS or v > MAX_DURATION_SECONDS:
            raise ValueError(
                f"duration_seconds must be between {MIN_DURATION_SECONDS} and {MAX_DURATION_SECONDS}"
            )
        return v

    @field_validator("min_interval_ms")
    @classmethod
    def validate_min_interval_ms(cls, v: int) -> int:
        if v < MIN_INTERVAL_MS or v > MAX_INTERVAL_MS:
            raise ValueError(
                f"min_interval_ms must be between {MIN_INTERVAL_MS} and {MAX_INTERVAL_MS}"
            )
        return v

    @field_validator("max_interval_ms")
    @classmethod
    def validate_max_interval_ms(cls, v: int) -> int:
        if v < MIN_INTERVAL_MS or v > MAX_INTERVAL_MS:
            raise ValueError(
                f"max_interval_ms must be between {MIN_INTERVAL_MS} and {MAX_INTERVAL_MS}"
            )
        return v

    @field_validator("sets")
    @classmethod
    def validate_sets(cls, v: int) -> int:
        if v < MIN_SETS or v > MAX_SETS:
            raise ValueError(f"sets must be between {MIN_SETS} and {MAX_SETS}")
        return v

    @field_validator("work_seconds")
    @classmethod
    def validate_work_seconds(cls, v: int) -> int:
        if v < MIN_WORK_SECONDS or v > MAX_WORK_SECONDS:
            raise ValueError(
                f"work_seconds must be between {MIN_WORK_SECONDS} and {MAX_WORK_SECONDS}"
            )
        return v

    @field_validator("rest_seconds")
    @classmethod
    def validate_rest_seconds(cls, v: int) -> int:
        if v < MIN_REST_SECONDS or v > MAX_REST_SECONDS:
            raise ValueError(
                f"rest_seconds must be between {MIN_REST_SECONDS} and {MAX_REST_SECONDS}"
            )
        return v

    @model_validator(mode="after")
    def validate_intervals(self) -> "SessionStartRequest":
        """Validate that min_interval <= max_interval."""
        if self.min_interval_ms > self.max_interval_ms:
            raise ValueError("min_interval_ms must be <= max_interval_ms")
        return self

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Fencing Drill application starting")

app = FastAPI(title="Fencing Drill")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)"
    )
    return response


# Setup paths
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Session manager (single instance for the app)
session_manager = SessionManager()


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.get("/googlec9f039cb609e237c.html")
async def google_verification():
    """Google Search Console verification file."""
    return HTMLResponse(
        content="google-site-verification: googlec9f039cb609e237c.html",
        media_type="text/html",
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/settings/{mode}", response_class=HTMLResponse)
async def get_settings(request: Request, mode: str):
    """Get settings panel HTML fragment for a training mode."""
    valid_modes = [m.value for m in TrainingMode]
    if mode not in valid_modes:
        raise HTTPException(status_code=404, detail=f"Invalid mode: {mode}")

    return templates.TemplateResponse(
        f"components/settings_{mode}.html", {"request": request}
    )


@app.post("/session/start", response_class=HTMLResponse)
async def start_session(
    request: Request,
    mode: Annotated[str, Form()],
    weapon: Annotated[str, Form()] = "foil",
    pair_id: Annotated[str, Form()] = "marche_rompe",
    repetitions: Annotated[int, Form()] = 10,
    tempo_bpm: Annotated[int, Form()] = 60,
    command_set: Annotated[str, Form()] = "beginner",
    duration_seconds: Annotated[int, Form()] = 60,
    min_interval_ms: Annotated[int, Form()] = 1000,
    max_interval_ms: Annotated[int, Form()] = 3000,
    pattern_id: Annotated[str, Form()] = "A",
    work_seconds: Annotated[int, Form()] = 30,
    rest_seconds: Annotated[int, Form()] = 15,
    sets: Annotated[int, Form()] = 5,
):
    """Start a training session."""
    # Validate input using Pydantic model
    try:
        validated = SessionStartRequest(
            mode=mode,
            weapon=weapon,
            pair_id=pair_id,
            repetitions=repetitions,
            tempo_bpm=tempo_bpm,
            command_set=command_set,
            duration_seconds=duration_seconds,
            min_interval_ms=min_interval_ms,
            max_interval_ms=max_interval_ms,
            pattern_id=pattern_id,
            work_seconds=work_seconds,
            rest_seconds=rest_seconds,
            sets=sets,
        )
    except ValidationError as e:
        # Convert validation errors to JSON-serializable format
        errors = []
        for error in e.errors():
            err = {
                "loc": error.get("loc", []),
                "msg": error.get("msg", str(error)),
                "type": error.get("type", "validation_error"),
            }
            errors.append(err)
        raise HTTPException(status_code=422, detail=errors)

    # Stop any existing session
    active = session_manager.get_active_session()
    if active:
        active.stop()

    # Create config based on mode
    training_mode = TrainingMode(validated.mode)

    if training_mode == TrainingMode.BASIC:
        config = BasicConfig(
            pair_id=validated.pair_id,
            repetitions=validated.repetitions,
            tempo_bpm=validated.tempo_bpm,
            weapon=validated.weapon,
        )
    elif training_mode == TrainingMode.RANDOM:
        config = RandomConfig(
            command_set=validated.command_set,
            duration_seconds=validated.duration_seconds,
            min_interval_ms=validated.min_interval_ms,
            max_interval_ms=validated.max_interval_ms,
            weapon=validated.weapon,
        )
    elif training_mode == TrainingMode.COMBINATION:
        config = CombinationConfig(
            pattern_id=validated.pattern_id,
            repetitions=validated.repetitions,
            tempo_bpm=validated.tempo_bpm,
            weapon=validated.weapon,
        )
    elif training_mode == TrainingMode.INTERVAL:
        config = IntervalConfig(
            work_seconds=validated.work_seconds,
            rest_seconds=validated.rest_seconds,
            sets=validated.sets,
            tempo_bpm=validated.tempo_bpm,
            weapon=validated.weapon,
        )
    else:
        config = BasicConfig()

    try:
        session = session_manager.create_session(mode=training_mode, config=config)
    except SessionLimitExceeded:
        return HTMLResponse(
            content="""
            <div id="session-container">
                <section class="relative bg-fencing-surface/30 rounded-2xl border border-red-500/50 overflow-hidden">
                    <div class="relative px-6 py-16 min-h-[200px] flex flex-col items-center justify-center text-center">
                        <div class="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-red-500/50 flex items-center justify-center">
                            <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                            </svg>
                        </div>
                        <p class="text-red-400 text-lg font-medium mb-2" data-i18n="error.server_busy">サーバーが混み合っています</p>
                        <p class="text-fencing-steel/70 text-sm" data-i18n="error.try_later">しばらくお待ちいただいてから再度お試しください</p>
                    </div>
                </section>
            </div>
            """,
            status_code=429,
        )

    session.start()

    # Return HTML fragment with session info
    return HTMLResponse(
        content=f"""
        <div id="session-container" data-session-id="{session.id}">
            <section class="relative bg-fencing-surface/30 rounded-2xl border border-fencing-surface-light/50 overflow-hidden">
                <div class="absolute inset-0 opacity-5">
                    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-fencing-gold blur-3xl"></div>
                </div>
                <div class="relative border-b border-fencing-surface-light/30 px-6 py-3 flex justify-between items-center">
                    <div class="flex items-center gap-3">
                        <span class="text-xs text-fencing-steel/50 uppercase tracking-wider">Session Active</span>
                        <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                    </div>
                    <div class="flex items-center gap-4 text-sm">
                        <div class="flex items-center gap-2">
                            <svg class="w-4 h-4 text-fencing-steel/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <span class="text-fencing-steel/70" id="remaining-time">--:--</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-fencing-steel/50">#</span>
                            <span class="text-fencing-steel/70" id="current-rep">0 / {getattr(config, 'repetitions', '--')}</span>
                        </div>
                    </div>
                </div>
                <div class="relative px-6 py-16 min-h-[320px] flex flex-col items-center justify-center" id="command-area">
                    <div id="active-state" class="text-center">
                        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div class="w-64 h-64 rounded-full border border-fencing-gold/20 pulse-ring"></div>
                        </div>
                        <div class="relative">
                            <p class="text-fencing-gold/60 text-sm uppercase tracking-[0.3em] mb-2" id="command-label-fr">準備中...</p>
                            <p class="font-display text-7xl md:text-8xl text-fencing-silver command-display tracking-wide" id="command-text">—</p>
                        </div>
                    </div>
                </div>
                <div class="blade-line"></div>
                <div class="relative px-6 py-6 flex justify-center gap-4">
                    <button id="btn-stop"
                            class="px-8 py-3 rounded-lg font-medium border border-fencing-surface-light text-fencing-steel hover:bg-fencing-surface-light transition-colors flex items-center gap-2"
                            hx-post="/session/stop"
                            hx-target="#session-container"
                            hx-swap="innerHTML">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 6h12v12H6z"></path>
                        </svg>
                        <span data-i18n="button.stop">停止</span>
                    </button>
                </div>
            </section>
        </div>
        <script>
            // Connect to SSE after DOM update
            setTimeout(function() {{
                startTraining("{session.id}");
            }}, 100);
        </script>
        """,
        status_code=200,
    )


@app.post("/session/stop", response_class=HTMLResponse)
async def stop_session(request: Request):
    """Stop the active training session."""
    active = session_manager.get_active_session()
    if active:
        active.stop()

    # Return idle state HTML
    return HTMLResponse(
        content="""
        <section class="relative bg-fencing-surface/30 rounded-2xl border border-fencing-surface-light/50 overflow-hidden">
            <div class="absolute inset-0 opacity-5">
                <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-fencing-gold blur-3xl"></div>
            </div>
            <div class="relative border-b border-fencing-surface-light/30 px-6 py-3 flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <span class="text-xs text-fencing-steel/50 uppercase tracking-wider">Current Mode:</span>
                    <span class="text-sm text-fencing-silver" id="current-mode-label">—</span>
                </div>
                <div class="flex items-center gap-4 text-sm">
                    <div class="flex items-center gap-2">
                        <svg class="w-4 h-4 text-fencing-steel/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span class="text-fencing-steel/70" id="remaining-time">--:--</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-fencing-steel/50">#</span>
                        <span class="text-fencing-steel/70" id="current-rep">0 / --</span>
                    </div>
                </div>
            </div>
            <div class="relative px-6 py-16 min-h-[320px] flex flex-col items-center justify-center" id="command-area">
                <div id="idle-state" class="text-center">
                    <div class="w-24 h-24 mx-auto mb-6 rounded-full border-2 border-dashed border-fencing-surface-light flex items-center justify-center">
                        <svg class="w-10 h-10 text-fencing-steel/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <p class="text-fencing-steel/50 text-sm"><span data-i18n="status.idle">設定を確認して「開始」を押してください</span></p>
                </div>
            </div>
            <div class="blade-line"></div>
            <div class="relative px-6 py-6 flex justify-center gap-4">
                <button id="btn-start"
                        type="submit"
                        form="settings-form"
                        class="btn-primary px-8 py-3 rounded-lg font-medium text-fencing-dark flex items-center gap-2">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"></path>
                    </svg>
                    <span data-i18n="button.start">開始</span>
                </button>
            </div>
        </section>
        <script>
            stopTraining();
        </script>
        """,
        status_code=200,
    )


@app.get("/session/status")
async def get_session_status(session_id: str):
    """Get the current status of a session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "status": session.status.value,
        "mode": session.mode.value,
        "progress": session.progress,
    }


@app.post("/session/pause")
async def pause_session(session_id: str):
    """Pause a running session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.pause()
    return {"status": "paused", "session_id": session.id}


@app.post("/session/resume")
async def resume_session(session_id: str):
    """Resume a paused session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.resume()
    return {"status": "running", "session_id": session.id}


@app.get("/session/stream")
async def session_stream(session_id: str):
    """SSE endpoint for real-time command streaming."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if session is already finished
    if session.status == SessionStatus.FINISHED:
        raise HTTPException(status_code=410, detail="Session has already finished")

    # Check if session is paused
    if session.status == SessionStatus.PAUSED:
        raise HTTPException(status_code=409, detail="Session is paused")

    async def event_generator():
        """Generate SSE events for the session."""
        import json
        import random

        from logic.commands import COMMAND_SETS
        from logic.generator import (
            generate_combination,
            get_post_command_delay,
            select_constrained_command,
        )
        from logic.weapons import get_weapon_profile

        config = session.config
        profile = get_weapon_profile(config.weapon)

        # Send initial en_garde
        en_garde = COMMANDS["en_garde"]
        yield {
            "event": "command",
            "data": json.dumps(en_garde.to_dict()),
        }
        await asyncio.sleep(2)  # Pause after en_garde

        if isinstance(config, BasicConfig):
            # Basic mode: alternate between paired commands
            cmd1_id, cmd2_id = DRILL_PAIRS[config.pair_id]
            cmd1 = COMMANDS[cmd1_id]
            cmd2 = COMMANDS[cmd2_id]
            # Apply weapon tempo_multiplier: sabre faster, epee slower
            interval = 60.0 / (config.tempo_bpm * profile.tempo_multiplier)

            for i in range(config.repetitions):
                if session.status != SessionStatus.RUNNING:
                    break

                rep = i + 1
                cmd = cmd1 if i % 2 == 0 else cmd2
                yield {
                    "event": "status",
                    "data": json.dumps(
                        {"rep": rep, "total": config.repetitions}
                    ),
                }
                yield {
                    "event": "command",
                    "data": json.dumps(cmd.to_dict()),
                }
                await asyncio.sleep(interval)

        elif isinstance(config, CombinationConfig):
            # Combination mode: execute preset pattern
            command_ids = generate_combination(config)
            # Apply weapon tempo_multiplier: sabre faster, epee slower
            interval = 60.0 / (config.tempo_bpm * profile.tempo_multiplier)
            total = len(command_ids)

            for i, cmd_id in enumerate(command_ids):
                if session.status != SessionStatus.RUNNING:
                    break

                rep = i + 1
                cmd = COMMANDS[cmd_id]

                yield {
                    "event": "status",
                    "data": json.dumps({"rep": rep, "total": total}),
                }
                yield {
                    "event": "command",
                    "data": json.dumps(cmd.to_dict()),
                }
                await asyncio.sleep(interval)

        elif isinstance(config, RandomConfig):
            # Random mode: phrase-based random commands with position balance
            from logic.generator import PositionTracker
            from logic.phrases import get_phrases_for_difficulty, select_balanced_phrase

            start_time = asyncio.get_event_loop().time()
            end_time = start_time + config.duration_seconds

            # Get phrases and command set for difficulty level
            phrases = get_phrases_for_difficulty(config.command_set)
            command_ids = COMMAND_SETS.get(config.command_set, ["marche", "rompe"])

            # Position tracking for balance
            tracker = PositionTracker()
            history: list[str] = []
            last_cmd: str | None = None

            while (
                asyncio.get_event_loop().time() < end_time
                and session.status == SessionStatus.RUNNING
            ):
                # Select phrase based on current position
                phrase = select_balanced_phrase(tracker.position, phrases)

                # Execute commands from phrase
                for phrase_cmd_id in phrase.commands:
                    if (
                        asyncio.get_event_loop().time() >= end_time
                        or session.status != SessionStatus.RUNNING
                    ):
                        break

                    # Apply fendez->remise rule
                    if last_cmd and last_cmd == "fendez":
                        phrase_cmd_id = "remise"

                    # Skip consecutive remise (never allow remise after remise)
                    if phrase_cmd_id == "remise" and last_cmd == "remise":
                        continue

                    # Skip commands not in difficulty's command set
                    if phrase_cmd_id not in command_ids:
                        continue

                    # Apply weapon filtering
                    cmd_obj = COMMANDS.get(phrase_cmd_id)
                    if cmd_obj and cmd_obj.is_weapon_specific:
                        if cmd_obj.weapons and config.weapon not in cmd_obj.weapons:
                            continue

                    # Check weapon weight exclusions
                    if phrase_cmd_id in profile.command_weights:
                        if profile.command_weights[phrase_cmd_id] == 0.0:
                            continue

                    cmd = COMMANDS[phrase_cmd_id]

                    # Update tracking
                    tracker.apply_command(phrase_cmd_id)
                    history.append(phrase_cmd_id)
                    if len(history) > 10:
                        history.pop(0)
                    last_cmd = phrase_cmd_id

                    remaining = int(end_time - asyncio.get_event_loop().time())
                    mins, secs = divmod(remaining, 60)

                    yield {
                        "event": "status",
                        "data": json.dumps({"remaining": f"{mins}:{secs:02d}"}),
                    }
                    yield {
                        "event": "command",
                        "data": json.dumps(cmd.to_dict()),
                    }

                    # Calculate interval with bond delay and weapon tempo
                    base_interval = random.randint(
                        config.min_interval_ms, config.max_interval_ms
                    ) / 1000.0 / profile.tempo_multiplier
                    interval = get_post_command_delay(phrase_cmd_id, base_interval)
                    await asyncio.sleep(interval)

        elif isinstance(config, IntervalConfig):
            # Interval mode: work/rest cycles with phrase-based commands
            from logic.generator import PositionTracker
            from logic.phrases import get_phrases_for_difficulty, select_balanced_phrase

            command_ids = COMMAND_SETS["intermediate"]
            phrases = get_phrases_for_difficulty("intermediate")
            # Apply weapon tempo_multiplier: sabre faster, epee slower
            work_interval = 60.0 / (config.tempo_bpm * profile.tempo_multiplier)

            for set_num in range(1, config.sets + 1):
                if session.status != SessionStatus.RUNNING:
                    break

                # Work phase with position tracking
                tracker = PositionTracker()
                history: list[str] = []
                last_cmd: str | None = None
                work_start = asyncio.get_event_loop().time()
                work_end = work_start + config.work_seconds

                while (
                    asyncio.get_event_loop().time() < work_end
                    and session.status == SessionStatus.RUNNING
                ):
                    # Select phrase based on position
                    phrase = select_balanced_phrase(tracker.position, phrases)

                    for phrase_cmd_id in phrase.commands:
                        if (
                            asyncio.get_event_loop().time() >= work_end
                            or session.status != SessionStatus.RUNNING
                        ):
                            break

                        # Apply fendez->remise rule
                        if last_cmd and last_cmd == "fendez":
                            phrase_cmd_id = "remise"

                        # Skip consecutive remise (never allow remise after remise)
                        if phrase_cmd_id == "remise" and last_cmd == "remise":
                            continue

                        # Skip if not in intermediate command set
                        if phrase_cmd_id not in command_ids:
                            continue

                        # Apply weapon filtering
                        cmd_obj = COMMANDS.get(phrase_cmd_id)
                        if cmd_obj and cmd_obj.is_weapon_specific:
                            if cmd_obj.weapons and config.weapon not in cmd_obj.weapons:
                                continue

                        if phrase_cmd_id in profile.command_weights:
                            if profile.command_weights[phrase_cmd_id] == 0.0:
                                continue

                        cmd = COMMANDS[phrase_cmd_id]

                        # Update tracking
                        tracker.apply_command(phrase_cmd_id)
                        history.append(phrase_cmd_id)
                        if len(history) > 10:
                            history.pop(0)
                        last_cmd = phrase_cmd_id

                        remaining = int(work_end - asyncio.get_event_loop().time())

                        yield {
                            "event": "status",
                            "data": json.dumps({
                                "set": set_num,
                                "total_sets": config.sets,
                                "phase": "work",
                                "remaining": f"0:{remaining:02d}",
                            }),
                        }
                        yield {
                            "event": "command",
                            "data": json.dumps(cmd.to_dict()),
                        }

                        interval = get_post_command_delay(phrase_cmd_id, work_interval)
                        await asyncio.sleep(interval)

                # Rest phase (except after last set)
                if set_num < config.sets and session.status == SessionStatus.RUNNING:
                    # Send rest command
                    yield {
                        "event": "status",
                        "data": json.dumps({
                            "set": set_num,
                            "total_sets": config.sets,
                            "phase": "rest",
                            "remaining": f"0:{config.rest_seconds:02d}",
                        }),
                    }
                    yield {
                        "event": "command",
                        "data": json.dumps({
                            "id": "rest",
                            "fr": "Repos",
                            "jp": "休憩",
                            "audio": "/static/audio/repos.mp3",
                        }),
                    }

                    # Countdown during rest
                    for remaining in range(config.rest_seconds, 0, -1):
                        if session.status != SessionStatus.RUNNING:
                            break
                        yield {
                            "event": "status",
                            "data": json.dumps({
                                "set": set_num,
                                "total_sets": config.sets,
                                "phase": "rest",
                                "remaining": f"0:{remaining:02d}",
                            }),
                        }
                        await asyncio.sleep(1)

        # Send halte command before end event
        halte = COMMANDS["halte"]
        yield {
            "event": "command",
            "data": json.dumps(halte.to_dict()),
        }
        await asyncio.sleep(1)  # Brief pause after halte

        # Send end event
        yield {"event": "end", "data": json.dumps({"message": "終了"})}
        session.stop()

    return EventSourceResponse(event_generator())
