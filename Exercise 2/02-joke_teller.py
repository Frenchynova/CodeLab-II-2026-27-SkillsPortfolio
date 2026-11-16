import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import random

BG, PAPER, INK = "#F4F1EB", "#FFFEFA", "#292623"
MUTED, ACCENT = "#827B72", "#A39479"
FOLDER = Path(__file__).resolve().parent
jokes, deck, favourites = [], [], []
current, revealed, shown = None, False, 0

root = tk.Tk()
root.title("Joke Studio")
root.geometry("720x720")
root.minsize(660, 700)
root.configure(bg=BG)


def label(parent, text, size=12, color=INK):
    widget = tk.Label(
        parent, text=text, bg=parent["bg"], fg=color,
        font=("Segoe UI", size), wraplength=580, justify="left"
    )
    widget.pack(anchor="w", pady=8)
    return widget


def button(parent, text, command):
    widget = tk.Button(
        parent, text=text, command=command,
        bg=INK, fg=PAPER, activebackground=ACCENT,
        activeforeground=PAPER, font=("Segoe UI", 11),
        relief="flat", padx=16, pady=11, cursor="hand2"
    )
    return widget


def readJokes():
    try:
        lines = (FOLDER / "randomJokes.txt").read_text(
            encoding="utf-8-sig"
        ).splitlines()
    except (OSError, UnicodeError):
        return
    for line in lines:
        setup, separator, answer = line.strip().partition("?")
        if separator and setup.strip() and answer.strip():
            joke = (setup.strip() + "?", answer.strip())
            if joke not in jokes:
                jokes.append(joke)


def nextJoke():
    global current, revealed, shown, deck
    if not jokes:
        return
    if not deck:
        deck = jokes.copy()
        random.shuffle(deck)
        if len(deck) > 1 and deck[-1] == current:
            deck[0], deck[-1] = deck[-1], deck[0]

    current = deck.pop()
    revealed = False
    shown += 1
    setup_label.config(text=current[0])
    answer_label.config(text="Take a guess before revealing the answer.", fg=MUTED)
    status.config(text="")
    reveal_button.config(state="normal")
    copy_button.config(state="disabled")
    updateControls()


def reveal():
    global revealed
    if current is None or revealed:
        return
    revealed = True
    answer_label.config(text=current[1], fg=ACCENT)
    reveal_button.config(state="disabled")
    copy_button.config(state="normal")


def updateControls():
    counter.config(text=f"{len(jokes)} jokes available  /  {shown} told this session")
    save_button.config(
        state="normal" if current else "disabled",
        text="Remove favourite" if current in favourites else "Save favourite"
    )
    favourites_button.config(text=f"Favourites ({len(favourites)})")


def saveFavourite():
    if current is None:
        return
    if current in favourites:
        favourites.remove(current)
        status.config(text="Removed from favourites.")
    else:
        favourites.append(current)
        status.config(text="Saved for this app session.")
    updateControls()


def showFavourites():
    window = tk.Toplevel(root)
    window.title("Your favourites")
    window.geometry("550x420")
    window.configure(bg=BG)
    label(window, "  Worth keeping.", 24)

    text = ScrolledText(
        window, wrap="word", font=("Segoe UI", 12),
        bg=PAPER, fg=INK, relief="flat", padx=15, pady=15
    )
    text.pack(fill="both", expand=True, padx=20, pady=15)
    if not favourites:
        text.insert("end", "No favourites yet.")
    for number, (setup, answer) in enumerate(favourites, 1):
        text.insert("end", f"{number}. {setup}\n{answer}\n\n")
    text.config(state="disabled")


def copyJoke():
    if current is not None and revealed:
        try:
            root.clipboard_clear()
            root.clipboard_append("\n".join(current))
            status.config(text="Copied to your clipboard.")
        except tk.TclError:
            status.config(text="The clipboard is unavailable.")


# Header and optional logo
header = tk.Frame(root, bg=BG, padx=28, pady=18)
header.pack(fill="x")
try:
    image = tk.PhotoImage(file=str(FOLDER / "joke_studio_logo.png"))
    scale = max(1, (max(image.width(), image.height()) + 55) // 56)
    logo = image.subsample(scale)
    tk.Label(header, image=logo, bg=BG).pack(side="left", padx=(0, 12))
    root.iconphoto(True, logo)
except (tk.TclError, OSError):
    pass

tk.Label(
    header, text="Joke Studio", bg=BG, fg=INK,
    font=("Segoe UI", 23, "bold")
).pack(side="left")
favourites_button = button(header, "Favourites", showFavourites)
favourites_button.pack(side="right")

body = tk.Frame(root, bg=BG, padx=30, pady=8)
body.pack(fill="both", expand=True)
label(body, "A joke, on demand.", 28)
counter = label(body, "", 10, MUTED)

card = tk.Frame(
    body, bg=PAPER, padx=24, pady=20,
    highlightbackground="#E1DCD3", highlightthickness=1
)
card.pack(fill="both", expand=True, pady=(12, 18))
label(card, "THE SETUP", 9, ACCENT)
setup_label = label(card, "Something to smile about.", 21)
tk.Frame(card, bg="#E1DCD3", height=1).pack(fill="x", pady=14)
label(card, "THE PUNCHLINE", 9, MUTED)
answer_label = label(card, "Ask Jarvis for a joke to get started.", 16, MUTED)

start_button = button(body, "Jarvis tell me a Joke", nextJoke)
start_button.pack(fill="x", pady=5)

actions = tk.Frame(body, bg=BG)
actions.pack(fill="x", pady=5)
reveal_button = button(actions, "Show Punchline", reveal)
reveal_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
reveal_button.config(state="disabled")
next_button = button(actions, "Next Joke", nextJoke)
next_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

tools = tk.Frame(body, bg=BG)
tools.pack(fill="x", pady=5)
save_button = button(tools, "Save favourite", saveFavourite)
save_button.pack(side="left")
copy_button = button(tools, "Copy joke", copyJoke)
copy_button.pack(side="left", padx=8)
copy_button.config(state="disabled")
button(tools, "Quit", root.destroy).pack(side="right")
status = label(body, "", 10, MUTED)

readJokes()
updateControls()
if not jokes:
    setup_label.config(text="The joke file could not be loaded.")
    answer_label.config(
        text="Place a UTF-8 randomJokes.txt file beside this program, then restart."
    )
    start_button.config(state="disabled")
    next_button.config(state="disabled")

root.mainloop()