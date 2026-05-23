"""
Desktop Pomodoro Timer - 桌面番茄钟
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import json
import os
from pathlib import Path
from datetime import datetime

try:
    from win10toast import ToastNotifier
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

APP_NAME = "番茄钟"
CONFIG_FILE = Path.home() / ".pomodoro_config.json"
SOUND_FILE = Path(__file__).parent / "bell.wav"

# ---- color palette ----
BG = "#0f0f1a"          # 主背景
CARD = "#1a1a2e"        # 卡片背景
CARD_HOVER = "#222240"
FG = "#f0f0f0"          # 主文字
FG2 = "#8888a0"         # 次要文字
COLORS = {
    "work":        {"bg": "#e74c3c", "fg": "#fff", "label": "专注", "icon": "●"},
    "short_break": {"bg": "#2ecc71", "fg": "#fff", "label": "短休息", "icon": "●"},
    "long_break":  {"bg": "#3498db", "fg": "#fff", "label": "长休息", "icon": "●"},
}

DEFAULT_CONFIG = {
    "work_duration": 25 * 60,
    "short_break": 5 * 60,
    "long_break": 15 * 60,
    "long_break_interval": 4,
    "always_on_top": True,
    "sound_enabled": True,
    "notification_enabled": True,
}

PHASE_CONFIG_KEY = {
    "work": "work_duration",
    "short_break": "short_break",
    "long_break": "long_break",
}


class PomodoroTimer:

    def __init__(self):
        self.config = self._load_config()
        self._init_state()
        self._update_lock = threading.Lock()
        self._notifier = ToastNotifier() if HAS_TOAST else None

        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("420x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        if self.config.get("always_on_top", True):
            self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 去掉原生标题栏风格（可选）
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self._setup_ui()
        self._update_display()
        self.root.mainloop()

    # ================================================================
    # State
    # ================================================================
    def _init_state(self):
        self.state = {
            "phase": "work",
            "remaining": self.config["work_duration"],
            "total": self.config["work_duration"],
            "running": False,
            "completed_pomodoros": 0,
            "current_cycle": 0,
            "start_time": None,
        }

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                merged = dict(DEFAULT_CONFIG)
                merged.update(data)
                return merged
            except Exception:
                return dict(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    def _save_config(self):
        try:
            CONFIG_FILE.write_text(
                json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    # ================================================================
    # UI
    # ================================================================
    def _setup_ui(self):
        self.root.columnconfigure(0, weight=1)

        # ---------- 顶部：阶段标签 ----------
        top = tk.Frame(self.root, bg=BG)
        top.grid(row=0, column=0, pady=(25, 0))

        self.phase_badge = tk.Label(
            top, text="●  专注", font=("Segoe UI", 13, "bold"),
            fg="#fff", bg=COLORS["work"]["bg"], padx=14, pady=4)
        self.phase_badge.pack()

        # ---------- 进度环 ----------
        self.canvas = tk.Canvas(self.root, width=300, height=300,
                                bg=BG, highlightthickness=0)
        self.canvas.grid(row=1, column=0, pady=(15, 0))

        cx, cy, r = 150, 150, 130

        # 外圈底环（细）
        self._arc_bg = self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#222240", width=10)

        # 进度弧
        self._progress = self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90, extent=0, outline=COLORS["work"]["bg"],
            width=10, style="arc")

        # 内圈装饰（极淡）
        self._arc_inner = self.canvas.create_oval(
            cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18,
            outline="#181830", width=1)

        # 时间数字
        self._time_text = self.canvas.create_text(
            cx, cy - 10, text="25:00",
            font=("Segoe UI", 48, "bold"), fill=FG)

        # 子状态文字
        self._sub_text = self.canvas.create_text(
            cx, cy + 38, text="准备好了",
            font=("Segoe UI", 12), fill=FG2)

        # ---------- 控制按钮 ----------
        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.grid(row=2, column=0, pady=(10, 0))

        self.btn_start = self._make_button(ctrl, "开  始", COLORS["work"]["bg"], self._toggle_start)
        self.btn_start.pack(side="left", padx=4)

        self.btn_pause = self._make_button(ctrl, "暂  停", "#888", self._toggle_pause)
        self.btn_pause.pack(side="left", padx=4)
        self.btn_pause.config(state="disabled")

        self.btn_reset = self._make_button(ctrl, "重  置", "#555", self._reset)
        self.btn_reset.pack(side="left", padx=4)

        # ---------- 统计 ----------
        stats = tk.Frame(self.root, bg=BG)
        stats.grid(row=3, column=0, pady=(15, 0))

        sep = tk.Frame(stats, height=1, bg="#222240")
        sep.pack(fill="x", padx=40, pady=(0, 10))

        row1 = tk.Frame(stats, bg=BG)
        row1.pack()
        self._pomo_label = tk.Label(
            row1, text="0", font=("Segoe UI", 24, "bold"),
            fg=COLORS["work"]["bg"], bg=BG)
        self._pomo_label.pack(side="left")
        tk.Label(row1, text="  番茄完成", font=("Segoe UI", 11),
                 fg=FG2, bg=BG).pack(side="left")

        # ---------- 底部按钮 ----------
        bottom = tk.Frame(self.root, bg=BG)
        bottom.grid(row=4, column=0, pady=(12, 0))

        self._settings_btn = tk.Label(
            bottom, text="⚙ 设置", font=("Segoe UI", 10),
            fg=FG2, bg=BG, cursor="hand2")
        self._settings_btn.pack(side="left", padx=8)
        self._settings_btn.bind("<Button-1>", lambda e: self._open_settings())
        self._settings_btn.bind("<Enter>", lambda e: self._settings_btn.config(fg=FG))
        self._settings_btn.bind("<Leave>", lambda e: self._settings_btn.config(fg=FG2))

    def _make_button(self, parent, text, color, cmd):
        """创建统一样式的按钮"""
        btn = tk.Label(
            parent, text=text, font=("Segoe UI", 12, "bold"),
            fg="#fff", bg=color, padx=22, pady=8, cursor="hand2")
        btn.pack  # just reference
        # inner frame approach for rounded look
        outer = tk.Frame(parent, bg=color, highlightbackground=color,
                         highlightthickness=1, bd=0)
        outer.pack(side="left", padx=4)

        # We wrap a label inside for the click/text
        lbl = tk.Label(outer, text=text, font=("Segoe UI", 12, "bold"),
                       fg="#fff", bg=color, padx=22, pady=8, cursor="hand2")
        lbl.pack()
        lbl.bind("<Button-1>", lambda e: cmd())
        lbl.bind("<Enter>", lambda e: lbl.config(bg=self._lighten(color, 0.15)))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=color))
        # outer stays color so it frames it
        return lbl

    @staticmethod
    def _lighten(hex_color, factor=0.15):
        """简单提亮颜色"""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _button_enable(self, btn, color):
        btn.config(fg="#fff", bg=color)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._lighten(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))

    def _button_disable(self, btn):
        btn.config(fg="#666", bg="#2a2a3a")

    # ================================================================
    # Timer logic
    # ================================================================
    def _toggle_start(self):
        if self.state["running"]:
            return
        self.state["running"] = True
        self.state["start_time"] = time.time() - (
            self.state["total"] - self.state["remaining"])
        self._button_disable(self.btn_start)
        self._button_enable(self.btn_pause, "#888")
        self.btn_pause.config(text="暂  停")
        self._tick()
        self._save_config()

    def _toggle_pause(self):
        phase_colors = COLORS[self.state["phase"]]
        if self.state["running"]:
            self.state["running"] = False
            if self.state["start_time"]:
                elapsed = time.time() - self.state["start_time"]
                self.state["remaining"] = max(0, self.state["total"] - int(elapsed))
            self.btn_pause.config(text="继  续")
            self._button_enable(self.btn_pause, "#f39c12")
            self._button_enable(self.btn_start, phase_colors["bg"])
        else:
            self.state["running"] = True
            self.state["start_time"] = time.time() - (
                self.state["total"] - self.state["remaining"])
            self.btn_pause.config(text="暂  停")
            self._button_enable(self.btn_pause, "#888")
            self._button_disable(self.btn_start)
            self._tick()
        self._update_display()

    def _reset(self):
        self.state["running"] = False
        self.state["phase"] = "work"
        self.state["remaining"] = self.config["work_duration"]
        self.state["total"] = self.config["work_duration"]
        self.state["start_time"] = None
        self.state["current_cycle"] = 0
        self.btn_pause.config(text="暂  停")
        self._button_disable(self.btn_pause)
        self._button_enable(self.btn_start, COLORS["work"]["bg"])
        self._update_display()

    def _tick(self):
        if not self.state["running"]:
            return
        now = time.time()
        elapsed = now - self.state["start_time"]
        remaining = self.state["total"] - int(elapsed)

        if remaining <= 0:
            self._on_phase_complete()
            return

        with self._update_lock:
            self.state["remaining"] = remaining
        self._update_display()
        self.root.after(200, self._tick)

    def _on_phase_complete(self):
        self.state["running"] = False
        self.state["remaining"] = 0
        self._update_display()

        phase = self.state["phase"]
        cp = COLORS[phase]
        self._notify(f"{cp['label']}结束！")
        if HAS_SOUND and self.config.get("sound_enabled", True):
            self._play_sound()

        if phase == "work":
            self.state["completed_pomodoros"] += 1
            self.state["current_cycle"] += 1
            if self.state["current_cycle"] >= self.config["long_break_interval"]:
                self.state["current_cycle"] = 0
                self._switch_phase("long_break")
            else:
                self._switch_phase("short_break")
        else:
            self._switch_phase("work")

        self.btn_pause.config(text="暂  停")
        self._button_disable(self.btn_pause)
        self._button_enable(self.btn_start, COLORS[self.state["phase"]]["bg"])
        self._save_config()

    def _switch_phase(self, new_phase):
        self.state["phase"] = new_phase
        cfg_key = PHASE_CONFIG_KEY[new_phase]
        self.state["total"] = self.config[cfg_key]
        self.state["remaining"] = self.state["total"]
        self.state["start_time"] = None
        self._update_display()

    # ================================================================
    # Display
    # ================================================================
    def _update_display(self):
        phase = self.state["phase"]
        cp = COLORS[phase]
        remaining = self.state["remaining"]
        running = self.state["running"]
        total = self.state["total"]

        # ---- 阶段徽章 ----
        self.phase_badge.config(text=f"{cp['icon']}  {cp['label']}", bg=cp["bg"])

        # ---- 时间数字 ----
        mm, ss = divmod(max(0, remaining), 60)
        self.canvas.itemconfig(self._time_text, text=f"{mm:02d}:{ss:02d}")

        # ---- 子状态 ----
        status = ""
        if running:
            if phase == "work":
                status = f"第 {self.state['current_cycle'] + 1}/{self.config['long_break_interval']} 轮 · 专注中"
            else:
                status = "休息中"
        elif remaining > 0 and remaining < total:
            status = "已暂停"
        elif remaining <= 0:
            status = "时间到"
        else:
            status = "准备好了" if phase == "work" else "休息时间"
        self.canvas.itemconfig(self._sub_text, text=status)

        # ---- 进度弧 ----
        extent = 0
        if total > 0:
            extent = -360 * (1 - remaining / total)
        self.canvas.itemconfig(self._progress, extent=extent, outline=cp["bg"])

        # ---- 统计 ----
        self._pomo_label.config(text=str(self.state["completed_pomodoros"]))

    # ================================================================
    # Notifications
    # ================================================================
    def _notify(self, message):
        if self.config.get("notification_enabled", True) and self._notifier:
            threading.Thread(
                target=lambda: self._notifier.show_toast(APP_NAME, message, duration=5, threaded=True),
                daemon=True).start()

    def _play_sound(self):
        if SOUND_FILE.exists():
            winsound.PlaySound(str(SOUND_FILE), winsound.SND_ASYNC)
        else:
            winsound.Beep(880, 500)

    # ================================================================
    # Settings
    # ================================================================
    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("设置")
        win.geometry("360x350")
        win.resizable(False, False)
        win.configure(bg=CARD)
        win.transient(self.root)
        win.grab_set()

        # 标题
        tk.Label(win, text="番茄钟设置", font=("Segoe UI", 14, "bold"),
                 fg=FG, bg=CARD).pack(pady=(16, 12))

        fields = [
            ("work_duration",     "专注时长 (分)",  1, 120),
            ("short_break",       "短休息 (分)",    1, 60),
            ("long_break",        "长休息 (分)",    1, 60),
            ("long_break_interval", "长休息间隔 (轮)", 1, 10),
        ]
        rows = tk.Frame(win, bg=CARD)
        rows.pack(padx=30, fill="x")

        for i, (key, label, lo, hi) in enumerate(fields):
            f = tk.Frame(rows, bg=CARD)
            f.pack(fill="x", pady=4)
            f.columnconfigure(1, weight=1)

            tk.Label(f, text=label, font=("Segoe UI", 10),
                     fg=FG, bg=CARD).pack(side="left")

            val = self.config[key]
            if "duration" in key:
                val = val // 60
            v = tk.IntVar(value=val)

            sb = ttk.Spinbox(
                f, from_=lo, to=hi, textvariable=v, width=5,
                font=("Segoe UI", 10))
            sb.pack(side="right")
            sb.bind("<FocusOut>", lambda e, k=key, vv=v: self._setting_changed(k, vv.get()))
            sb.bind("<Key-Return>", lambda e, k=key, vv=v: self._setting_changed(k, vv.get()))

        # 分隔
        ttk.Separator(win).pack(fill="x", padx=30, pady=(10, 6))

        # 选项
        opts = tk.Frame(win, bg=CARD)
        opts.pack(padx=30, fill="x")

        for key, label in [("always_on_top", "窗口置顶"),
                           ("sound_enabled", "声音提示"),
                           ("notification_enabled", "桌面通知")]:
            v = tk.BooleanVar(value=self.config.get(key, True))
            cb = tk.Checkbutton(opts, text=label, variable=v,
                                font=("Segoe UI", 10), fg=FG, bg=CARD,
                                selectcolor=CARD, activebackground=CARD,
                                command=lambda k=key, vv=v: self._toggle_option(k, vv))
            cb.pack(anchor="w", pady=1)

        # 关闭
        tk.Label(win, text="关闭", font=("Segoe UI", 10),
                 fg=FG2, bg=CARD, cursor="hand2").pack(pady=(8, 12))
        # hook close on click
        for child in win.winfo_children():
            if isinstance(child, tk.Label) and child.cget("text") == "关闭":
                child.bind("<Button-1>", lambda e: win.destroy())
                child.bind("<Enter>", lambda e: child.config(fg=FG))
                child.bind("<Leave>", lambda e: child.config(fg=FG2))

    def _setting_changed(self, key, val):
        try:
            v = int(val)
        except (ValueError, TypeError):
            return
        clamped = max(1, v)
        if "duration" in key:
            clamped = max(60, clamped * 60)
        self.config[key] = clamped
        self._save_config()
        if not self.state["running"]:
            cfg_key = PHASE_CONFIG_KEY[self.state["phase"]]
            self.state["total"] = self.config[cfg_key]
            self.state["remaining"] = self.state["total"]
            self._update_display()

    def _toggle_option(self, key, var):
        self.config[key] = var.get()
        if key == "always_on_top":
            self.root.attributes("-topmost", var.get())
        self._save_config()

    # ================================================================
    # Close
    # ================================================================
    def _on_close(self):
        if self.state["running"]:
            if not messagebox.askokcancel("退出", "计时器正在运行，确定退出吗？"):
                return
        self._save_config()
        self.root.destroy()


if __name__ == "__main__":
    PomodoroTimer()
