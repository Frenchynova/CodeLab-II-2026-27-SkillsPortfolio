import json
import random
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox


BG = "#F2F4F3"
WHITE = "#FFFFFF"
INK = "#20332F"
MUTED = "#6E7D77"
TEAL = "#207568"
LINE = "#DCE4DF"
RED = "#AE473F"

# Stored beside the script, making the app easy to move.
DATA_FILE = Path(__file__).resolve().with_name("maths_studio_data.json")

LEVELS = {
    "Easy": (0, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999),
}
OPERATIONS = {
    "Addition": ("+",),
    "Subtraction": ("−",),
    "Multiplication": ("×",),
    "Division": ("÷",),
    "Mixed": ("+", "−", "×", "÷"),
}


def make_question(level, operation, negatives):
    op = random.choice(OPERATIONS[operation])
    low, high = LEVELS[level]
    a, b = random.randint(low, high), random.randint(low, high)

    # Keep multiplication and division practical for mental maths.
    if op in ("×", "÷"):
        limits = {
            "Easy": ((1, 10), (1, 10)),
            "Moderate": ((2, 12), (2, 12)),
            "Advanced": ((12, 99), (2, 12)),
        }
        left, right = limits[level]
        a, b = random.randint(*left), random.randint(*right)

    if op == "+":
        answer = a + b
    elif op == "−":
        if not negatives:
            a, b = max(a, b), min(a, b)
        answer = a - b
    elif op == "×":
        answer = a * b
    else:
        # Construct divisions with exact whole-number answers.
        answer = a
        a *= b

    return {"a": a, "b": b, "op": op, "answer": answer}


def expression(q):
    return f'{q["a"]} {q["op"]} {q["b"]}'


