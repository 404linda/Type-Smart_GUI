#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os, time, random
from datetime import datetime

# ======================================================
# FILE & PROGRESS MANAGEMENT
# ======================================================
PROGRESS_FILE = os.path.expanduser("~/.typing_progress_gui_v10.json")

if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {
        "theme": "neon",
        "level": 1,
        "current_set": 0,
        "total_words": 0,
        "total_errors": 0,
        "total_time": 0.0,
        "heatmap": {},
        "streak": 0,
        "last_practice": "",
        "custom_lessons": []
    }

def save_progress():
    tmp = PROGRESS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(progress, f)
    os.replace(tmp, PROGRESS_FILE)

# ======================================================
# THEMES
# ======================================================
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#000000", "accent": "#007acc", "good": "#28a745", "bad": "#dc3545"},
    "dark": {"bg": "#222222", "fg": "#ffffff", "accent": "#00bfff", "good": "#28a745", "bad": "#dc3545"},
    "neon": {"bg": "#1a1a1a", "fg": "#00ffff", "accent": "#ff00ff", "good": "#28a745", "bad": "#ff0066"}
}
THEME = THEMES.get(progress["theme"], THEMES["neon"])

# ======================================================
# LEVEL DATA
# ======================================================
BEGINNER_LEVEL = [
    "asdf jkl qwe rty",
    "zxcv bn m po iu",
    "qaz wsx edc rfv",
] + [f"wordset {i}" for i in range(10)]

INTERMEDIATE_LEVEL = [
    "The quick brown fox jumps over the lazy dog.",
    "Typing improves focus and muscle memory.",
] + [f"Intermediate sentence {i}" for i in range(10)]

EXPERT_LEVEL = [
    "Expert typing requires endurance, precision, and mental stamina.",
    "Long-form typing helps develop high sustained WPM.",
] + [f"Expert paragraph {i}" for i in range(10)]

LEVELS = {1: BEGINNER_LEVEL, 2: INTERMEDIATE_LEVEL, 3: EXPERT_LEVEL}

# ======================================================
# UTILITY FUNCTIONS
# ======================================================
def normalize(s):
    return " ".join(s.strip().split())

def update_heatmap(key, correct):
    hm = progress["heatmap"]
    if key not in hm:
        hm[key] = {"correct":0,"wrong":0}
    if correct:
        hm[key]["correct"] += 1
    else:
        hm[key]["wrong"] +=1
    save_progress()

def progress_bar(current, total, width=20):
    filled = int((current/total)*width)
    return "[" + "#"*filled + "-"*(width-filled) + "]"

