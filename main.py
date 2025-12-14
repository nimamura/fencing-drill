"""FastAPI application for Fencing Drill."""
import asyncio
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

from logic.commands import COMMANDS
from logic.session import (
    BasicConfig,
    CombinationConfig,
    IntervalConfig,
    RandomConfig,
    Session,
    SessionManager,
    SessionStatus,
    TrainingMode,
)

app = FastAPI(title="Fencing Drill")

# Setup paths
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Session manager (single instance for the app)
session_manager = SessionManager()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/settings/{mode}", response_class=HTMLResponse)
async def get_settings(request: Request, mode: str):
    """Get settings panel HTML fragment for a training mode."""
    valid_modes = ["basic", "combination", "random", "interval"]
    if mode not in valid_modes:
        raise HTTPException(status_code=404, detail=f"Invalid mode: {mode}")

    return templates.TemplateResponse(
        f"components/settings_{mode}.html", {"request": request}
    )


@app.post("/session/start", response_class=HTMLResponse)
async def start_session(
    request: Request,
    mode: Annotated[str, Form()],
    command_id: Annotated[str, Form()] = "marche",
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
    # Stop any existing session
    active = session_manager.get_active_session()
    if active:
        active.stop()

    # Create config based on mode
    training_mode = TrainingMode(mode)

    if training_mode == TrainingMode.BASIC:
        config = BasicConfig(
            command_id=command_id, repetitions=repetitions, tempo_bpm=tempo_bpm
        )
    elif training_mode == TrainingMode.RANDOM:
        config = RandomConfig(
            command_set=command_set,
            duration_seconds=duration_seconds,
            min_interval_ms=min_interval_ms,
            max_interval_ms=max_interval_ms,
        )
    elif training_mode == TrainingMode.COMBINATION:
        config = CombinationConfig(
            pattern_id=pattern_id, repetitions=repetitions, tempo_bpm=tempo_bpm
        )
    elif training_mode == TrainingMode.INTERVAL:
        config = IntervalConfig(
            work_seconds=work_seconds,
            rest_seconds=rest_seconds,
            sets=sets,
            tempo_bpm=tempo_bpm,
        )
    else:
        config = BasicConfig()

    session = session_manager.create_session(mode=training_mode, config=config)
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
                        停止
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
                    <p class="text-fencing-steel/50 text-sm">設定を確認して「開始」を押してください</p>
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
                    開始
                </button>
            </div>
        </section>
        <script>
            stopTraining();
        </script>
        """,
        status_code=200,
    )


@app.get("/session/stream")
async def session_stream(session_id: str):
    """SSE endpoint for real-time command streaming."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        """Generate SSE events for the session."""
        import json
        import random

        config = session.config
        rep = 0

        # Send initial en_garde
        en_garde = COMMANDS["en_garde"]
        yield {
            "event": "command",
            "data": json.dumps(en_garde.to_dict()),
        }
        await asyncio.sleep(2)  # Pause after en_garde

        if isinstance(config, BasicConfig):
            # Basic mode: repeat single command
            cmd = COMMANDS.get(config.command_id, COMMANDS["marche"])
            interval = 60.0 / config.tempo_bpm

            for i in range(config.repetitions):
                if session.status != SessionStatus.RUNNING:
                    break

                rep = i + 1
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

        elif isinstance(config, RandomConfig):
            # Random mode: random commands from set
            from logic.commands import COMMAND_SETS

            command_ids = COMMAND_SETS.get(config.command_set, ["marche", "rompe"])
            start_time = asyncio.get_event_loop().time()
            end_time = start_time + config.duration_seconds

            while (
                asyncio.get_event_loop().time() < end_time
                and session.status == SessionStatus.RUNNING
            ):
                cmd_id = random.choice(command_ids)
                cmd = COMMANDS[cmd_id]

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

                interval = random.randint(
                    config.min_interval_ms, config.max_interval_ms
                ) / 1000.0
                await asyncio.sleep(interval)

        # Send end event
        yield {"event": "end", "data": json.dumps({"message": "終了"})}
        session.stop()

    return EventSourceResponse(event_generator())
