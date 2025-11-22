"""
typesmart.gui.main_window
Improved, modular Tkinter GUI based on your original script.
Depends on:
  - typesmart.core.storage.load_progress / save_progress
  - typesmart.core.config.THEMES
  - typesmart.core.levels.LEVELS
  - typesmart.core.utils.normalize, progress_bar, update_heatmap
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import random
from datetime import datetime

from typesmart.core import storage, config, levels, utils

# Load persisted progress
progress = storage.load_progress()

# Theme object (mutable; updated when user changes theme)
THEME = config.THEMES.get(progress.get("theme", "neon"), config.THEMES["neon"])


class TypingTrainerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TypeSmart — Ultra-Light Typing Trainer")
        self.geometry("880x460")
        self.configure(bg=THEME["bg"])

        # Data / state
        self.level_number = progress.get("level", 1)
        self.level_sets = levels.LEVELS.get(self.level_number, [])
        self.set_idx = progress.get("current_set", 0)
        self.current_target = ""
        self.start_time = None

        # Build UI
        self._build_styles()
        self.create_widgets()
        self.load_set()

    # --------------------------
    # UI Construction & Styling
    # --------------------------
    def _build_styles(self):
        # Configure ttk styles to follow theme where practical
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", padding=6)
        style.configure("TLabel", background=THEME["bg"], foreground=THEME["fg"])

    def create_widgets(self):
        # Top: target text container (scrollable label)
        self.target_frame = tk.Frame(self, bg=THEME["bg"])
        self.target_frame.pack(fill="x", padx=12, pady=(12, 6))

        self.target_label = tk.Label(
            self.target_frame,
            text="",
            font=("Consolas", 16),
            bg=THEME["bg"],
            fg=THEME["accent"],
            wraplength=840,
            justify="left",
        )
        self.target_label.pack(anchor="w")

        # Input
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            self,
            textvariable=self.input_var,
            font=("Consolas", 16),
            width=90,
            relief="solid",
            bd=1,
        )
        self.input_entry.pack(padx=12, pady=(6, 8))
        self.input_entry.bind("<KeyRelease>", self.on_type)
        self.input_entry.focus_set()

        # Stats and progress row
        stats_frame = tk.Frame(self, bg=THEME["bg"])
        stats_frame.pack(fill="x", padx=12)

        self.stats_label = tk.Label(
            stats_frame, text="", font=("Consolas", 11), bg=THEME["bg"], fg=THEME["fg"]
        )
        self.stats_label.pack(side="left", anchor="w")

        self.progress_label = tk.Label(
            stats_frame, text="", font=("Consolas", 11), bg=THEME["bg"], fg=THEME["fg"]
        )
        self.progress_label.pack(side="right", anchor="e")

        # Controls
        ctrl_frame = tk.Frame(self, bg=THEME["bg"])
        ctrl_frame.pack(pady=10)

        btn_cfg = {"bg": THEME["accent"], "fg": THEME["fg"], "activebackground": THEME["good"], "bd": 0, "padx": 8, "pady": 4}
        # Using tk.Button for wide compatibility across Termux environments
        tk.Button(ctrl_frame, text="Next Set", command=self.next_set, **btn_cfg).grid(row=0, column=0, padx=6)
        tk.Button(ctrl_frame, text="Daily Practice", command=self.daily_practice, **btn_cfg).grid(row=0, column=1, padx=6)
        tk.Button(ctrl_frame, text="Custom Lesson", command=self.add_custom_lesson, **btn_cfg).grid(row=0, column=2, padx=6)
        tk.Button(ctrl_frame, text="1-min Test", command=lambda: self.typing_test(1), **btn_cfg).grid(row=0, column=3, padx=6)
        tk.Button(ctrl_frame, text="5-min Test", command=lambda: self.typing_test(5), **btn_cfg).grid(row=0, column=4, padx=6)
        tk.Button(ctrl_frame, text="Show Stats", command=self.show_stats, **btn_cfg).grid(row=0, column=5, padx=6)
        tk.Button(ctrl_frame, text="Change Theme", command=self.change_theme, **btn_cfg).grid(row=0, column=6, padx=6)

    # --------------------------
    # Loading / Progress Logic
    # --------------------------
    def load_set(self):
        # Ensure level_sets is not empty
        if not self.level_sets:
            self.level_sets = levels.LEVELS.get(self.level_number, ["(no content)"])

        # If completed level
        if self.set_idx >= len(self.level_sets):
            messagebox.showinfo("Level Complete", f"🎉 Level {self.level_number} completed!")
            if self.level_number < max(levels.LEVELS.keys()):
                self.level_number += 1
                self.level_sets = levels.LEVELS.get(self.level_number, [])
                self.set_idx = 0
            else:
                self.set_idx = 0

        self.current_target = self.level_sets[self.set_idx]
        self.target_label.config(text=self.current_target)
        self.input_var.set("")
        self.start_time = time.time()
        self.update_stats_labels()

    # --------------------------
    # Typing handler
    # --------------------------
    def on_type(self, event=None):
        typed = self.input_var.get()
        # Update heatmap for typed characters
        for i, c in enumerate(typed):
            correct = i < len(self.current_target) and c == self.current_target[i]
            utils.update_heatmap(c, correct, progress)

        # Stats calculation (safe arithmetic)
        elapsed = max(0.001, time.time() - (self.start_time or time.time()))
        words_typed = len(typed.split())
        wpm = (words_typed / elapsed) * 60 if elapsed > 0 else 0.0

        correct_chars = sum(
            1 for i in range(min(len(typed), len(self.current_target))) if typed[i] == self.current_target[i]
        )
        acc = (correct_chars / len(typed) * 100) if typed else 100.0

        self.stats_label.config(text=f"WPM: {wpm:.1f} | Accuracy: {acc:.1f}%")
        # Progress bar uses number of completed sets vs total sets
        total_sets = max(1, len(self.level_sets))
        self.progress_label.config(text=f"{utils.progress_bar(self.set_idx, total_sets)} {self.set_idx}/{total_sets}")

        # Auto-complete detection (normalize whitespace)
        if utils.normalize(typed) == utils.normalize(self.current_target):
            # Update stored statistics safely
            progress["total_words"] = progress.get("total_words", 0) + len(self.current_target.split())
            progress["total_time"] = progress.get("total_time", 0.0) + elapsed
            progress["current_set"] = self.set_idx + 1
            storage.save_progress(progress)  # persist progress
            self.set_idx += 1
            # slight delay to allow final key to appear before loading next
            self.after(80, self.load_set)

    # --------------------------
    # Controls
    # --------------------------
    def next_set(self):
        self.set_idx += 1
        self.load_set()

    def daily_practice(self):
        today = datetime.today().strftime("%Y-%m-%d")
        if progress.get("last_practice") != today:
            progress["streak"] = progress.get("streak", 0) + 1
            progress["last_practice"] = today
            storage.save_progress(progress)
        messagebox.showinfo("Daily Practice", f"Daily practice started! Streak: {progress.get('streak',0)} days")
        self.load_set()

    def add_custom_lesson(self):
        text = simpledialog.askstring("Custom Lesson", "Enter text for custom lesson:")
        if text:
            progress.setdefault("custom_lessons", []).append(text)
            storage.save_progress(progress)
            messagebox.showinfo("Custom Lesson", "Lesson added!")

    def typing_test(self, minutes):
        # Non-blocking test dialog collection using repeated prompts in a loop
        end_time = time.time() + minutes * 60
        total_typed = []
        while time.time() < end_time:
            sample = random.choice(levels.EXPERT_LEVEL)
            typed = simpledialog.askstring("Typing Test", sample)
            if typed is None:
                # user cancelled test
                break
            total_typed.append(typed)
        words = sum(len(t.split()) for t in total_typed)
        wpm = (words / minutes) if minutes > 0 else 0.0
        messagebox.showinfo(f"{minutes}-Minute Typing Test", f"Test Complete! WPM: {wpm:.1f}")

    def show_stats(self):
        total_time = progress.get("total_time", 0.0) or 1.0
        total_words = progress.get("total_words", 0)
        avg_wpm = (total_words / (total_time / 60.0)) if total_words else 0.0
        heatmap_text = "\n".join(f"{k}: {v['correct']}/{v['correct']+v['wrong']} correct" for k, v in progress.get("heatmap", {}).items())
        stats = (
            f"Level: {self.level_number}\n"
            f"Total Words: {total_words}\n"
            f"Errors: {progress.get('total_errors',0)}\n"
            f"Avg WPM: {avg_wpm:.1f}\n"
            f"Streak: {progress.get('streak',0)} days\n\n"
            f"Heatmap:\n{heatmap_text}"
        )
        messagebox.showinfo("Stats", stats)

    def change_theme(self):
        choice = simpledialog.askstring("Change Theme", f"Available: {', '.join(config.THEMES.keys())}")
        if not choice:
            return
        if choice in config.THEMES:
            progress["theme"] = choice
            storage.save_progress(progress)
            # update local THEME and reapply
            global THEME
            THEME = config.THEMES[choice]
            self._reapply_theme()
            messagebox.showinfo("Theme", f"Theme changed to {choice}")
        else:
            messagebox.showerror("Theme", "Invalid theme")

    def _reapply_theme(self):
        # reconfigure backgrounds/foregrounds for major widgets
        self.configure(bg=THEME["bg"])
        widgets = [self.target_frame, self.target_label, self.stats_label, self.progress_label, self.input_entry]
        for w in widgets:
            try:
                w.config(bg=THEME.get("bg", "#000000"), fg=THEME.get("fg", "#ffffff"))
            except Exception:
                # some widgets (Entry) may not accept fg/bg changes in same way
                try:
                    w.config(bg=THEME.get("bg", "#000000"))
                except Exception:
                    pass

        # update control buttons
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                for btn in child.winfo_children():
                    if isinstance(btn, tk.Button):
                        try:
                            btn.config(bg=THEME["accent"], fg=THEME["fg"])
                        except Exception:
                            pass

# If run as module
def run_app():
    app = TypingTrainerGUI()
    app.mainloop()

if __name__ == "__main__":
    run_app()
