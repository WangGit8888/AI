# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Desktop Pomodoro Timer (番茄钟) — a Windows GUI app built with Python + Tkinter. Single-file application with dark-themed UI, progress ring, system notifications, and sound alerts.

## Commands

```bash
python pomodoro.py        # launch the timer
pip install -r requirements.txt  # install dependency (win10toast)
```

No test suite or linter is configured.

## Architecture

`pomodoro.py` is the entire application (~500 lines). Key internals:

- **Config**: stored at `~/.pomodoro_config.json`, loaded/merged with `DEFAULT_CONFIG` on startup. Duration keys are in **seconds** (`work_duration`, `short_break`, `long_break`).
- **State machine**: three phases — `work` → `short_break` / `long_break` → `work`. Tracked via `self.state` dict (`phase`, `remaining`, `total`, `running`, `completed_pomodoros`, `current_cycle`, `start_time`). `long_break` triggers every `long_break_interval` work sessions.
- **Timer loop**: `_tick()` runs on `root.after(200, …)`, not a separate thread. Pause/resume recalculates `remaining` from elapsed wall-clock time (`start_time`).
- **UI**: pure Tkinter, no ttkbootstrap. Canvas-based circular progress ring (`_progress` arc with `extent`). Dark color palette defined at module top (`BG`, `CARD`, `FG`, `COLORS`). Settings window is a `Toplevel` with `Spinbox` inputs and `Checkbutton` toggles.
- **Notifications**: `win10toast` for desktop toasts (graceful degrade if absent), `winsound` for audio (plays `bell.wav` from project dir, falls back to `Beep`).
- **Always-on-top**: `root.attributes("-topmost", …)`, controlled by config toggle.

## Platform

Windows only. Relies on `win10toast` and `winsound` (both Windows-specific). The `run.bat` launcher assumes Windows `%dp0` path resolution.
