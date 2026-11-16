import tkinter as tk
from pathlib import Path
import random

BG = "#F4F5F0"
GREEN = "#326B50"
INK = "#243C32"

LIMITS = {
    "Easy": (0, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999)
}

root = tk.Tk()
root.title("Maths Studio")
root.geometry("620x570")
root.configure(bg=BG)

header = tk.Frame(root, bg=INK, padx=20, pady=15)
header.pack(fill="x")

# Load the optional logo from the same folder as this file.
try:
    path = Path(__file__).resolve().parent / "maths_studio_logo.png"
    image = tk.PhotoImage(file=str(path))
    scale = max(1, (max(image.width(), image.height()) + 47) // 48)
    logo = image.subsample(scale)
    tk.Label(header, image=logo, bg=INK).pack(side="left", padx=(0, 12))
    root.iconphoto(True, logo)
except (tk.TclError, OSError):
    pass

tk.Label(
    header, text="MATHS QUIZ", bg=INK, fg="white",
    font=("Segoe UI", 20, "bold")
).pack(side="left")

body = tk.Frame(root, bg=BG, padx=30, pady=25)
body.pack(fill="both", expand=True)


def clear():
    for widget in body.winfo_children():
        widget.destroy()


def label(text, size=14, color=INK):
    widget = tk.Label(
        body, text=text, bg=BG, fg=color,
        font=("Segoe UI", size), wraplength=520
    )
    widget.pack(pady=10)
    return widget


def button(text, command):
    widget = tk.Button(
        body, text=text, command=command,
        bg=GREEN, fg="white", activebackground=INK,
        activeforeground="white", font=("Segoe UI", 12),
        relief="flat", pady=10, cursor="hand2"
    )
    widget.pack(fill="x", pady=6)
    return widget


def displayMenu():
    clear()
    label("A little maths. A little progress.", 23)
    label("Choose your difficulty.")
    for level in LIMITS:
        button(level, lambda selected=level: start(selected))
    label("10 questions • Two attempts\nFirst try: 10 points • Second try: 5 points", 11)


def start(level):
    global difficulty, score, question
    difficulty = level
    score = 0
    question = 0
    displayProblem()


def randomInt(level):
    low, high = LIMITS[level]
    return random.randint(low, high)


def decideOperation():
    return random.choice(["+", "-"])


def displayProblem():
    global question, correct_answer, attempt, finished
    global entry, feedback, action

    if question == 10:
        displayResults()
        return

    clear()
    question += 1
    attempt = 1
    finished = False

    a = randomInt(difficulty)
    b = randomInt(difficulty)
    operation = decideOperation()
    correct_answer = a + b if operation == "+" else a - b

    label(f"{difficulty} • Question {question}/10 • Score: {score}", 12)
    label(f"{a} {operation} {b} = ?", 36)
    label("Your answer", 12)

    entry = tk.Entry(
        body, font=("Segoe UI", 22),
        justify="center", relief="solid", bd=1
    )
    entry.pack(pady=10, ipady=8)
    entry.bind("<Return>", check)
    entry.focus_set()

    feedback = label("First attempt: 10 points available", 12)
    action = button("Check answer", check)


def isCorrect(answer):
    return answer == correct_answer


def check(event=None):
    global score, attempt, finished

    if finished:
        return "break"

    try:
        answer = int(entry.get().strip())
    except ValueError:
        feedback.config(text="Enter a whole number, such as 12 or -5.")
        return "break"

    if isCorrect(answer):
        points = 10 if attempt == 1 else 5
        score += points
        feedback.config(text=f"Correct! +{points} points.")
    elif attempt == 1:
        attempt = 2
        feedback.config(text="Not quite. Try again for 5 points.")
        entry.delete(0, tk.END)
        entry.focus_set()
        return "break"
    else:
        feedback.config(text=f"The correct answer is {correct_answer}.")

    finished = True
    entry.config(state="disabled")
    action.config(
        text="View results" if question == 10 else "Next question",
        command=displayProblem
    )
    return "break"


def displayResults():
    clear()

    if score > 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"

    label("Practice complete.", 26)
    label(f"{score} / 100", 38, GREEN)
    label(f"Grade: {grade}", 20)
    label("Would you like to play again?")
    button("Play again", displayMenu)
    button("Quit", root.destroy)


displayMenu()
root.mainloop()