# ======================================================
# GUI APP
# ======================================================
class TypingTrainerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultra-Light Typing Trainer v10")
        self.geometry("800x400")
        self.configure(bg=THEME["bg"])

        self.level_number = progress["level"]
        self.level_sets = LEVELS[self.level_number]
        self.set_idx = progress["current_set"]
        self.current_target = ""
        self.start_time = None

        self.create_widgets()
        self.load_set()

    def create_widgets(self):
        # Target text
        self.target_label = tk.Label(self, text="", font=("Consolas",16), bg=THEME["bg"], fg=THEME["accent"], wraplength=760, justify="left")
        self.target_label.pack(pady=10)

        # Typing input
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(self, textvariable=self.input_var, font=("Consolas",16), width=80)
        self.input_entry.pack(pady=5)
        self.input_entry.bind("<KeyRelease>", self.on_type)
        self.input_entry.focus()

        # Stats labels
        self.stats_label = tk.Label(self, text="", font=("Consolas",12), bg=THEME["bg"], fg=THEME["fg"])
        self.stats_label.pack(pady=5)

        # Progress bar
        self.progress_label = tk.Label(self, text="", font=("Consolas",12), bg=THEME["bg"], fg=THEME["fg"])
        self.progress_label.pack(pady=5)

        # Controls
        frame = tk.Frame(self, bg=THEME["bg"])
        frame.pack(pady=10)

        tk.Button(frame, text="Next Set", command=self.next_set, bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=0,padx=5)
        tk.Button(frame, text="Daily Practice", command=self.daily_practice, bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=1,padx=5)
        tk.Button(frame, text="Custom Lesson", command=self.add_custom_lesson, bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=2,padx=5)
        tk.Button(frame, text="Typing Test 1min", command=lambda:self.typing_test(1), bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=3,padx=5)
        tk.Button(frame, text="Typing Test 5min", command=lambda:self.typing_test(5), bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=4,padx=5)
        tk.Button(frame, text="Show Stats", command=self.show_stats, bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=5,padx=5)
        tk.Button(frame, text="Change Theme", command=self.change_theme, bg=THEME["accent"], fg=THEME["fg"]).grid(row=0,column=6,padx=5)

    def load_set(self):
        if self.set_idx >= len(self.level_sets):
            messagebox.showinfo("Level Complete", f"🎉 Level {self.level_number} completed!")
            if self.level_number < 3:
                self.level_number += 1
                self.level_sets = LEVELS[self.level_number]
                self.set_idx = 0
            else:
                self.set_idx = 0

        self.current_target = self.level_sets[self.set_idx]
        self.target_label.config(text=self.current_target)
        self.input_var.set("")
        self.start_time = time.time()
        self.update_stats()

    def on_type(self, event=None):
        typed = self.input_var.get()
        # Update heatmap
        for i, c in enumerate(typed):
            correct = i < len(self.current_target) and c == self.current_target[i]
            update_heatmap(c, correct)
        # Stats
        elapsed = max(0.001, time.time() - self.start_time)
        wpm = len(typed.split()) / elapsed * 60
        correct_chars = sum(typed[i] == self.current_target[i] for i in range(min(len(typed),len(self.current_target))))
        acc = correct_chars/len(typed)*100 if typed else 100
        self.stats_label.config(text=f"WPM: {wpm:.1f} | Accuracy: {acc:.1f}%")
        self.progress_label.config(text=progress_bar(self.set_idx, len(self.level_sets)) + f" {self.set_idx}/{len(self.level_sets)}")

        # Auto-complete
        if normalize(typed) == normalize(self.current_target):
            progress["total_words"] += len(self.current_target.split())
            progress["total_time"] += elapsed
            progress["current_set"] = self.set_idx +1
            save_progress()
            self.set_idx +=1
            self.load_set()

    def next_set(self):
        self.set_idx +=1
        self.load_set()

    def daily_practice(self):
        today = datetime.today().strftime("%Y-%m-%d")
        if progress["last_practice"] != today:
            progress["streak"] +=1
            progress["last_practice"] = today
            save_progress()
        messagebox.showinfo("Daily Practice", f"Daily practice started! Streak: {progress['streak']} days")
        self.load_set()

    def add_custom_lesson(self):
        text = simpledialog.askstring("Custom Lesson", "Enter text for custom lesson:")
        if text:
            progress["custom_lessons"].append(text)
            save_progress()
            messagebox.showinfo("Custom Lesson", "Lesson added!")

    def typing_test(self, minutes):
        end_time = time.time() + minutes*60
        total_typed = ""
        while time.time() < end_time:
            sample = random.choice(LEVELS[3])
            typed = simpledialog.askstring("Typing Test", sample)
            if typed:
                total_typed += " " + typed
        words = len(total_typed.split())
        wpm = words / minutes
        messagebox.showinfo(f"{minutes}-Minute Typing Test", f"Test Complete! WPM: {wpm:.1f}")

    def show_stats(self):
        total_time = progress["total_time"] or 1
        avg_wpm = progress["total_words"] / (total_time/60) if progress["total_words"] else 0
        heatmap_text = "\n".join(f"{k}:{v['correct']}/{v['correct']+v['wrong']} correct" for k,v in progress["heatmap"].items())
        stats = f"Level: {progress['level']}\nTotal Words: {progress['total_words']}\nErrors: {progress['total_errors']}\nAvg WPM: {avg_wpm:.1f}\nStreak: {progress['streak']} days\nHeatmap:\n{heatmap_text}"
        messagebox.showinfo("Stats", stats)

    def change_theme(self):
        choice = simpledialog.askstring("Change Theme", f"Available: {', '.join(THEMES.keys())}")
        if choice in THEMES:
            progress["theme"] = choice
            save_progress()
            global THEME
            THEME = THEMES[choice]
            self.configure(bg=THEME["bg"])
            self.target_label.config(bg=THEME["bg"], fg=THEME["accent"])
            self.stats_label.config(bg=THEME["bg"], fg=THEME["fg"])
            self.progress_label.config(bg=THEME["bg"], fg=THEME["fg"])
            for child in self.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=THEME["bg"])
            messagebox.showinfo("Theme", f"Theme changed to {choice}")
        else:
            messagebox.showerror("Theme", "Invalid theme")

# ======================================================
# RUN APP
# ======================================================
if __name__ == "__main__":
    app = TypingTrainerGUI()
    app.mainloop()
