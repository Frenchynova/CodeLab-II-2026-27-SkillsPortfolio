import tkinter as tk
from tkinter import ttk
from pathlib import Path
import random

BG, GREEN, INK = "#F4F5F0", "#326B50", "#243C32"
LEVELS = {"Easy": (0, 9), "Moderate": (10, 99), "Advanced": (1000, 9999)}
best = {}
screen = "menu"

root = tk.Tk()
root.title("Maths Studio")
root.geometry("620x600")
root.configure(bg=BG)

header = tk.Frame(root, bg=INK, padx=20, pady=15)
header.pack(fill="x")
try:
    image = tk.PhotoImage(
        file=str(Path(__file__).resolve().parent / "maths_studio_logo.png")
    )
    logo = image.subsample(max(1, (max(image.width(), image.height()) + 47) // 48))
    tk.Label(header, image=logo, bg=INK).pack(side="left", padx=(0, 12))
    root.iconphoto(True, logo)
except (tk.TclError, OSError):
    pass

tk.Label(header, text="MATHS QUIZ", bg=INK, fg="white",
         font=("Segoe UI", 20, "bold")).pack(side="left")
body = tk.Frame(root, bg=BG, padx=30, pady=20)
body.pack(fill="both", expand=True)


def clear():
    for widget in body.winfo_children():
        widget.destroy()


def label(text, size=14):
    widget = tk.Label(body, text=text, bg=BG, fg=INK,
                      font=("Segoe UI", size), wraplength=520)
    widget.pack(pady=12)
    return widget


def button(text, command):
    widget = tk.Button(body, text=text, command=command, bg=GREEN,
                       fg="white", font=("Segoe UI", 12), relief="flat", pady=10)
    widget.pack(fill="x", pady=6)
    return widget


def displayMenu():
    global screen
    screen = "menu"
    clear()
    label("A little maths. A little progress.", 23)
    for level in LEVELS:
        record = f" • Best: {best[level]}/100" if level in best else ""
        button(level + record, lambda chosen=level: start(chosen))
    label("10 questions • Two attempts\nFirst try: 10 points • Second try: 5 points", 11)


def start(level):
    global difficulty, score, question
    difficulty, score, question = level, 0, 0
    displayProblem()


def randomInt(level):
    return random.randint(*LEVELS[level])


def decideOperation():
    return random.choice(["+", "-"])


def displayProblem():
    global question, attempt, solution, screen, entry, feedback, action, bar
    if question == 10:
        displayResults()
        return
    clear()
    question += 1
    attempt, screen = 1, "answer"
    a, b, operation = randomInt(difficulty), randomInt(difficulty), decideOperation()
    solution = a + b if operation == "+" else a - b
    label(f"{difficulty} • Question {question}/10 • Score: {score}", 12)
    bar = ttk.Progressbar(body, maximum=10, value=question - 1)
    bar.pack(fill="x", pady=8)
    label(f"{a} {operation} {b} = ?", 36)
    entry = tk.Entry(body, font=("Segoe UI", 22), justify="center")
    entry.pack(pady=10, ipady=8)
    entry.focus_set()
    feedback = label("Enter your answer.", 12)
    action = button("Check answer", check)
    label("Press Enter to check or continue.", 10)


def isCorrect(answer):
    return answer == solution


def check():
    global score, attempt, screen
    if screen != "answer":
        return
    try:
        answer = int(entry.get())
    except ValueError:
        feedback.config(text="Please enter a whole number.")
        return
    if isCorrect(answer):
        points = 10 if attempt == 1 else 5
        score += points
        feedback.config(text=f"Correct! +{points} points.")
    elif attempt == 1:
        attempt = 2
        feedback.config(text="Try again for 5 points.")
        entry.delete(0, tk.END)
        entry.focus_set()
        return
    else:
        feedback.config(text=f"The correct answer is {solution}.")
    screen = "next"
    entry.config(state="disabled")
    bar["value"] = question
    action.config(text="Results" if question == 10 else "Next question",
                  command=displayProblem)


def displayResults():
    global screen
    screen = "results"
    clear()
    best[difficulty] = max(best.get(difficulty, 0), score)
    grade = "F"
    for minimum, letter in [(91, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D")]:
        if score >= minimum:
            grade = letter
            break
    label("Practice complete.", 26)
    label(f"{score}/100 • Grade: {grade}", 30)
    label(f"Personal best: {best[difficulty]}/100")
    button("Play again", displayMenu)
    button("Quit", root.destroy)
    label("Personal bests reset when the app closes.", 10)


def enter(event):
    if screen == "answer":
        check()
    elif screen == "next":
        displayProblem()
    return "break"


root.bind("<Return>", enter)
displayMenu()
root.mainloop()