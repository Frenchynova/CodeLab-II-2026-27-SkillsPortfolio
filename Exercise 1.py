import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import time
from pathlib import Path

BG, WHITE, INK, GREEN = "#F4F3EF", "#FFFFFF", "#24352E", "#276B50"
MUTED, RED = "#728077", "#A34F38"
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


class MathsQuiz:
    def __init__(self, root):
        self.root, self.page, self.timer = root, "home", None
        root.title("Maths Studio")
        root.geometry("1000x780")
        root.minsize(940, 740)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.history = []
        try:
            data = json.loads(FILE.read_text())
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
        style.configure("TProgressbar", background=GREEN, troughcolor="#DFE4DE")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        side = tk.Frame(root, bg=INK, width=190)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        self.label(side, "MATHS\nSTUDIO", 24, WHITE, True)
        self.button(side, "Practice", lambda: self.navigate(self.displayMenu))
        self.button(side, "History", lambda: self.navigate(self.showHistory))
        self.label(side, "10 questions\n2 chances\n100 points", 11, "#B9C8BE")
        self.main = tk.Frame(root, bg=BG, padx=28, pady=24)
        self.main.pack(fill="both", expand=True)
        self.displayMenu()

    def label(self, parent, text, size=11, color=INK, bold=False):
        widget = tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                          font=("Segoe UI", size, "bold" if bold else "normal"),
                          anchor="w", justify="left")
        widget.pack(fill="x", padx=12, pady=8)
        return widget

    def button(self, parent, text, command, primary=False):
        color = GREEN if primary else WHITE
        button = tk.Button(parent, text=text, command=command, bg=color,
                           fg=WHITE if primary else INK, relief="flat",
                           activebackground="#DCE7DF", activeforeground=INK,
                           font=("Segoe UI", 11, "bold"), pady=12,
                           cursor="hand2", highlightcolor=GREEN)
        button.pack(fill="x", padx=12, pady=6)
        button.bind("<Return>", lambda e: (button.invoke(), "break")[1])
        return button

    def clear(self, page):
        self.page = page
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        for widget in self.main.winfo_children():
            widget.destroy()

    def heading(self, title, subtitle):
        self.label(self.main, "MATHS STUDIO / " + self.page.upper(), 10, GREEN, True)
        self.label(self.main, title, 30, bold=True)
        self.label(self.main, subtitle, 11, MUTED)

    def best(self, level):
        return max((r["score"] for r in self.history if r["level"] == level),
                   default=None)

    def displayMenu(self):
        self.clear("home")
        self.heading("Make room for a little maths.",
                     f"{len(self.history)} saved sessions · Choose your difficulty")
        for level, (low, high) in LEVELS.items():
            best = self.best(level)
            record = "No score yet" if best is None else f"Best: {best}/100"
            self.button(self.main, f"{level}  ·  {low}–{high}  ·  {record}",
                        lambda chosen=level: self.start(chosen))
        self.label(self.main,
                   "\nFirst attempt: 10 points · Second attempt: 5 points\n\n"
                   "Addition and subtraction. Answers can be negative.\n\n"
                   "The timer measures practice time. There is no time limit.",
                   11, MUTED)

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
        self.heading(f"Question {self.number:02d} of 10", self.level)
        self.status = self.label(self.main, f"Score: {self.score}/100", 13, GREEN, True)
        self.progress = ttk.Progressbar(self.main, maximum=10, value=self.number - 1)
        self.progress.pack(fill="x", padx=12, pady=12)
        card = tk.Frame(self.main, bg=WHITE, padx=20, pady=18)
        card.pack(fill="x", padx=12, pady=12)
        self.label(card, "SOLVE THE EXPRESSION", 10, MUTED)
        self.label(card, self.problem + " = ?", 38, bold=True)
        self.label(card, "Your answer", 11, MUTED)
        self.entry = tk.Entry(card, font=("Segoe UI", 24), bg=BG, fg=INK,
                              relief="flat", highlightthickness=2,
                              highlightbackground="#DFE4DE", highlightcolor=GREEN)
        self.entry.pack(fill="x", padx=12, pady=10, ipady=10)
        self.entry.bind("<Return>", self.submit)
        self.feedback = self.label(card, "Attempt 1 of 2", 12, MUTED)
        self.action = self.button(self.main, "Check answer", self.submit, True)
        self.clock = self.label(self.main, "", 10, MUTED)
        self.label(self.main, "Press Enter to submit or continue.", 10, MUTED)
        self.entry.focus_set()
        self.tick()

    def tick(self):
        seconds = int(time.monotonic() - self.started)
        self.clock.config(text=f"Practice time  {seconds // 60:02d}:{seconds % 60:02d}")
        self.timer = self.root.after(1000, self.tick)

    def isCorrect(self, answer):
        correct = answer == self.solution
        points = 10 if self.attempt == 1 else 5
        message = (f"Correct. +{points} points." if correct else
                   "Not quite. One more try." if self.attempt == 1 else
                   f"The correct answer is {self.solution}.")
        self.feedback.config(text=message, fg=GREEN if correct else RED)
        return correct

    def submit(self, event=None):
        if not self.accepting:
            return "break"
        try:
            answer = int(self.entry.get().strip())
        except ValueError:
            self.feedback.config(text="Enter a whole number, such as 12 or -5.", fg=RED)
            return "break"
        self.answers.append(answer)
        correct = self.isCorrect(answer)
        if not correct and self.attempt == 1:
            self.attempt = 2
            self.entry.delete(0, "end")
            return "break"
        points = (10 if self.attempt == 1 else 5) if correct else 0
        self.score += points
        self.records.append((self.problem, ", ".join(map(str, self.answers)),
                             self.solution, points))
        self.accepting = False
        self.entry.config(state="disabled")
        self.status.config(text=f"Score: {self.score}/100")
        self.progress.config(value=self.number)
        self.action.config(text="View results" if self.number == 10 else "Next question",
                           command=self.displayResults if self.number == 10
                           else self.displayProblem)
        self.action.focus_set()
        return "break"

    def table(self, headings):
        frame = tk.Frame(self.main, bg=WHITE)
        frame.pack(fill="both", expand=True, padx=12, pady=8)
        table = ttk.Treeview(frame, columns=headings, show="headings", height=10)
        for heading in headings:
            table.heading(heading, text=heading)
            table.column(heading, width=145, minwidth=65, anchor="center")
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
        first = sum(row[3] == 10 for row in self.records)
        self.heading(f"{self.score} / 100",
                     f"Grade {grade(self.score)} · {first}/10 correct first try · "
                     f"{seconds // 60}:{seconds % 60:02d}")
        if previous is None or self.score > previous:
            self.label(self.main, "Your best score at this level.", 12, GREEN, True)
        missed = tk.BooleanVar(value=False)
        table = self.table(("Question", "Your attempts", "Correct", "Points"))

        def refresh():
            for item in table.get_children():
                table.delete(item)
            for row in self.records:
                if not missed.get() or row[3] == 0:
                    table.insert("", "end", values=row)

        tk.Checkbutton(self.main, text="Only missed questions (0 points)",
                       variable=missed, command=refresh, bg=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=12)
        refresh()
        if not saved:
            self.label(self.main, "This session could not be saved.", 10, RED)
        self.button(self.main, "Practice again", self.displayMenu, True)

    def showHistory(self):
        self.clear("history")
        self.heading("Every session counts.", "Latest 50 completed sessions, newest first.")
        if not self.history:
            self.label(self.main, "Complete a quiz to see your progress here.", 12, MUTED)
            return
        table = self.table(("Completed", "Level", "Score", "Time"))
        for row in reversed(self.history):
            seconds = row["seconds"]
            table.insert("", "end", values=(
                row["date"], row["level"], f'{row["score"]}/100',
                f"{seconds // 60}:{seconds % 60:02d}"))

    def navigate(self, destination):
        if self.page != "quiz" or messagebox.askyesno(
            "Leave session?", "Your current quiz will end without saving a score.",
            parent=self.root
        ):
            destination()

    def close(self):
        self.navigate(self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    MathsQuiz(root)
    root.mainloop()