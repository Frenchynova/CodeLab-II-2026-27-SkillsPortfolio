import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import random
import math

# Colours
BG = "#F4F5F0"
CARD = "#FFFFFF"
INK = "#243C32"
MUTED = "#758078"
GREEN = "#326B50"
HOVER = "#285840"
PALE = "#E7EFE8"
LINE = "#DCE3DC"
RED = "#AD4940"

LEVELS = {
    "Easy": (0, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999)
}

LOGO_FILE = Path(__file__).resolve().parent / "maths_studio_logo.png"


def randomInt(level):
    minimum, maximum = LEVELS[level]
    return random.randint(minimum, maximum)


def decideOperation(mode="Mixed"):
    if mode == "Addition":
        return "+"
    if mode == "Subtraction":
        return "−"
    return random.choice(["+", "−"])


def getGrade(percentage):
    if percentage > 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    return "F"


class MathsStudio:
    def __init__(self, root):
        self.root = root
        self.playing = False
        self.level = tk.StringVar(value="Easy")
        self.mode = tk.StringVar(value="Mixed")
        self.best = {}

        root.title("Maths Studio")
        root.geometry("920x830")
        root.minsize(820, 780)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)

        header = tk.Frame(root, bg=INK, padx=32, pady=16)
        header.pack(fill="x")

        self.logo_label = tk.Label(header, bg=INK)
        self.logo_label.pack(side="left", padx=(0, 16))
        self.loadLogo()

        self.label(header, "MATHS QUIZ", 22, CARD, True).pack(side="left")
        self.label(
            header, "A PLACE TO PRACTISE", 10, "#BBCBBF"
        ).pack(side="right")

        self.body = tk.Frame(root, bg=BG, padx=36, pady=24)
        self.body.pack(fill="both", expand=True)
        self.displayMenu()

    # ---------- Reusable design helpers ----------

    def label(self, parent, text, size=12, color=INK, bold=False,
              wraplength=0):
        weight = "bold" if bold else "normal"

        return tk.Label(
            parent, text=text, bg=parent["bg"], fg=color,
            font=("Segoe UI", size, weight),
            justify="left", anchor="w", wraplength=wraplength
        )

    def button(self, parent, text, command, primary=True):
        if primary:
            normal, hover, foreground = GREEN, HOVER, CARD
        else:
            normal, hover, foreground = PALE, "#D8E5DA", INK

        button = tk.Button(
            parent, text=text, command=command,
            bg=normal, fg=foreground,
            activebackground=hover, activeforeground=foreground,
            relief="flat", bd=0, padx=22, pady=13,
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            highlightthickness=2, highlightbackground=normal,
            highlightcolor="#90B49C"
        )

        button.bind("<Enter>", lambda event: button.config(bg=hover))
        button.bind("<Leave>", lambda event: button.config(bg=normal))

        def activate(event):
            button.invoke()
            return "break"

        button.bind("<Return>", activate)
        return button

    def card(self, parent):
        return tk.Frame(
            parent, bg=CARD, padx=26, pady=24,
            highlightbackground=LINE, highlightthickness=1
        )

    def clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def heading(self, title, subtitle):
        self.label(self.body, title, 29, bold=True).pack(anchor="w")
        self.label(
            self.body, subtitle, 12, MUTED, wraplength=730
        ).pack(anchor="w", pady=(8, 24))

    def choices(self, parent, variable, values):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=(10, 20))

        for value in values:
            tk.Radiobutton(
                row, text=value, value=value, variable=variable,
                indicatoron=False, bg=BG, fg=INK, selectcolor=PALE,
                activebackground=PALE, activeforeground=INK,
                relief="flat", offrelief="flat", overrelief="flat",
                borderwidth=0, padx=12, pady=13,
                font=("Segoe UI", 12), cursor="hand2",
                highlightthickness=1, highlightbackground=LINE,
                highlightcolor=GREEN
            ).pack(side="left", fill="x", expand=True, padx=3)

    def loadLogo(self):
        try:
            original = tk.PhotoImage(master=self.root, file=str(LOGO_FILE))
            size = max(original.width(), original.height())

            if original.width() == 0 or original.height() == 0:
                raise ValueError("Empty image")

            scale = max(1, math.ceil(size / 54))
            self.logo = original.subsample(scale)
            self.logo_label.config(image=self.logo)

        except (tk.TclError, OSError, ValueError):
            self.logo_label.config(
                text="M+", font=("Segoe UI", 24, "bold"),
                fg="#BBCBBF", bg=INK
            )
            return

        try:
            self.root.iconphoto(True, self.logo)
        except tk.TclError:
            pass

    # ---------- Home screen ----------

    def displayMenu(self):
        self.playing = False
        self.clear()

        self.heading(
            "A little maths. A little progress.",
            "Choose your practice, then take it one question at a time."
        )

        card = self.card(self.body)
        card.pack(fill="x")

        self.label(card, "YOUR SESSION", 10, GREEN, True).pack(anchor="w")
        self.label(card, "Difficulty", 15, bold=True).pack(
            anchor="w", pady=(18, 0)
        )
        self.choices(card, self.level, list(LEVELS))

        self.label(card, "Operation", 15, bold=True).pack(anchor="w")
        self.choices(card, self.mode, ["Addition", "Subtraction", "Mixed"])

        self.label(
            card,
            "Easy: single digits / Moderate: two digits / Advanced: four digits",
            10, MUTED, wraplength=650
        ).pack(anchor="w", pady=(0, 16))

        self.button(card, "Start practice  →", self.start).pack(fill="x")

        self.label(
            self.body, "10 questions  ·  Two attempts  ·  No time limit",
            12, GREEN, True
        ).pack(anchor="w", pady=(24, 8))

        self.label(
            self.body,
            "Earn 10 points on your first try, or 5 on your second.\n"
            "Subtraction can have a negative answer.\n"
            "Choose Mixed for the assignment's random operations.",
            11, MUTED
        ).pack(anchor="w")

    # ---------- Create the questions ----------

    def start(self):
        self.session_level = self.level.get()
        self.session_mode = self.mode.get()
        questions = []

        while len(questions) < 10:
            a = randomInt(self.session_level)
            b = randomInt(self.session_level)
            operation = decideOperation(self.session_mode)
            question = (a, b, operation)

            if question not in questions:
                questions.append(question)

        self.begin(questions)

    def begin(self, questions, review=False):
        self.questions = questions
        self.review = review
        self.records = []
        self.score = 0
        self.playing = True
        self.displayProblem()

    # ---------- Question screen ----------

    def displayProblem(self):
        if len(self.records) == len(self.questions):
            self.displayResults()
            return

        self.clear()
        self.answered = False
        self.attempts = []

        self.question = self.questions[len(self.records)]
        a, b, operation = self.question
        self.problem = f"{a} {operation} {b}"

        if operation == "+":
            self.solution = a + b
        else:
            self.solution = a - b

        total = len(self.questions)

        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x", pady=(0, 14))

        if self.review:
            title = "REVIEW PRACTICE"
        else:
            title = f"{self.session_level.upper()} / {self.session_mode.upper()}"

        self.label(top, title, 10, GREEN, True).pack(side="left")
        self.score_label = self.label(
            top, f"{self.score} / {total * 10} points", 12, bold=True
        )
        self.score_label.pack(side="right")

        progress = tk.Frame(self.body, bg=BG)
        progress.pack(fill="x", pady=(0, 24))
        self.segments = []

        for index in range(total):
            color = LINE

            if index < len(self.records):
                if self.records[index]["points"] > 0:
                    color = GREEN
                else:
                    color = RED

            segment = tk.Frame(progress, bg=color, height=5)
            segment.pack(side="left", fill="x", expand=True, padx=2)
            self.segments.append(segment)

        card = self.card(self.body)
        card.pack(fill="x")

        self.label(
            card, f"Question {len(self.records) + 1} of {total}", 12, MUTED
        ).pack(anchor="center")

        self.label(card, self.problem, 48, bold=True).pack(pady=(20, 24))
        self.label(card, "YOUR ANSWER", 10, MUTED, True).pack()

        self.entry = tk.Entry(
            card, width=17, justify="center", font=("Segoe UI", 27),
            bg=BG, fg=INK, insertbackground=GREEN, relief="flat",
            highlightthickness=2, highlightbackground=LINE,
            highlightcolor=GREEN
        )
        self.entry.pack(ipady=12, pady=(10, 0))
        self.entry.bind("<Return>", self.check)

        self.feedback = self.label(
            card, "First attempt · 10 points available",
            12, MUTED, wraplength=650
        )
        self.feedback.pack(pady=(22, 4))

        self.action = self.button(self.body, "Check answer", self.check)
        self.action.pack(fill="x", pady=(18, 12))

        bottom = tk.Frame(self.body, bg=BG)
        bottom.pack(fill="x")

        self.label(
            bottom, "Press Enter to check or continue", 10, MUTED
        ).pack(side="left")

        self.button(
            bottom, "End session", self.leave, primary=False
        ).pack(side="right")

        self.entry.focus_set()

    # ---------- Check the answer ----------

    def isCorrect(self, answer):
        return answer == self.solution

    def check(self, event=None):
        if self.answered:
            return "break"

        raw = self.entry.get().strip()

        try:
            if len(raw) > 12:
                raise ValueError
            answer = int(raw)
        except ValueError:
            self.feedback.config(
                text="Enter a whole number, such as 12 or -5.", fg=RED
            )
            return "break"

        self.attempts.append(answer)
        correct = self.isCorrect(answer)

        if not correct and len(self.attempts) == 1:
            self.feedback.config(
                text="Not quite. Try again for 5 points.", fg=RED
            )
            self.entry.selection_range(0, "end")
            self.entry.focus_set()
            return "break"

        # First correct attempt earns 10; second earns 5.
        points = 0
        if correct:
            if len(self.attempts) == 1:
                points = 10
            else:
                points = 5

        self.score += points
        self.records.append({
            "question": self.question,
            "problem": self.problem,
            "solution": self.solution,
            "attempts": self.attempts.copy(),
            "points": points
        })

        self.answered = True
        self.entry.config(state="disabled")

        if correct:
            message = f"Correct. You earned {points} points."
            color = GREEN
        else:
            message = f"The answer is {self.solution}."
            color = RED

        self.feedback.config(text=message, fg=color)
        self.score_label.config(
            text=f"{self.score} / {len(self.questions) * 10} points"
        )
        self.segments[len(self.records) - 1].config(bg=color)

        if len(self.records) == len(self.questions):
            next_text = "View results  →"
        else:
            next_text = "Next question  →"

        self.action.config(text=next_text, command=self.displayProblem)
        self.action.focus_set()
        return "break"

    # ---------- Results screen ----------

    def displayResults(self):
        self.playing = False
        self.clear()

        self.heading(
            "Practice complete.",
            "Here's how you did. Revisit anything that needs another try."
        )

        total = len(self.questions)
        maximum = total * 10
        percentage = self.score / maximum * 100
        first = 0
        difficult = []

        for record in self.records:
            if record["points"] == 10:
                first += 1
            else:
                difficult.append(record["question"])

        summary = self.card(self.body)
        summary.pack(fill="x")

        score_group = tk.Frame(summary, bg=CARD)
        score_group.pack(side="left")

        self.label(
            score_group, f"{self.score} / {maximum}", 36, GREEN, True
        ).pack(anchor="w")
        self.label(
            score_group, f"Grade: {getGrade(percentage)}", 13, GREEN, True
        ).pack(anchor="w", pady=(5, 0))

        self.label(
            summary, f"{first} of {total}\ncorrect on the first try",
            12, MUTED
        ).pack(side="right")

        if not self.review:
            key = (self.session_level, self.session_mode)
            previous = self.best.get(key, -1)

            if self.score > previous:
                self.best[key] = self.score
                best_text = "New best for these settings during this app session."
            else:
                best_text = f"Best during this app session: {previous}/100"

            self.label(self.body, best_text, 10, GREEN).pack(
                anchor="w", pady=(12, 0)
            )

        self.label(self.body, "Answer review", 16, bold=True).pack(
            anchor="w", pady=(18, 10)
        )

        review_frame = tk.Frame(self.body, bg=CARD)
        review_frame.pack(fill="both", expand=True, pady=(0, 18))

        scrollbar = tk.Scrollbar(review_frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            review_frame, height=6, bg=CARD, fg=INK,
            font=("Segoe UI", 12), relief="flat", bd=0,
            padx=18, pady=12, wrap="word",
            yscrollcommand=scrollbar.set
        )
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        text.tag_configure("good", foreground=GREEN)
        text.tag_configure("retry", foreground=RED)
        text.tag_configure("muted", foreground=MUTED)

        for record in self.records:
            if record["points"] == 10:
                tag = "good"
            else:
                tag = "retry"

            answers = []
            for answer in record["attempts"]:
                answers.append(str(answer))

            text.insert(
                "end",
                f'{record["problem"]} = {record["solution"]}'
                f'     +{record["points"]} points\n',
                tag
            )
            text.insert(
                "end", "Your answers: " + ", ".join(answers) + "\n\n",
                "muted"
            )

        text.config(state="disabled")

        actions = tk.Frame(self.body, bg=BG)
        actions.pack(fill="x")

        self.button(
            actions, "New session", self.displayMenu, primary=False
        ).pack(side="left")

        if difficult:
            self.button(
                actions,
                f"Retry {len(difficult)} difficult questions  →",
                lambda: self.begin(difficult, review=True)
            ).pack(side="right")

    # ---------- End or close the session ----------

    def leave(self):
        if len(self.records) == len(self.questions):
            self.displayResults()
        elif messagebox.askyesno(
            "End session?", "Leave this unfinished session?",
            parent=self.root
        ):
            self.displayMenu()

    def close(self):
        if self.playing and len(self.records) < len(self.questions):
            confirmed = messagebox.askyesno(
                "Close Maths Studio?", "Leave this unfinished session?",
                parent=self.root
            )
            if not confirmed:
                return

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    MathsStudio(root)
    root.mainloop()