def duration(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class MathsStudio:
    def __init__(self, root):
        self.root = root
        self.page = ""
        self.timer = None
        self.history = []
        self.settings = {}
        self.load()

        root.title("Maths Studio")
        root.geometry("1000x800")
        root.minsize(900, 740)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(
            "TCombobox", padding=7, font=("Segoe UI", 11)
        )
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=LINE,
            background=TEAL,
            borderwidth=0,
            lightcolor=TEAL,
            darkcolor=TEAL,
        )
        style.configure(
            "Treeview", background=WHITE, fieldbackground=WHITE,
            foreground=INK, rowheight=35, borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading", background=BG, foreground=INK,
            font=("Segoe UI", 10, "bold"), padding=9,
        )
        style.map("Treeview", background=[("selected", TEAL)],
                  foreground=[("selected", WHITE)])

        header = tk.Frame(root, bg=INK, padx=30, pady=15)
        header.pack(fill="x")
        self.label(header, "maths studio", 20, WHITE, True).pack(side="left")
        self.button(header, "History",
                    lambda: self.navigate(self.show_history)).pack(side="right")
        self.button(header, "Practice",
                    lambda: self.navigate(self.home)).pack(side="right", padx=8)

        self.main = tk.Frame(root, bg=BG, padx=32, pady=24)
        self.main.pack(fill="both", expand=True)
        self.home()

    def load(self):
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return
            settings = data.get("settings", {})
            if isinstance(settings, dict):
                self.settings = settings
            rows = data.get("history", [])
            if isinstance(rows, list):
                self.history = [
                    r for r in rows
                    if isinstance(r, dict)
                    and r.get("level") in LEVELS
                    and r.get("operation") in OPERATIONS
                    and type(r.get("count")) is int
                    and 1 <= r["count"] <= 20
                    and type(r.get("score")) is int
                    and 0 <= r["score"] <= r["count"] * 10
                    and type(r.get("seconds")) is int
                    and r["seconds"] >= 0
                    and isinstance(r.get("date"), str)
                    and type(r.get("negatives")) is bool
                ][-100:]
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            temporary = DATA_FILE.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(
                    {"settings": self.settings, "history": self.history},
                    indent=2,
                ),
                encoding="utf-8",
            )
            temporary.replace(DATA_FILE)
            return True
        except OSError:
            return False

    def label(self, parent, text, size=11, color=INK, bold=False):
        return tk.Label(
            parent, text=text, bg=parent["bg"], fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            anchor="w", justify="left",
        )

    def button(self, parent, text, command, primary=False):
        bg, fg = (TEAL, WHITE) if primary else (WHITE, INK)
        button = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground="#DDEAE5" if not primary else "#185C52",
            activeforeground=fg, relief="flat", bd=0,
            font=("Segoe UI", 11, "bold"), padx=18, pady=11,
            cursor="hand2", highlightthickness=2,
            highlightbackground=bg, highlightcolor="#7BA99B",
        )
        button.bind("<Return>", lambda event: (button.invoke(), "break")[1])
        return button

    def card(self, parent):
        return tk.Frame(
            parent, bg=WHITE, padx=24, pady=22,
            highlightbackground=LINE, highlightthickness=1,
        )

    def clear(self, page):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.page = page
        for child in self.main.winfo_children():
            child.destroy()

    def heading(self, title, subtitle):
        self.label(self.main, title, 28, bold=True).pack(anchor="w")
        self.label(self.main, subtitle, 11, MUTED).pack(
            anchor="w", pady=(8, 22)
        )

    def home(self):
        self.clear("home")
        self.heading("A little practice goes a long way.",
                     "Set up a session and work at your own pace.")

        card = self.card(self.main)
        card.pack(fill="x")
        self.label(card, "Your session", 18, bold=True).pack(anchor="w")

        fields = tk.Frame(card, bg=WHITE)
        fields.pack(fill="x", pady=20)
        self.level_var = tk.StringVar()
        self.operation_var = tk.StringVar()
        self.count_var = tk.StringVar()

        options = [
            ("Difficulty", self.level_var, list(LEVELS), "level", "Easy"),
            ("Questions", self.count_var, ["5", "10", "20"], "count", "10"),
            ("Operation", self.operation_var,
             list(OPERATIONS), "operation", "Mixed"),
        ]
        for column, (title, var, values, key, default) in enumerate(options):
            fields.columnconfigure(column, weight=1, uniform="fields")
            frame = tk.Frame(fields, bg=WHITE)
            frame.grid(row=0, column=column, sticky="ew", padx=(0, 15))
            self.label(frame, title, 10, MUTED, True).pack(anchor="w", pady=(0, 8))
            saved = str(self.settings.get(key, default))
            var.set(saved if saved in values else default)
            ttk.Combobox(frame, textvariable=var, values=values,
                         state="readonly", width=18).pack(fill="x")

        self.negative_var = tk.BooleanVar(
            value=self.settings.get("negatives") is True
        )
        tk.Checkbutton(
            card, text="Allow negative subtraction answers",
            variable=self.negative_var, bg=WHITE, fg=INK,
            activebackground=WHITE, selectcolor=WHITE,
            font=("Segoe UI", 11),
        ).pack(anchor="w")
        self.label(
            card,
            "Addition / subtraction: 1, 2 or 4 digits by level.\n"
            "Multiplication / division: times tables, then larger numbers.\n"
            "All answers are whole numbers.",
            10, MUTED,
        ).pack(anchor="w", pady=15)
        self.button(card, "Start session  →", self.start, True).pack(anchor="w")

        note = self.card(self.main)
        note.pack(fill="x", pady=18)
        self.label(note, "Two chances per question", 14, bold=True).pack(anchor="w")
        self.label(
            note,
            "First try: 10 points. Second try: 5 points.\n"
            "There’s no time limit. Review difficult questions when you finish.",
            11, MUTED,
        ).pack(anchor="w", pady=(8, 0))
        self.label(
            self.main, f"{len(self.history)} completed sessions saved",
            10, MUTED,
        ).pack(anchor="w")

    def start(self):
        self.settings = {
            "level": self.level_var.get(),
            "operation": self.operation_var.get(),
            "count": int(self.count_var.get()),
            "negatives": self.negative_var.get(),
        }
        questions, seen = [], set()
        for _ in range(self.settings["count"]):
            for attempt in range(100):
                q = make_question(
                    self.settings["level"], self.settings["operation"],
                    self.settings["negatives"],
                )
                key = expression(q)
                if key not in seen:
                    break
            seen.add(key)
            questions.append(q)
        self.begin(questions, retry=False)

    def begin(self, questions, retry):
        self.questions = questions
        self.retry = retry
        self.records = []
        self.score = 0
        self.index = 0
        self.started = time.monotonic()
        self.finished = False
        self.show_question()

    def show_question(self):
        self.clear("quiz")
        self.attempts = []
        self.accepting = True
        q = self.questions[self.index]
        total = len(self.questions)
        self.heading(
            f"Question {self.index + 1} of {total}",
            "Review practice" if self.retry else
            f'{self.settings["level"]} · {self.settings["operation"]}',
        )

        bar = tk.Frame(self.main, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.score_label = self.label(bar, f"Score  {self.score}/{total * 10}", bold=True)
        self.score_label.pack(side="left")
        self.clock = self.label(bar, "", color=MUTED)
        self.clock.pack(side="right")
        self.progress = ttk.Progressbar(
            self.main, maximum=total, value=self.index
        )
        self.progress.pack(fill="x", pady=(0, 20))

        card = self.card(self.main)
        card.pack(fill="x")
        self.label(card, "Work out the answer", 11, MUTED).pack(anchor="center")
        self.label(card, expression(q) + " = ?", 38, bold=True).pack(pady=20)

        self.entry = tk.Entry(
            card, width=18, justify="center", font=("Segoe UI", 26),
            bg=BG, fg=INK, relief="flat", insertbackground=TEAL,
            highlightthickness=2, highlightbackground=LINE,
            highlightcolor=TEAL,
        )
        self.entry.pack(ipady=10)
        self.entry.bind("<Return>", self.submit)
        self.feedback = self.label(card, "First attempt · 10 points available", 11, MUTED)
        self.feedback.pack(pady=(20, 8))
        self.action = self.button(self.main, "Check answer", self.submit, True)
        self.action.pack(fill="x", pady=18)
        self.label(self.main, "Press Enter to check or continue.", 10, MUTED).pack()
        self.entry.focus_set()
        self.tick()

    def tick(self):
        self.clock.config(text=duration(time.monotonic() - self.started))
        self.timer = self.root.after(1000, self.tick)

    def submit(self, event=None):
        if not self.accepting:
            return "break"
        raw = self.entry.get().strip()
        try:
            # Bound input length so accidental pastes remain manageable.
            if len(raw) > 12:
                raise ValueError
            answer = int(raw)
        except ValueError:
            self.feedback.config(text="Enter a whole number, such as 24 or -7.", fg=RED)
            return "break"

        q = self.questions[self.index]
        self.attempts.append(answer)
        correct = answer == q["answer"]
        if not correct and len(self.attempts) == 1:
            self.feedback.config(text="Not quite. Try once more for 5 points.", fg=RED)
            self.entry.selection_range(0, "end")
            self.entry.focus_set()
            return "break"

        points = (10 if len(self.attempts) == 1 else 5) if correct else 0
        self.score += points
        self.records.append({
            "question": q.copy(), "attempts": self.attempts[:], "points": points
        })
        self.accepting = False
        self.entry.config(state="disabled")
        self.feedback.config(
            text=f"Correct · +{points} points" if correct else
            f'{expression(q)} = {q["answer"]}',
            fg=TEAL if correct else RED,
        )
        self.score_label.config(
            text=f"Score  {self.score}/{len(self.questions) * 10}"
        )
        self.progress.config(value=self.index + 1)
        if self.index + 1 == len(self.questions):
            # Freeze duration when the final answer is checked.
            self.elapsed = int(time.monotonic() - self.started)
            if self.timer is not None:
                self.root.after_cancel(self.timer)
                self.timer = None
            self.clock.config(text=duration(self.elapsed))
        self.action.config(
            text="See results  →" if self.index + 1 == len(self.questions)
            else "Next question  →",
            command=self.next_question,
        )
        self.action.focus_set()
        return "break"

    def next_question(self):
        if self.page != "quiz" or self.accepting:
            return
        self.index += 1
        if self.index == len(self.questions):
            self.results()
        else:
            self.show_question()

    def table(self, headings):
        frame = tk.Frame(self.main, bg=WHITE)
        frame.pack(fill="both", expand=True, pady=12)
        table = ttk.Treeview(frame, columns=headings, show="headings", height=6)
        for title in headings:
            table.heading(title, text=title)
            table.column(title, anchor="center", width=140, minwidth=80)
        scroll = ttk.Scrollbar(frame, command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(fill="both", expand=True)
        table.tag_configure("retry", foreground=RED)
        return table

    def results(self):
        if self.finished:
            return
        self.finished = True
        total = len(self.questions)
        percent = round(self.score / (total * 10) * 100)
        first = sum(r["points"] == 10 for r in self.records)
        difficult = [
            r["question"].copy() for r in self.records if r["points"] < 10
        ]

        # Compare only sessions with the same practice settings.
        comparable = [
            r["score"] for r in self.history
            if all(r.get(k) == self.settings[k]
                   for k in ("level", "operation", "count", "negatives"))
        ]
        previous = max(comparable, default=-1)
        saved = True
        if not self.retry:
            self.history.append({
                **self.settings,
                "score": self.score,
                "seconds": self.elapsed,
                "date": time.strftime("%d %b %Y, %H:%M"),
            })
            self.history = self.history[-100:]
            saved = self.save()

        self.clear("results")
        self.heading(
            "Session complete",
            "Review practice doesn’t affect your saved scores." if self.retry
            else "Your results and answers are below.",
        )
        summary = self.card(self.main)
        summary.pack(fill="x")
        self.label(summary, f"{self.score}/{total * 10} points", 30, bold=True).pack(anchor="w")
        self.label(
            summary,
            f"{percent}% score   ·   {first}/{total} correct first time"
            f"   ·   {duration(self.elapsed)}",
            11, MUTED,
        ).pack(anchor="w", pady=(8, 0))
        if not self.retry and self.score > previous:
            self.label(
                summary, "Best score for these settings", 10, TEAL, True
            ).pack(anchor="w", pady=(10, 0))

        controls = tk.Frame(self.main, bg=BG)
        controls.pack(fill="x", pady=(16, 0))
        self.label(controls, "Answer review", 14, bold=True).pack(side="left")
        only_difficult = tk.BooleanVar(value=False)
        table = self.table(("Question", "Your answers", "Answer", "Points"))

        def refresh():
            table.delete(*table.get_children())
            for record in self.records:
                if only_difficult.get() and record["points"] == 10:
                    continue
                q = record["question"]
                table.insert("", "end", values=(
                    expression(q),
                    ", ".join(map(str, record["attempts"])),
                    q["answer"], record["points"],
                ), tags=("retry",) if record["points"] < 10 else ())

        tk.Checkbutton(
            controls, text="Needs practice", variable=only_difficult,
            command=refresh, bg=BG, fg=MUTED, activebackground=BG,
            font=("Segoe UI", 10),
        ).pack(side="right")
        refresh()

        if not saved:
            self.label(
                self.main, "Couldn’t save to disk. This result is available until you close the app.",
                10, RED,
            ).pack(anchor="w")

        actions = tk.Frame(self.main, bg=BG)
        actions.pack(fill="x", pady=(8, 0))
        self.button(actions, "New session", self.home).pack(side="left")
        if difficult:
            self.button(
                actions, f"Practise {len(difficult)} difficult questions  →",
                lambda: self.begin(difficult, retry=True), True,
            ).pack(side="right")

    def show_history(self):
        self.clear("history")
        self.heading("Session history", "Your latest 100 completed sessions. Review practice is excluded.")
        if not self.history:
            card = self.card(self.main)
            card.pack(fill="x")
            self.label(card, "No sessions yet", 20, bold=True).pack(anchor="w")
            self.label(card, "Finish your first session to see it here.", color=MUTED).pack(
                anchor="w", pady=12
            )
            self.button(card, "Start practising", self.home, True).pack(anchor="w")
            return

        table = self.table(("Completed", "Level", "Operation", "Score", "Time"))
        table.column("Completed", width=190)
        for row in reversed(self.history):
            table.insert("", "end", values=(
                row["date"], row["level"], row["operation"],
                f'{row["score"]}/{row["count"] * 10}',
                duration(row["seconds"]),
            ))
        self.label(
            self.main, "Scores use 10 points per question; compare like-for-like sessions.",
            10, MUTED,
        ).pack(anchor="w")

    def navigate(self, destination):
        if self.page == "quiz":
            # A completed quiz should be saved even if the user leaves
            # before clicking the results button.
            if len(self.records) == len(self.questions):
                self.results()
            elif not messagebox.askyesno(
                "Leave session?",
                "This session is still in progress. Leave without saving it?",
                parent=self.root,
            ):
                return
        destination()

    def close(self):
        self.navigate(self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    MathsStudio(root)
    root.mainloop()