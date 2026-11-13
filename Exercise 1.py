"""Maths Studio — Python 3 / Tkinter. No extra packages required."""

import json
import random
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

BG = "#F4F3EF"
WHITE = "#FFFFFF"
INK = "#24352E"
MUTED = "#728077"
GREEN = "#276B50"
LIGHT = "#E8F0E9"
RED = "#A34F38"
LINE = "#DFE4DE"
LEVELS = {
    "Easy": (0, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999),
}


def randomInt(level):
    return random.randint(*LEVELS[level])


def decideOperation():
    return random.choice(("+", "-"))


def ranking(score):
    for minimum, name in (
        (95, "A+"), (80, "A"), (70, "B"),
        (60, "C"), (50, "D"), (0, "F")
    ):
        if score >= minimum:
            return name


class MathsStudio:
    def __init__(self, root):
        self.root = root
        root.title("Maths Studio")
        root.geometry("1060x790")
        root.minsize(980, 750)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)

        self.screen = "home"
        self.timer_job = None
        self.sessions = []
        self.storage = Path.home() / ".maths_studio_history.json"
        self.loadHistory()

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(
            "Studio.Horizontal.TProgressbar",
            background=GREEN,
            troughcolor=LINE,
            borderwidth=0,
            lightcolor=GREEN,
            darkcolor=GREEN,
        )
        style.configure(
            "Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=INK,
            font=("Segoe UI", 10),
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=LIGHT,
            foreground=INK,
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.map(
            "Treeview",
            background=[("selected", GREEN)],
            foreground=[("selected", WHITE)],
        )

        sidebar = tk.Frame(root, bg=INK, width=205)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.text(
            sidebar, "MATHS\nSTUDIO", 23, WHITE, True, INK
        ).pack(anchor="w", padx=25, pady=(35, 8))
        self.text(
            sidebar, "A little better, daily.", 10, "#B9C8BE",
            bg=INK
        ).pack(anchor="w", padx=25, pady=(0, 35))

        self.button(
            sidebar, "Practice", self.goHome
        ).pack(fill="x", padx=20, pady=5)
        self.button(
            sidebar, "Session history", self.showHistory
        ).pack(fill="x", padx=20, pady=5)

        self.text(
            sidebar,
            "10 questions\n2 chances\n100 possible points",
            11, "#B9C8BE", bg=INK
        ).pack(side="bottom", anchor="w", padx=25, pady=35)

        self.main = tk.Frame(root, bg=BG, padx=30, pady=26)
        self.main.pack(side="left", fill="both", expand=True)
        self.displayMenu()

    def text(self, parent, value, size=11, color=INK,
             bold=False, bg=BG):
        return tk.Label(
            parent, text=value, bg=bg, fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            justify="left", anchor="w",
        )

    def button(self, parent, value, command, primary=False):
        normal = GREEN if primary else WHITE
        hover = "#1D543E" if primary else LIGHT
        button = tk.Button(
            parent, text=value, command=command,
            bg=normal, fg=WHITE if primary else INK,
            activebackground=hover,
            activeforeground=WHITE if primary else INK,
            font=("Segoe UI", 11, "bold"),
            relief="flat", bd=0, padx=18, pady=12,
            cursor="hand2",
            highlightthickness=2,
            highlightbackground=normal,
            highlightcolor="#A5BBA9",
        )
        button.bind("<Enter>", lambda event: button.config(bg=hover))
        button.bind("<Leave>", lambda event: button.config(bg=normal))

        def activate(event):
            button.invoke()
            return "break"

        button.bind("<Return>", activate)
        return button

    def clear(self):
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        for widget in self.main.winfo_children():
            widget.destroy()

    def heading(self, eyebrow, title, subtitle):
        self.text(
            self.main, eyebrow, 10, GREEN, True
        ).pack(anchor="w", pady=(0, 8))
        self.text(
            self.main, title, 30, bold=True
        ).pack(anchor="w", pady=(0, 8))
        self.text(
            self.main, subtitle, 11, MUTED
        ).pack(anchor="w", pady=(0, 22))

    def card(self, parent):
        return tk.Frame(
            parent, bg=WHITE, padx=22, pady=20,
            highlightbackground=LINE, highlightthickness=1,
        )

    def loadHistory(self):
        try:
            records = json.loads(self.storage.read_text("utf-8"))
            if not isinstance(records, list):
                return
            self.sessions = [
                row for row in records
                if isinstance(row, dict)
                and row.get("level") in LEVELS
                and type(row.get("score")) is int
                and 0 <= row["score"] <= 100
                and isinstance(row.get("date"), str)
                and type(row.get("seconds")) is int
                and row["seconds"] >= 0
            ][-50:]
        except (OSError, ValueError):
            pass

    def best(self, level):
        scores = [
            row["score"] for row in self.sessions
            if row["level"] == level
        ]
        return max(scores) if scores else None

    def displayMenu(self):
        self.screen = "home"
        self.clear()
        self.heading(
            "YOUR DAILY PRACTICE",
            "Make room for a little maths.",
            "Choose a level. Take your time. Build your confidence.",
        )

        stats = self.card(self.main)
        stats.pack(fill="x", pady=(0, 20))
        self.text(
            stats,
            f"{len(self.sessions)} saved sessions"
            "     /     10 questions per session",
            13, bold=True, bg=WHITE
        ).pack(anchor="w")

        descriptions = {
            "Easy": "Single digits · A comfortable starting point",
            "Moderate": "Two digits · A little more to think about",
            "Advanced": "Four digits · A proper mental workout",
        }
        for level in LEVELS:
            row = self.card(self.main)
            row.pack(fill="x", pady=5)
            best = self.best(level)
            best_text = "No score yet" if best is None else f"Best {best}/100"
            self.button(
                row, "Start", lambda chosen=level: self.start(chosen),
                primary=True
            ).pack(side="right", padx=(15, 0))
            self.text(
                row, f"{level}   ·   {best_text}",
                14, bold=True, bg=WHITE
            ).pack(anchor="w")
            self.text(
                row, descriptions[level], 10, MUTED, bg=WHITE
            ).pack(anchor="w", pady=(5, 0))

        self.text(
            self.main,
            "First try: 10 points. Second try: 5 points.\n"
            "Addition and subtraction only. Negative answers are possible.\n"
            "The practice timer has no time limit.",
            10, MUTED
        ).pack(anchor="w", pady=(20, 0))

    def start(self, level):
        self.level = level
        self.score = 0
        self.number = 0
        self.records = []
        self.started = time.monotonic()
        self.displayProblem()

    def displayProblem(self):
        self.clear()
        self.screen = "quiz"
        self.accepting = True
        self.number += 1
        self.attempt = 1
        self.answers = []

        first = randomInt(self.level)
        second = randomInt(self.level)
        operation = decideOperation()
        self.problem = f"{first} {operation} {second}"
        self.solution = (
            first + second if operation == "+" else first - second
        )

        self.heading(
            f"PRACTICE / {self.level.upper()}",
            f"Question {self.number:02d}",
            "Focus on one answer at a time.",
        )

        status = tk.Frame(self.main, bg=BG)
        status.pack(fill="x", pady=(0, 12))
        self.score_label = self.text(
            status, f"SCORE  {self.score}/100", 11, GREEN, True
        )
        self.score_label.pack(side="left")
        self.clock = self.text(status, "", 11, MUTED)
        self.clock.pack(side="right")

        self.progress = ttk.Progressbar(
            self.main, maximum=10, value=self.number - 1,
            style="Studio.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x", pady=(0, 20))

        card = self.card(self.main)
        card.pack(fill="x")
        self.text(
            card, "SOLVE THE EXPRESSION", 10, MUTED, True, WHITE
        ).pack(anchor="w", pady=(0, 15))
        self.text(
            card, f"{self.problem} = ?", 38, bold=True, bg=WHITE
        ).pack(anchor="w", pady=(0, 20))
        self.text(
            card, "Your answer", 11, MUTED, bg=WHITE
        ).pack(anchor="w", pady=(0, 8))

        self.entry = tk.Entry(
            card, font=("Segoe UI", 25),
            bg=BG, fg=INK, insertbackground=GREEN,
            relief="flat", highlightthickness=2,
            highlightbackground=LINE, highlightcolor=GREEN,
        )
        self.entry.pack(fill="x", ipady=12)
        self.entry.bind("<Return>", self.submit)
        self.feedback = self.text(
            card, "Attempt 1 of 2", 12, MUTED, bg=WHITE
        )
        self.feedback.pack(anchor="w", pady=(18, 0))

        self.action = self.button(
            self.main, "Check answer", self.submit, primary=True
        )
        self.action.pack(fill="x", pady=(20, 12))
        self.text(
            self.main,
            "Press Enter to check your answer or continue.",
            10, MUTED
        ).pack(anchor="w")

        self.entry.focus_set()
        self.tick()

    def tick(self):
        seconds = int(time.monotonic() - self.started)
        self.clock.config(
            text=f"TIME  {seconds // 60:02d}:{seconds % 60:02d}"
        )
        self.timer_job = self.root.after(1000, self.tick)

    def isCorrect(self, answer):
        correct = answer == self.solution
        if correct:
            points = 10 if self.attempt == 1 else 5
            message = f"Correct. You earned {points} points."
        elif self.attempt == 1:
            message = "Not quite. You have one more try."
        else:
            message = f"The correct answer is {self.solution}."
        self.feedback.config(
            text=message, fg=GREEN if correct else RED
        )
        return correct

    def submit(self, event=None):
        if self.screen != "quiz" or not self.accepting:
            return "break"
        try:
            answer = int(self.entry.get().strip())
        except ValueError:
            self.feedback.config(
                text="Enter a whole number, such as 12 or -5.",
                fg=RED,
            )
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
        self.records.append((
            self.problem, ", ".join(map(str, self.answers)),
            self.solution, points,
        ))
        self.accepting = False
        self.entry.config(state="disabled")
        self.score_label.config(text=f"SCORE  {self.score}/100")
        self.progress.config(value=self.number)
        self.action.config(
            text="See your results" if self.number == 10
            else "Next question",
            command=self.nextQuestion,
        )
        self.action.focus_set()
        return "break"

    def nextQuestion(self):
        if self.screen != "quiz" or self.accepting:
            return
        if self.number == 10:
            self.displayResults()
        else:
            self.displayProblem()

    def displayResults(self):
        elapsed = int(time.monotonic() - self.started)
        previous = self.best(self.level)
        self.sessions.append({
            "date": time.strftime("%d %b %Y, %H:%M"),
            "level": self.level,
            "score": self.score,
            "seconds": elapsed,
        })
        self.sessions = self.sessions[-50:]
        saved = True
        try:
            temporary = self.storage.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(self.sessions, indent=2), encoding="utf-8"
            )
            temporary.replace(self.storage)
        except OSError:
            saved = False

        self.screen = "results"
        self.clear()
        first = sum(row[3] == 10 for row in self.records)
        self.heading(
            "SESSION COMPLETE",
            f"{self.score} / 100",
            f"Grade {ranking(self.score)}    ·    "
            f"{first}/10 correct first try    ·    "
            f"{elapsed // 60}:{elapsed % 60:02d}",
        )

        if previous is None or self.score > previous:
            self.text(
                self.main, "Your best score at this level.",
                12, GREEN, True
            ).pack(anchor="w", pady=(0, 12))

        controls = tk.Frame(self.main, bg=BG)
        controls.pack(fill="x", pady=(0, 10))
        self.text(
            controls, "ANSWER REVIEW", 10, MUTED, True
        ).pack(side="left")
        self.missed = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls, text="Only missed questions",
            variable=self.missed, command=self.fillReview,
            bg=BG, fg=INK, activebackground=BG,
            selectcolor=WHITE, font=("Segoe UI", 10),
        ).pack(side="right")

        self.review = self.table(
            ("Question", "Your attempts", "Correct", "Points"),
            (190, 180, 110, 75),
        )
        self.fillReview()
        self.review_note = self.text(
            self.main,
            "Missed questions are those worth 0 points.",
            10, MUTED
        )
        self.review_note.pack(anchor="w", pady=10)

        if not saved:
            self.text(
                self.main,
                "This session could not be saved to your computer.",
                10, RED
            ).pack(anchor="w")

        self.button(
            self.main, "Practice again", self.displayMenu, True
        ).pack(fill="x", pady=(10, 0))

    def table(self, headings, widths):
        holder = tk.Frame(self.main, bg=WHITE)
        holder.pack(fill="both", expand=True)
        columns = tuple(str(i) for i in range(len(headings)))
        table = ttk.Treeview(
            holder, columns=columns, show="headings", height=10
        )
        for column, title, width in zip(columns, headings, widths):
            table.heading(column, text=title)
            table.column(column, width=width, minwidth=60, anchor="center")
        scroll = ttk.Scrollbar(
            holder, orient="vertical", command=table.yview
        )
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(side="left", fill="both", expand=True)
        return table

    def fillReview(self):
        for item in self.review.get_children():
            self.review.delete(item)
        for row in self.records:
            if not self.missed.get() or row[3] == 0:
                self.review.insert("", "end", values=row)

    def canLeave(self):
        if self.screen != "quiz":
            return True
        return messagebox.askyesno(
            "Leave this session?",
            "Your current quiz will end without saving a score.",
            parent=self.root,
        )

    def goHome(self):
        if self.canLeave():
            self.displayMenu()

    def showHistory(self):
        if not self.canLeave():
            return
        self.screen = "history"
        self.clear()
        self.heading(
            "YOUR PROGRESS",
            "Every session counts.",
            "Your latest 50 completed sessions, newest first.",
        )
        if not self.sessions:
            self.text(
                self.main,
                "Complete a quiz to see your progress here.",
                13, MUTED
            ).pack(anchor="w", pady=20)
            return

        table = self.table(
            ("Completed", "Level", "Score", "Time"),
            (220, 150, 100, 85),
        )
        for row in reversed(self.sessions):
            seconds = row["seconds"]
            table.insert("", "end", values=(
                row["date"], row["level"],
                f'{row["score"]}/100',
                f"{seconds // 60}:{seconds % 60:02d}",
            ))

    def close(self):
        if self.canLeave():
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    MathsStudio(root)
    root.mainloop()