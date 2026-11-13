import tkinter as tk
from tkinter import messagebox
import random

# Appearance
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
    "Advanced": (1000, 9999),
}


class MathsStudio:
    def __init__(self, root):
        self.root = root
        self.playing = False
        self.level = tk.StringVar(value="Easy")
        self.mode = tk.StringVar(value="Mixed")
        self.best = {}

        root.title("Maths Studio")
        root.geometry("900x790")
        root.minsize(820, 750)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)

        header = tk.Frame(root, bg=INK, padx=32, pady=20)
        header.pack(fill="x")
        self.label(header, "MATHS QUIZ", 22, CARD, True).pack(side="left")
        self.label(header, "A PLACE TO PRACTISE", 10, "#BBCBBF").pack(
            side="right"
        )

        self.body = tk.Frame(root, bg=BG, padx=36, pady=24)
        self.body.pack(fill="both", expand=True)
        self.home()

    # Small helpers keep the screen code readable.
    def label(self, parent, text, size=12, color=INK, bold=False):
        return tk.Label(
            parent, text=text, bg=parent["bg"], fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            justify="left", anchor="w",
        )

    def button(self, parent, text, command, primary=True):
        normal = GREEN if primary else PALE
        hover = HOVER if primary else "#D8E5DA"
        foreground = CARD if primary else INK

        button = tk.Button(
            parent, text=text, command=command,
            bg=normal, fg=foreground,
            activebackground=hover, activeforeground=foreground,
            relief="flat", bd=0, padx=22, pady=13,
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            highlightthickness=2, highlightbackground=normal,
            highlightcolor="#90B49C",
        )
        button.bind("<Enter>", lambda event: button.config(bg=hover))
        button.bind("<Leave>", lambda event: button.config(bg=normal))
        button.bind(
            "<Return>", lambda event: (button.invoke(), "break")[1]
        )
        return button

    def card(self, parent):
        return tk.Frame(
            parent, bg=CARD, padx=26, pady=24,
            highlightbackground=LINE, highlightthickness=1,
        )

    def clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def heading(self, title, subtitle):
        self.label(self.body, title, 29, bold=True).pack(anchor="w")
        self.label(self.body, subtitle, 12, MUTED).pack(
            anchor="w", pady=(8, 24)
        )

    def choices(self, parent, variable, values):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=(10, 20))

        for value in values:
            tk.Radiobutton(
                row, text=value, value=value, variable=variable,
                indicatoron=False, bg=BG, fg=INK,
                selectcolor=PALE, activebackground=PALE,
                activeforeground=INK, relief="flat",
                offrelief="flat", overrelief="flat",
                borderwidth=0, padx=12, pady=13,
                font=("Segoe UI", 12), cursor="hand2",
                highlightthickness=1, highlightbackground=LINE,
                highlightcolor=GREEN,
            ).pack(side="left", fill="x", expand=True, padx=3)

    def home(self):
        self.playing = False
        self.clear()
        self.heading(
            "A little maths. A little progress.",
            "Choose your practice, then take it one question at a time.",
        )

        card = self.card(self.body)
        card.pack(fill="x")

        self.label(card, "YOUR SESSION", 10, GREEN, True).pack(anchor="w")
        self.label(card, "Difficulty", 15, bold=True).pack(
            anchor="w", pady=(18, 0)
        )
        self.choices(card, self.level, list(LEVELS))

        self.label(card, "Operation", 15, bold=True).pack(anchor="w")
        self.choices(
            card, self.mode, ["Addition", "Subtraction", "Mixed"]
        )

        self.label(
            card,
            "Easy: single digits    /    Moderate: two digits"
            "    /    Advanced: four digits",
            10, MUTED,
        ).pack(anchor="w", pady=(0, 16))

        self.button(card, "Start practice  →", self.start).pack(fill="x")

        self.label(
            self.body,
            "10 questions  ·  Two attempts  ·  No time limit",
            12, GREEN, True,
        ).pack(anchor="w", pady=(24, 8))
        self.label(
            self.body,
            "Earn 10 points on your first try, or 5 on your second.\n"
            "Subtraction can have a negative answer.",
            11, MUTED,
        ).pack(anchor="w")

    def start(self):
        operations = {
            "Addition": ["+"],
            "Subtraction": ["−"],
            "Mixed": ["+", "−"],
        }
        questions = []
        seen = set()

        while len(questions) < 10:
            a = random.randint(*LEVELS[self.level.get()])
            b = random.randint(*LEVELS[self.level.get()])
            op = random.choice(operations[self.mode.get()])
            question = (a, b, op)
            if question not in seen:
                seen.add(question)
                questions.append(question)

        self.begin(questions, review=False)

    def begin(self, questions, review):
        self.questions = questions
        self.review = review
        self.records = []
        self.score = 0
        self.playing = True
        self.show_question()

    def show_question(self):
        if len(self.records) == len(self.questions):
            self.results()
            return

        self.clear()
        self.answered = False
        self.attempts = []
        self.question = self.questions[len(self.records)]
        a, b, op = self.question
        self.problem = f"{a} {op} {b}"
        self.solution = a + b if op == "+" else a - b
        total = len(self.questions)

        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x", pady=(0, 14))
        self.label(
            top, "REVIEW PRACTICE" if self.review
            else f"{self.level.get().upper()} / {self.mode.get().upper()}",
            10, GREEN, True,
        ).pack(side="left")
        self.score_label = self.label(
            top, f"{self.score} / {total * 10} points", 12, bold=True
        )
        self.score_label.pack(side="right")

        # Individual segments show completed questions.
        self.segments = []
        progress = tk.Frame(self.body, bg=BG)
        progress.pack(fill="x", pady=(0, 24))
        for index in range(total):
            segment = tk.Frame(
                progress, bg=GREEN if index < len(self.records) else LINE,
                height=5,
            )
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
            card, width=17, justify="center",
            font=("Segoe UI", 27), bg=BG, fg=INK,
            insertbackground=GREEN, relief="flat",
            highlightthickness=2, highlightbackground=LINE,
            highlightcolor=GREEN,
        )
        self.entry.pack(ipady=12, pady=(10, 0))
        self.entry.bind("<Return>", self.check)

        self.feedback = self.label(
            card, "First attempt · 10 points available", 12, MUTED
        )
        self.feedback.pack(pady=(22, 4))

        self.action = self.button(self.body, "Check answer", self.check)
        self.action.pack(fill="x", pady=(18, 12))

        bottom = tk.Frame(self.body, bg=BG)
        bottom.pack(fill="x")
        self.label(bottom, "Press Enter to check or continue", 10, MUTED).pack(
            side="left"
        )
        self.button(
            bottom, "End session", self.leave, primary=False
        ).pack(side="right")
        self.entry.focus_set()

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
        correct = answer == self.solution

        if not correct and len(self.attempts) == 1:
            self.feedback.config(
                text="Not quite. Try again for 5 points.", fg=RED
            )
            self.entry.selection_range(0, "end")
            self.entry.focus_set()
            return "break"

        points = (10 if len(self.attempts) == 1 else 5) if correct else 0
        self.score += points
        self.records.append({
            "question": self.question,
            "problem": self.problem,
            "solution": self.solution,
            "attempts": self.attempts[:],
            "points": points,
        })
        self.answered = True
        self.entry.config(state="disabled")
        self.feedback.config(
            text=f"Correct. You earned {points} points." if correct
            else f"The answer is {self.solution}.",
            fg=GREEN if correct else RED,
        )
        self.score_label.config(
            text=f"{self.score} / {len(self.questions) * 10} points"
        )
        self.segments[len(self.records) - 1].config(bg=GREEN if correct else RED)
        self.action.config(
            text="View results  →" if len(self.records) == len(self.questions)
            else "Next question  →",
            command=self.show_question,
        )
        self.action.focus_set()
        return "break"

    def results(self):
        self.playing = False
        self.clear()
        self.heading(
            "Practice complete.",
            "Here’s how you did. Revisit anything that needs another try.",
        )
        total = len(self.questions)
        first = sum(record["points"] == 10 for record in self.records)
        difficult = [
            record["question"] for record in self.records
            if record["points"] < 10
        ]

        summary = self.card(self.body)
        summary.pack(fill="x")
        self.label(
            summary, f"{self.score} / {total * 10}", 40, GREEN, True
        ).pack(side="left")
        self.label(
            summary, f"{first} of {total}\ncorrect on the first try",
            12, MUTED,
        ).pack(side="right")

        if not self.review:
            key = (self.level.get(), self.mode.get())
            previous = self.best.get(key, -1)
            self.best[key] = max(previous, self.score)
            text = "New personal best for these settings." if self.score > previous \
                else f"Personal best for these settings: {previous}/100"
            self.label(self.body, text, 11, GREEN).pack(
                anchor="w", pady=(12, 0)
            )

        self.label(self.body, "Answer review", 16, bold=True).pack(
            anchor="w", pady=(18, 10)
        )

        # A simple scrollable review using standard Tkinter.
        review = tk.Frame(self.body, bg=CARD)
        review.pack(fill="both", expand=True, pady=(0, 18))
        scroll = tk.Scrollbar(review)
        scroll.pack(side="right", fill="y")
        text = tk.Text(
            review, height=6, bg=CARD, fg=INK,
            font=("Segoe UI", 12), relief="flat", bd=0,
            padx=18, pady=12, wrap="word",
            yscrollcommand=scroll.set,
        )
        text.pack(fill="both", expand=True)
        scroll.config(command=text.yview)
        text.tag_configure("good", foreground=GREEN)
        text.tag_configure("retry", foreground=RED)
        text.tag_configure("muted", foreground=MUTED)

        for record in self.records:
            tag = "good" if record["points"] == 10 else "retry"
            text.insert(
                "end",
                f'{record["problem"]} = {record["solution"]}'
                f'     +{record["points"]} points\n',
                tag,
            )
            text.insert(
                "end",
                "Your answers: " + ", ".join(map(str, record["attempts"]))
                + "\n\n",
                "muted",
            )
        text.config(state="disabled")

        actions = tk.Frame(self.body, bg=BG)
        actions.pack(fill="x")
        self.button(actions, "New session", self.home, False).pack(side="left")
        if difficult:
            self.button(
                actions, f"Retry {len(difficult)} difficult questions  →",
                lambda: self.begin(difficult, review=True),
            ).pack(side="right")

    def leave(self):
        if len(self.records) == len(self.questions):
            self.results()
        elif messagebox.askyesno(
            "End session?", "Leave this unfinished session?", parent=self.root
        ):
            self.home()

    def close(self):
        if not self.playing or len(self.records) == len(self.questions):
            self.root.destroy()
        elif messagebox.askyesno(
            "Close Maths Studio?", "Leave this unfinished session?",
            parent=self.root,
        ):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    MathsStudio(root)
    root.mainloop()