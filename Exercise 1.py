import json
import random
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

BG = "#F3F2EE"
INK = "#24332F"
GREEN = "#226650"
MUTED = "#69756F"
LEVELS = {
    "Easy": (0, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999),
}


def randomInt(level):
    return random.randint(*LEVELS[level])


def decideOperation():
    return random.choice(("+", "-"))


def grade(score):
    for minimum, result in [
        (95, "A+"), (80, "A"), (70, "B"),
        (60, "C"), (50, "D"), (0, "F")
    ]:
        if score >= minimum:
            return result


class MathsQuiz:
    def __init__(self, root):
        self.root = root
        root.title("Maths Studio")
        root.geometry("800x760")
        root.minsize(740, 720)
        root.configure(bg=BG)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            ".", background=BG, foreground=INK,
            font=("Segoe UI", 11)
        )
        style.configure("TButton", padding=14, background="white")
        style.map("TButton", background=[("active", "#DFE8E1")])
        style.configure(
            "Primary.TButton", background=GREEN,
            foreground="white"
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#174B3B")]
        )
        style.configure("TEntry", padding=12)
        style.configure(
            "Horizontal.TProgressbar",
            background=GREEN, troughcolor="#DDE3DC"
        )
        style.configure("Treeview", rowheight=27)
        self.frame = ttk.Frame(root, padding=32)
        self.frame.pack(fill="both", expand=True)

        self.score_file = Path.home() / ".maths_studio_scores.json"
        self.best = {}
        try:
            data = json.loads(self.score_file.read_text())
            if isinstance(data, dict):
                self.best = {
                    key: value for key, value in data.items()
                    if key in LEVELS
                    and type(value) is int
                    and 0 <= value <= 100
                }
        except (OSError, ValueError):
            pass

        self.timer_job = None
        self.state = "menu"
        root.bind("<Return>", self.enter)
        self.displayMenu()

    def clear(self):
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        for widget in self.frame.winfo_children():
            widget.destroy()

    def label(self, text, size=11, color=INK, bold=False):
        label = ttk.Label(
            self.frame, text=text, foreground=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            wraplength=660
        )
        label.pack(anchor="w", pady=(0, 14))
        return label

    def button(self, text, command, primary=False):
        button = ttk.Button(
            self.frame, text=text, command=command,
            style="Primary.TButton" if primary else "TButton"
        )
        button.pack(fill="x", pady=5)
        return button

    def displayMenu(self):
        self.state = "menu"
        self.clear()
        self.label("MATHS STUDIO / PRACTICE", 10, GREEN, True)
        self.label("A little practice.\nA sharper mind.", 34, bold=True)
        self.label(
            "Ten questions. Two chances. Make each answer count.",
            12, MUTED
        )
        ttk.Separator(self.frame).pack(fill="x", pady=16)
        self.label("CHOOSE YOUR LEVEL", 10, MUTED, True)

        for level, bounds in LEVELS.items():
            best = self.best.get(level)
            best_text = f"{best}/100" if best is not None else "—"
            self.button(
                f"{level}    ·    {bounds[0]}–{bounds[1]}"
                f"    ·    Best: {best_text}",
                lambda selected=level: self.start(selected)
            )

        self.label(
            "\nFirst attempt: 10 points · Second attempt: 5 points\n"
            "Addition and subtraction. Answers can be negative.",
            11, MUTED
        )
        self.label(
            "The timer measures practice time. There is no time limit.",
            10, MUTED
        )
        self.button("Close", self.root.destroy)

    def start(self, level):
        self.level = level
        self.score = 0
        self.number = 0
        self.records = []
        self.started = time.monotonic()
        self.displayProblem()

    def displayProblem(self):
        self.clear()
        self.state = "answer"
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

        self.label(f"PRACTICE / {self.level.upper()}", 10, GREEN, True)
        self.status = self.label(
            f"Question {self.number} of 10   ·   Score {self.score}/100",
            12, MUTED
        )
        self.progress = ttk.Progressbar(
            self.frame, maximum=10, value=self.number - 1
        )
        self.progress.pack(fill="x", pady=(0, 28))
        self.label(f"{self.problem} = ?", 40, bold=True)
        self.label("Your answer", 11, MUTED)

        self.entry = ttk.Entry(
            self.frame, font=("Segoe UI", 24), justify="center"
        )
        self.entry.pack(fill="x", pady=(0, 18))
        self.feedback = self.label("Attempt 1 of 2", 12, MUTED)
        self.action = self.button(
            "Submit answer", self.submit, primary=True
        )
        self.clock = self.label("", 10, MUTED)
        self.label("Press Enter to submit or continue.", 10, MUTED)
        self.tick()
        self.entry.focus_set()

    def tick(self):
        seconds = int(time.monotonic() - self.started)
        self.clock.configure(
            text=f"Practice time  {seconds // 60:02d}:{seconds % 60:02d}"
        )
        self.timer_job = self.root.after(1000, self.tick)

    def isCorrect(self, answer):
        correct = answer == self.solution
        if correct:
            points = 10 if self.attempt == 1 else 5
            message = f"Correct. +{points} points."
        elif self.attempt == 1:
            message = "Not quite. Try once more."
        else:
            message = f"The correct answer is {self.solution}."
        self.feedback.configure(
            text=message,
            foreground=GREEN if correct else "#9B4B24"
        )
        return correct

    def submit(self):
        if self.state != "answer":
            return
        try:
            answer = int(self.entry.get().strip())
        except ValueError:
            self.feedback.configure(
                text="Enter a whole number, such as 12 or -5.",
                foreground="#9B4B24"
            )
            return

        self.answers.append(answer)
        correct = self.isCorrect(answer)
        if not correct and self.attempt == 1:
            self.attempt = 2
            self.entry.delete(0, "end")
            self.entry.focus_set()
            return

        points = (10 if self.attempt == 1 else 5) if correct else 0
        self.score += points
        self.records.append((
            self.problem,
            ", ".join(map(str, self.answers)),
            self.solution,
            points
        ))
        self.state = "next"
        self.entry.state(["disabled"])
        self.progress.configure(value=self.number)
        self.status.configure(
            text=f"Question {self.number} of 10"
                 f"   ·   Score {self.score}/100"
        )
        self.action.configure(
            text="View results" if self.number == 10 else "Next question",
            command=self.nextQuestion
        )
        self.action.focus_set()

    def nextQuestion(self):
        if self.state != "next":
            return
        if self.number == 10:
            self.displayResults()
        else:
            self.displayProblem()

    def enter(self, event=None):
        if self.state == "answer":
            self.submit()
        elif self.state == "next":
            self.nextQuestion()
        return "break"

    def displayResults(self):
        elapsed = int(time.monotonic() - self.started)
        self.state = "results"
        self.clear()
        previous = self.best.get(self.level, -1)
        self.best[self.level] = max(previous, self.score)
        saved = True
        try:
            temporary = self.score_file.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.best), encoding="utf-8")
            temporary.replace(self.score_file)
        except OSError:
            saved = False

        self.label("SESSION COMPLETE", 10, GREEN, True)
        self.label(f"{self.score} / 100", 44, bold=True)
        first_try = sum(row[3] == 10 for row in self.records)
        self.label(
            f"Grade {grade(self.score)}   ·   "
            f"{first_try}/10 correct first try   ·   "
            f"{elapsed // 60}:{elapsed % 60:02d}",
            12, MUTED
        )
        if self.score > previous:
            self.label("Your best score at this level.", 12, GREEN, True)

        self.label("ANSWER REVIEW", 10, MUTED, True)
        columns = ("question", "attempts", "correct", "points")
        table = ttk.Treeview(
            self.frame, columns=columns, show="headings", height=10
        )
        for column, title, width in [
            ("question", "Question", 180),
            ("attempts", "Your attempts", 190),
            ("correct", "Correct", 110),
            ("points", "Points", 80)
        ]:
            table.heading(column, text=title)
            table.column(column, width=width, anchor="center")
        for record in self.records:
            table.insert("", "end", values=record)
        table.pack(fill="both", expand=True, pady=(0, 12))

        if not saved:
            self.label(
                "Your best score could not be saved on this computer.",
                10, MUTED
            )
        self.button("Play again", self.displayMenu, primary=True)
        self.button("Close", self.root.destroy)


if __name__ == "__main__":
    window = tk.Tk()
    MathsQuiz(window)
    window.mainloop()