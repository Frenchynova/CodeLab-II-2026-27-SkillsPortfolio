import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import time
from pathlib import Path

BG, WHITE, NAVY = "#F3F5F7", "#FFFFFF", "#172B3A"
TEAL, MUTED, LINE = "#187A70", "#697985", "#DEE5E9"
RED, PALE = "#A6453D", "#EAF5F2"
LEVELS = {"Easy": (0, 9), "Moderate": (10, 99), "Advanced": (1000, 9999)}
FILE = Path.home() / ".maths_studio_history.json"


def randomInt(level):
    return random.randint(*LEVELS[level])


def decideOperation():
    return random.choice(("+", "-"))


def grade(score):
    return next(g for minimum, g in [
        (95, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (0, "F")
    ] if score >= minimum)


class MathsStudio:
    def __init__(self, root):
        self.root, self.page, self.timer = root, "home", None
        self.history = []
        root.title("Maths Studio")
        root.geometry("1060x820")
        root.minsize(960, 780)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)

        try:
            data = json.loads(FILE.read_text("utf-8"))
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

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", background=TEAL, troughcolor=LINE,
                        borderwidth=0, lightcolor=TEAL, darkcolor=TEAL)
        style.configure("Treeview", rowheight=32, background=WHITE,
                        fieldbackground=WHITE, foreground=NAVY,
                        font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", background="#EDF2F5",
                        foreground=NAVY, padding=10,
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", TEAL)],
                  foreground=[("selected", WHITE)])

        header = tk.Frame(root, bg=NAVY, padx=30, pady=16)
        header.pack(fill="x")
        self.label(header, "MATHS / STUDIO", 17, WHITE, True).pack(side="left")
        self.button(header, "Session history",
                    lambda: self.navigate(self.showHistory)).pack(side="right")
        self.button(header, "Practice",
                    lambda: self.navigate(self.displayMenu)).pack(side="right", padx=10)

        footer = tk.Frame(root, bg=BG, padx=32, pady=12)
        footer.pack(side="bottom", fill="x")
        self.label(footer, "MATHS STUDIO", 9, MUTED, True).pack(side="left")
        self.label(footer, "Small steps. Steady progress.", 9, MUTED).pack(side="right")
        self.main = tk.Frame(root, bg=BG, padx=36, pady=26)
        self.main.pack(fill="both", expand=True)
        self.displayMenu()

    def label(self, parent, text, size=11, color=NAVY, bold=False):
        return tk.Label(
            parent, text=text, bg=parent["bg"], fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            anchor="w", justify="left"
        )

    def button(self, parent, text, command, primary=False):
        normal, hover = (TEAL, "#12645C") if primary else (WHITE, "#E9EFF2")
        button = tk.Button(
            parent, text=text, command=command, bg=normal,
            fg=WHITE if primary else NAVY, relief="flat", bd=0,
            activebackground=hover, activeforeground=WHITE if primary else NAVY,
            font=("Segoe UI", 10, "bold"), padx=20, pady=12, cursor="hand2",
            highlightthickness=2, highlightbackground=normal,
            highlightcolor="#89B9B4"
        )
        button.bind("<Enter>", lambda e: button.config(bg=hover))
        button.bind("<Leave>", lambda e: button.config(bg=normal))
        button.bind("<Return>", lambda e: (button.invoke(), "break")[1])
        return button

    def card(self, parent):
        return tk.Frame(parent, bg=WHITE, padx=24, pady=22,
                        highlightbackground=LINE, highlightthickness=1)

    def clear(self, page):
        self.page = page
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        for widget in self.main.winfo_children():
            widget.destroy()

    def heading(self, eyebrow, title, subtitle):
        self.label(self.main, eyebrow, 10, TEAL, True).pack(anchor="w", pady=(0, 8))
        self.label(self.main, title, 29, bold=True).pack(anchor="w", pady=(0, 8))
        self.label(self.main, subtitle, 11, MUTED).pack(anchor="w", pady=(0, 24))

    def best(self, level):
        return max((r["score"] for r in self.history if r["level"] == level),
                   default=None)

    def stat(self, parent, title, value):
        box = self.card(parent)
        box.pack(side="left", fill="both", expand=True, padx=4)
        self.label(box, title, 9, MUTED, True).pack(anchor="w")
        value_label = self.label(box, value, 21, bold=True)
        value_label.pack(anchor="w", pady=(7, 0))
        return value_label

    def displayMenu(self):
        self.clear("home")
        self.heading("YOUR PRACTICE SPACE", "Build confidence, one question at a time.",
                     "Choose a level and settle into a short, focused practice session.")

        summary = tk.Frame(self.main, bg=BG)
        summary.pack(fill="x", pady=(0, 26))
        self.stat(summary, "SAVED SESSIONS", str(len(self.history)))
        self.stat(summary, "QUESTIONS PER SESSION", "10")
        self.stat(summary, "MAXIMUM SCORE", "100")

        self.label(self.main, "CHOOSE YOUR LEVEL", 10, MUTED, True).pack(anchor="w", pady=(0, 12))
        levels = tk.Frame(self.main, bg=BG)
        levels.pack(fill="x")
        descriptions = [
            ("Easy", "Start with the essentials.", "Single-digit numbers"),
            ("Moderate", "Give yourself a little stretch.", "Two-digit numbers"),
            ("Advanced", "Take on a bigger challenge.", "Four-digit numbers"),
        ]
        for column, (level, description, detail) in enumerate(descriptions):
            levels.columnconfigure(column, weight=1, uniform="level")
            card = self.card(levels)
            card.grid(row=0, column=column, sticky="nsew", padx=4)
            self.label(card, f"0{column + 1}", 10, TEAL, True).pack(anchor="w")
            self.label(card, level, 21, bold=True).pack(anchor="w", pady=(12, 6))
            self.label(card, detail, 10, MUTED).pack(anchor="w")
            self.label(card, description, 10, MUTED).pack(anchor="w", pady=(6, 20))
            best = self.best(level)
            self.label(card, "No score yet" if best is None else f"Personal best: {best}/100",
                       10, TEAL, True).pack(anchor="w", pady=(0, 14))
            self.button(card, "Start practice", lambda value=level: self.start(value),
                        True).pack(fill="x")

        self.label(self.main,
                   "HOW IT WORKS   ·   10 points on your first try. 5 on your second.\n"
                   "Addition and subtraction only. Negative answers are possible. No time limit.",
                   10, MUTED).pack(anchor="w", pady=(24, 0))

    def start(self, level):
        self.level, self.score, self.number = level, 0, 0
        self.records, self.started = [], time.monotonic()
        self.displayProblem()

    def displayProblem(self):
        self.clear("quiz")
        self.number += 1
        self.attempt, self.answers, self.accepting = 1, [], True
        a, b, operation = randomInt(self.level), randomInt(self.level), decideOperation()
        self.problem = f"{a} {operation} {b}"
        self.solution = a + b if operation == "+" else a - b

        self.heading(f"{self.level.upper()} / PRACTICE",
                     f"Question {self.number:02d} of 10",
                     "Take your time. Accuracy comes first.")

        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", pady=(0, 16))
        self.score_label = self.stat(stats, "CURRENT SCORE", f"{self.score}/100")
        self.clock = self.stat(stats, "PRACTICE TIME", "00:00")
        self.attempt_label = self.stat(stats, "ATTEMPT", "1 of 2")
        self.progress = ttk.Progressbar(self.main, maximum=10, value=self.number - 1)
        self.progress.pack(fill="x", padx=4, pady=(0, 18))

        card = self.card(self.main)
        card.pack(fill="x", padx=4)
        self.label(card, "SOLVE THE EXPRESSION", 10, MUTED, True).pack(anchor="center")
        self.label(card, self.problem + " = ?", 42, bold=True).pack(pady=(12, 20))
        self.label(card, "YOUR ANSWER", 9, MUTED, True).pack()
        self.entry = tk.Entry(
            card, font=("Segoe UI", 25), width=18, justify="center",
            bg=BG, fg=NAVY, relief="flat", insertbackground=TEAL,
            highlightthickness=2, highlightbackground=LINE, highlightcolor=TEAL
        )
        self.entry.pack(pady=10, ipady=9)
        self.entry.bind("<Return>", self.submit)
        self.feedback = self.label(card, "Enter a whole number below the question.", 11, MUTED)
        self.feedback.pack(pady=(8, 0))
        self.action = self.button(self.main, "Check answer  →", self.submit, True)
        self.action.pack(fill="x", padx=4, pady=(18, 8))
        self.label(self.main, "Enter to submit or continue · Tab to move between controls",
                   9, MUTED).pack(anchor="center")
        self.entry.focus_set()
        self.tick()

    def tick(self):
        seconds = int(time.monotonic() - self.started)
        self.clock.config(text=f"{seconds // 60:02d}:{seconds % 60:02d}")
        self.timer = self.root.after(1000, self.tick)

    def isCorrect(self, answer):
        correct = answer == self.solution
        points = 10 if self.attempt == 1 else 5
        message = (f"Correct. You earned {points} points." if correct else
                   "Not quite. You have one more try." if self.attempt == 1 else
                   f"The correct answer is {self.solution}.")
        self.feedback.config(text=message, fg=TEAL if correct else RED)
        return correct

    def submit(self, event=None):
        if not self.accepting:
            return "break"
        try:
            answer = int(self.entry.get().strip())
        except ValueError:
            self.feedback.config(text="Please enter a whole number, such as 12 or -5.", fg=RED)
            return "break"

        self.answers.append(answer)
        correct = self.isCorrect(answer)
        if not correct and self.attempt == 1:
            self.attempt = 2
            self.attempt_label.config(text="2 of 2")
            self.entry.delete(0, "end")
            self.entry.focus_set()
            return "break"

        points = (10 if self.attempt == 1 else 5) if correct else 0
        self.score += points
        self.records.append((self.problem, ", ".join(map(str, self.answers)),
                             self.solution, points))
        self.accepting = False
        self.entry.config(state="disabled")
        self.score_label.config(text=f"{self.score}/100")
        self.progress.config(value=self.number)
        self.action.config(
            text="View results  →" if self.number == 10 else "Next question  →",
            command=self.displayResults if self.number == 10 else self.displayProblem
        )
        self.action.focus_set()
        return "break"

    def table(self, headings):
        frame = tk.Frame(self.main, bg=WHITE)
        frame.pack(fill="both", expand=True, pady=10)
        table = ttk.Treeview(frame, columns=headings, show="headings", height=8)
        for heading in headings:
            table.heading(heading, text=heading)
            table.column(heading, width=160, minwidth=75, anchor="center")
        scroll = ttk.Scrollbar(frame, command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(fill="both", expand=True)
        return table

    def displayResults(self):
        seconds, previous = int(time.monotonic() - self.started), self.best(self.level)
        self.history.append(dict(date=time.strftime("%d %b %Y, %H:%M"),
                                 level=self.level, score=self.score, seconds=seconds))
        self.history = self.history[-50:]
        saved = True
        try:
            temporary = FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.history), encoding="utf-8")
            temporary.replace(FILE)
        except OSError:
            saved = False

        self.clear("results")
        self.heading("SESSION COMPLETE", "A little progress, well earned.",
                     f"{self.level} practice · Review your answers below.")
        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", pady=(0, 14))
        self.stat(stats, "FINAL SCORE", f"{self.score}/100")
        self.stat(stats, "GRADE", grade(self.score))
        self.stat(stats, "FIRST-TRY ANSWERS", f"{sum(r[3] == 10 for r in self.records)}/10")
        self.stat(stats, "TIME", f"{seconds // 60}:{seconds % 60:02d}")
        if previous is None or self.score > previous:
            self.label(self.main, "Personal best at this level.", 11, TEAL, True).pack(anchor="w")

        controls = tk.Frame(self.main, bg=BG)
        controls.pack(fill="x", pady=(12, 0))
        self.label(controls, "ANSWER REVIEW", 10, MUTED, True).pack(side="left")
        missed = tk.BooleanVar(value=False)
        table = self.table(("Question", "Your attempts", "Correct answer", "Points"))

        def refresh():
            for item in table.get_children():
                table.delete(item)
            for row in self.records:
                if not missed.get() or row[3] == 0:
                    table.insert("", "end", values=row)

        tk.Checkbutton(
            controls, text="Only missed questions (0 points)",
            variable=missed, command=refresh, bg=BG, fg=MUTED,
            activebackground=BG, font=("Segoe UI", 10)
        ).pack(side="right")
        refresh()
        if not saved:
            self.label(self.main, "This session could not be saved.", 10, RED).pack(anchor="w")
        self.button(self.main, "Start another session  →",
                    self.displayMenu, True).pack(anchor="e", pady=(8, 0))

    def showHistory(self):
        self.clear("history")
        self.heading("YOUR PROGRESS", "Every session counts.",
                     "Your latest 50 completed sessions, newest first.")
        if not self.history:
            card = self.card(self.main)
            card.pack(fill="x")
            self.label(card, "Your progress starts here.", 20, bold=True).pack(anchor="w")
            self.label(card, "Complete a quiz to see your results here.", 11, MUTED).pack(
                anchor="w", pady=12)
            self.button(card, "Start practice", self.displayMenu, True).pack(anchor="w")
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
        self.navigate(self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    MathsStudio(root)
    root.mainloop()