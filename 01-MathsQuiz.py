import tkinter as tk
from tkinter import ttk, messagebox, font
from pathlib import Path
import random
import json
import time
import math

# Appearance
BG = "#F2F4F7"
WHITE = "#FFFFFF"
NAVY = "#101B35"
INK = "#24324A"
MUTED = "#738096"
MINT = "#45D9BC"
TEAL = "#087D68"
CORAL = "#EF7968"
LINE = "#DFE5ED"
PALE = "#E8F7F2"

LEVELS = {"Easy": (0, 9), "Moderate": (10, 99), "Advanced": (1000, 9999)}
FOLDER = Path(__file__).resolve().parent
HISTORY_FILE = Path.home() / ".maths_studio_history.json"


def randomInt(level):
    return random.randint(*LEVELS[level])


def decideOperation():
    return random.choice(("+", "-"))


def grade(score):
    boundaries = [(95, "A+"), (80, "A"), (70, "B"),
                  (60, "C"), (50, "D"), (0, "F")]
    return next(letter for minimum, letter in boundaries if score >= minimum)


class MathsStudio:
    def __init__(self, root):
        self.root = root
        self.page = "home"
        self.timer = None
        self.history = []
        self.logo = None

        installed = set(font.families())
        self.body_font = next(
            (f for f in ("Segoe UI", "Aptos", "Helvetica") if f in installed),
            "TkDefaultFont"
        )
        self.title_font = next(
            (f for f in ("Bahnschrift", "Aptos Display", "Segoe UI")
             if f in installed), self.body_font
        )

        root.title("Maths Studio")
        width = min(1120, root.winfo_screenwidth() - 80)
        height = min(860, root.winfo_screenheight() - 100)
        root.geometry(f"{width}x{height}")
        root.minsize(850, 600)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.loadHistory()

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(
            "Treeview", background=WHITE, fieldbackground=WHITE,
            foreground=INK, rowheight=34, borderwidth=0,
            font=(self.body_font, 10)
        )
        style.configure(
            "Treeview.Heading", background="#EAF0F5", foreground=INK,
            padding=10, font=(self.body_font, 10, "bold")
        )
        style.map("Treeview", background=[("selected", TEAL)],
                  foreground=[("selected", WHITE)])

        self.sidebar = tk.Frame(root, bg=NAVY, width=192)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.makeLogo()

        self.text(self.sidebar, "MATHS\nSTUDIO", 23, WHITE,
                  bold=True).pack(anchor="w", padx=24, pady=(8, 5))
        self.text(self.sidebar, "A practice space.", 10, "#A4B1C7").pack(
            anchor="w", padx=24, pady=(0, 35))

        self.button(self.sidebar, "Practice",
                    lambda: self.navigate(self.displayMenu)).pack(
                        fill="x", padx=18, pady=5)
        self.button(self.sidebar, "Session history",
                    lambda: self.navigate(self.showHistory)).pack(
                        fill="x", padx=18, pady=5)

        self.text(
            self.sidebar, "TEN QUESTIONS.\nONE FRESH START.",
            9, "#A4B1C7", bold=True
        ).pack(side="bottom", anchor="w", padx=24, pady=30)

        # Scrollable content keeps every screen accessible.
        outer = tk.Frame(root, bg=BG)
        outer.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.main = tk.Frame(self.canvas, bg=BG, padx=28, pady=26)
        self.content = self.canvas.create_window(
            (0, 0), window=self.main, anchor="nw"
        )
        self.main.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(
            self.content, width=e.width))
        root.bind("<MouseWheel>", self.scroll)
        self.displayMenu()

    def text(self, parent, value, size=11, color=INK, bold=False):
        return tk.Label(
            parent, text=value, bg=parent["bg"], fg=color,
            font=(self.title_font if size >= 23 else self.body_font,
                  size, "bold" if bold else "normal"),
            anchor="w", justify="left"
        )

    def button(self, parent, value, command, primary=False):
        normal, hover = (MINT, "#70E5CD") if primary else (WHITE, "#EAF0F5")
        button = tk.Button(
            parent, text=value, command=command, bg=normal, fg=NAVY,
            activebackground=hover, activeforeground=NAVY,
            relief="flat", bd=0, padx=16, pady=12, cursor="hand2",
            font=(self.body_font, 10, "bold"),
            highlightthickness=2, highlightbackground=normal,
            highlightcolor=TEAL
        )
        button.bind("<Enter>", lambda e: button.config(bg=hover))
        button.bind("<Leave>", lambda e: button.config(bg=normal))
        button.bind("<Return>", lambda e: (button.invoke(), "break")[1])
        return button

    def card(self, parent, color=WHITE):
        return tk.Frame(
            parent, bg=color, padx=22, pady=20,
            highlightbackground=LINE if color == WHITE else color,
            highlightthickness=1
        )

    def makeLogo(self):
        try:
            image = tk.PhotoImage(file=str(FOLDER / "maths_studio_logo.png"))
            scale = max(1, math.ceil(max(image.width(), image.height()) / 72))
            self.logo = image.subsample(scale)
            tk.Label(self.sidebar, image=self.logo, bg=NAVY).pack(
                anchor="w", padx=20, pady=(24, 0))
            self.root.iconphoto(True, self.logo)
        except (tk.TclError, OSError):
            icon = tk.Canvas(self.sidebar, width=64, height=64,
                             bg=NAVY, highlightthickness=0)
            icon.pack(anchor="w", padx=24, pady=(28, 8))
            icon.create_rectangle(7, 22, 37, 30, fill=WHITE, outline="")
            icon.create_rectangle(18, 11, 26, 41, fill=WHITE, outline="")
            icon.create_rectangle(31, 43, 59, 49, fill=MINT, outline="")
            icon.create_rectangle(31, 54, 59, 60, fill=MINT, outline="")
            icon.create_oval(46, 9, 59, 22, fill=CORAL, outline="")

    def scroll(self, event):
        if isinstance(event.widget, ttk.Treeview):
            return
        if self.main.winfo_reqheight() > self.canvas.winfo_height():
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction * 3, "units")

    def clear(self, page):
        self.page = page
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        for widget in self.main.winfo_children():
            widget.destroy()
        self.canvas.yview_moveto(0)

    def heading(self, eyebrow, title, subtitle):
        self.text(self.main, eyebrow, 9, TEAL, True).pack(
            anchor="w", pady=(0, 8))
        self.text(self.main, title, 28, bold=True).pack(
            anchor="w", pady=(0, 8))
        self.text(self.main, subtitle, 10, MUTED).pack(
            anchor="w", pady=(0, 22))

    def stat(self, parent, title, value):
        box = self.card(parent)
        box.pack(side="left", fill="both", expand=True, padx=3)
        self.text(box, title, 9, MUTED, True).pack(anchor="w")
        label = self.text(box, value, 23, bold=True)
        label.pack(anchor="w", pady=(8, 0))
        return label

    def loadHistory(self):
        try:
            data = json.loads(HISTORY_FILE.read_text("utf-8"))
            if isinstance(data, list):
                self.history = [
                    r for r in data if isinstance(r, dict)
                    and r.get("level") in LEVELS
                    and type(r.get("score")) is int and 0 <= r["score"] <= 100
                    and type(r.get("seconds")) is int and r["seconds"] >= 0
                    and isinstance(r.get("date"), str)
                ][-50:]
        except (OSError, ValueError):
            pass

    def best(self, level):
        return max((r["score"] for r in self.history if r["level"] == level),
                   default=None)

    def displayMenu(self):
        self.clear("home")
        hero = self.card(self.main, NAVY)
        hero.pack(fill="x", pady=(0, 20))
        self.text(hero, "YOUR DAILY PRACTICE", 9, MINT, True).pack(anchor="w")
        self.text(hero, "Your next ten\nstart here.", 35, WHITE, True).pack(
            anchor="w", pady=(14, 10))
        self.text(hero, "A short session. A clearer head. Your own pace.",
                  11, "#BAC6D8").pack(anchor="w")

        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", pady=(0, 24))
        average = (round(sum(r["score"] for r in self.history) / len(self.history))
                   if self.history else None)
        self.stat(stats, "SAVED SESSIONS", str(len(self.history)))
        self.stat(stats, "AVERAGE SCORE", f"{average}/100" if average is not None else "—")
        self.stat(stats, "QUESTIONS / SESSION", "10")

        self.text(self.main, "CHOOSE YOUR LEVEL", 9, MUTED, True).pack(
            anchor="w", pady=(0, 10))

        descriptions = [
            ("Easy", "Single digits", "0–9"),
            ("Moderate", "Two digits", "10–99"),
            ("Advanced", "Four digits", "1000–9999"),
        ]
        for index, (level, detail, numbers) in enumerate(descriptions, 1):
            row = self.card(self.main)
            row.pack(fill="x", pady=4)
            self.button(row, "Start →", lambda chosen=level: self.start(chosen),
                        True).pack(side="right", padx=(10, 0))
            self.text(row, f"0{index}   {level}", 18, bold=True).pack(anchor="w")
            best = self.best(level)
            record = f"Best: {best}/100" if best is not None else "No score yet"
            self.text(row, f"{detail}  ·  {numbers}  ·  {record}",
                      10, MUTED).pack(anchor="w", pady=(5, 0))

        self.text(
            self.main,
            "10 points on your first try. 5 on your second.\n"
            "Addition and subtraction. Negative answers are possible.\n"
            "Statistics use your latest 50 saved sessions.",
            9, MUTED
        ).pack(anchor="w", pady=(20, 0))

    def start(self, level):
        self.level, self.score, self.number = level, 0, 0
        self.records, self.started = [], time.monotonic()
        self.streak = self.longest_streak = 0
        self.displayProblem()

    def displayProblem(self):
        self.clear("quiz")
        self.number += 1
        self.attempt, self.answers, self.accepting = 1, [], True
        a, b = randomInt(self.level), randomInt(self.level)
        operation = decideOperation()
        self.problem = f"{a} {operation} {b}"
        self.solution = a + b if operation == "+" else a - b

        self.heading(
            f"{self.level.upper()} / PRACTICE",
            f"Question {self.number:02d}",
            "Take your time. There is no time limit."
        )
        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", pady=(0, 16))
        self.score_label = self.stat(stats, "SCORE", f"{self.score}/100")
        self.clock = self.stat(stats, "TIME", "00:00")
        self.streak_label = self.stat(stats, "FIRST-TRY STREAK", str(self.streak))

        self.dots = tk.Canvas(self.main, height=42, bg=BG, highlightthickness=0)
        self.dots.pack(fill="x", pady=(0, 15))
        self.dots.bind("<Configure>", lambda e: self.drawProgress())

        card = self.card(self.main)
        card.pack(fill="x")
        self.text(card, "SOLVE THE EXPRESSION", 9, MUTED, True).pack()
        self.text(card, self.problem + " = ?", 42, bold=True).pack(pady=(18, 20))
        self.text(card, "YOUR ANSWER", 9, MUTED, True).pack()
        self.entry = tk.Entry(
            card, width=17, justify="center", font=(self.body_font, 25),
            bg=BG, fg=INK, insertbackground=TEAL, relief="flat",
            highlightthickness=2, highlightbackground=LINE,
            highlightcolor=TEAL
        )
        self.entry.pack(pady=12, ipady=10)
        self.entry.bind("<Return>", self.submit)
        self.feedback = self.text(card, "Attempt 1 of 2", 11, MUTED)
        self.feedback.pack(pady=(8, 0))

        self.action = self.button(self.main, "Check answer →", self.submit, True)
        self.action.pack(fill="x", pady=(18, 10))
        self.text(self.main, "ENTER  Submit or continue    ·    TAB  Move between controls",
                  9, MUTED).pack(anchor="center")
        self.entry.focus_set()
        self.tick()

    def drawProgress(self):
        self.dots.delete("all")
        width = max(self.dots.winfo_width(), 400)
        gap = width / 10
        for i in range(10):
            color = LINE
            foreground = MUTED
            if i < len(self.records):
                points = self.records[i][3]
                color = TEAL if points == 10 else "#B88930" if points == 5 else RED
                foreground = WHITE
            elif i == self.number - 1:
                color, foreground = NAVY, WHITE
            x = gap * (i + 0.5)
            self.dots.create_oval(x - 15, 5, x + 15, 35, fill=color, outline="")
            self.dots.create_text(x, 20, text=str(i + 1), fill=foreground,
                                  font=(self.body_font, 9, "bold"))

    def tick(self):
        seconds = int(time.monotonic() - self.started)
        self.clock.config(text=f"{seconds // 60:02d}:{seconds % 60:02d}")
        self.timer = self.root.after(1000, self.tick)

    def isCorrect(self, answer):
        correct = answer == self.solution
        points = 10 if self.attempt == 1 else 5
        message = (f"Correct. +{points} points." if correct else
                   "Not quite. Try again — attempt 2 of 2." if self.attempt == 1 else
                   f"{self.problem} = {self.solution}. No points this time.")
        self.feedback.config(text=message, fg=TEAL if correct else "#A34F3B")
        return correct

    def submit(self, event=None):
        if not self.accepting:
            return "break"
        try:
            answer = int(self.entry.get().strip())
        except ValueError:
            self.feedback.config(text="Enter a whole number, such as 12 or -5.",
                                 fg="#A34F3B")
            return "break"

        self.answers.append(answer)
        correct = self.isCorrect(answer)
        if not correct and self.attempt == 1:
            self.attempt = 2
            self.entry.delete(0, "end")
            self.entry.focus_set()
            return "break"

        points = (10 if self.attempt == 1 else 5) if correct else 0
        self.score += points
        self.streak = self.streak + 1 if points == 10 else 0
        self.longest_streak = max(self.longest_streak, self.streak)
        self.records.append((
            self.problem, ", ".join(map(str, self.answers)),
            self.solution, points
        ))
        self.accepting = False
        self.entry.config(state="disabled")
        self.score_label.config(text=f"{self.score}/100")
        self.streak_label.config(text=str(self.streak))
        self.drawProgress()
        self.action.config(
            text="View results →" if self.number == 10 else "Next question →",
            command=self.displayResults if self.number == 10 else self.displayProblem
        )
        self.action.focus_set()
        return "break"

    def table(self, headings):
        frame = tk.Frame(self.main, bg=WHITE)
        frame.pack(fill="x", pady=10)
        table = ttk.Treeview(frame, columns=headings, show="headings", height=10)
        for heading in headings:
            table.heading(heading, text=heading)
            table.column(heading, width=140, minwidth=60, anchor="center")
        scroll = ttk.Scrollbar(frame, command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(fill="both", expand=True)
        return table

    def displayResults(self):
        seconds = int(time.monotonic() - self.started)
        previous = self.best(self.level)
        self.history.append(dict(
            date=time.strftime("%d %b %Y, %H:%M"),
            level=self.level, score=self.score, seconds=seconds
        ))
        self.history = self.history[-50:]
        saved = True
        try:
            temporary = HISTORY_FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.history), encoding="utf-8")
            temporary.replace(HISTORY_FILE)
        except OSError:
            saved = False

        self.clear("results")
        self.heading("SESSION COMPLETE", "Ten questions. One step forward.",
                     f"{self.level} practice · {seconds // 60}:{seconds % 60:02d}")

        summary = self.card(self.main, NAVY)
        summary.pack(fill="x", pady=(0, 18))
        self.text(summary, "FINAL SCORE", 9, MINT, True).pack(anchor="w")
        self.text(summary, f"{self.score} / 100", 42, WHITE, True).pack(
            anchor="w", pady=(6, 8))
        self.text(summary, f"Grade {grade(self.score)}", 15, WHITE, True).pack(anchor="w")
        if previous is None or self.score > previous:
            self.text(summary, "Best score in your saved history at this level.",
                      10, MINT).pack(anchor="w", pady=(12, 0))

        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", pady=(0, 18))
        first = sum(row[3] == 10 for row in self.records)
        corrected = sum(row[3] == 5 for row in self.records)
        self.stat(stats, "FIRST TRY", f"{first}/10")
        self.stat(stats, "SECOND TRY", str(corrected))
        self.stat(stats, "BEST STREAK", str(self.longest_streak))

        controls = tk.Frame(self.main, bg=BG)
        controls.pack(fill="x")
        self.text(controls, "ANSWER REVIEW", 9, MUTED, True).pack(side="left")
        missed = tk.BooleanVar(value=False)
        table = self.table(("Question", "Your attempts", "Correct", "Points"))
        note = self.text(self.main, "", 9, MUTED)
        note.pack(anchor="w")

        def refresh():
            for item in table.get_children():
                table.delete(item)
            rows = [r for r in self.records if not missed.get() or r[3] == 0]
            for row in rows:
                table.insert("", "end", values=row)
            note.config(text="No missed questions. Well done." if not rows else
                        "10 points: first try · 5 points: second try · 0 points: missed")

        tk.Checkbutton(
            controls, text="Only missed questions", variable=missed,
            command=refresh, bg=BG, activebackground=BG,
            fg=INK, font=(self.body_font, 10)
        ).pack(side="right")
        refresh()

        if not saved:
            self.text(self.main, "This session could not be saved to your computer.",
                      10, "#A34F3B").pack(anchor="w", pady=8)
        self.button(self.main, "Start another session →", self.displayMenu,
                    True).pack(fill="x", pady=(18, 0))

    def showHistory(self):
        self.clear("history")
        self.heading("YOUR PROGRESS", "Every session adds up.",
                     "Your latest 50 completed sessions, newest first.")
        if not self.history:
            card = self.card(self.main)
            card.pack(fill="x")
            self.text(card, "Your first session is waiting.", 23, bold=True).pack(anchor="w")
            self.text(card, "Complete a quiz to see your results here.",
                      11, MUTED).pack(anchor="w", pady=15)
            self.button(card, "Start practice →", self.displayMenu, True).pack(anchor="w")
            return

        table = self.table(("Completed", "Level", "Score", "Time"))
        for row in reversed(self.history):
            seconds = row["seconds"]
            table.insert("", "end", values=(
                row["date"], row["level"], f'{row["score"]}/100',
                f"{seconds // 60}:{seconds % 60:02d}"
            ))

    def navigate(self, destination):
        if self.page != "quiz" or messagebox.askyesno(
            "Leave this session?",
            "Your current quiz will end without saving a score.",
            parent=self.root
        ):
            destination()

    def close(self):
        def finish():
            if self.timer is not None:
                self.root.after_cancel(self.timer)
            self.root.destroy()
        self.navigate(finish)


if __name__ == "__main__":
    root = tk.Tk()
    MathsStudio(root)
    root.mainloop()