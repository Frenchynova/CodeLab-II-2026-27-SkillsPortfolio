import json
import math
import random
import tkinter as tk
from pathlib import Path

# Colours and file locations
BG = "#F4F1EB"
PAPER = "#FFFEFA"
INK = "#292623"
MUTED = "#827B72"
LINE = "#E1DCD3"
ACCENT = "#BC573D"
SOFT = "#EEE7DC"

FOLDER = Path(__file__).resolve().parent
JOKES_FILE = FOLDER / "randomJokes.txt"
LOGO_FILE = FOLDER / "joke_studio_logo.png"
SAVED_FILE = Path.home() / ".joke_studio_favourites.json"


class JokeStudio:
    def __init__(self, root):
        self.root = root
        self.current = None
        self.revealed = False
        self.deck = []
        self.shown = 0
        self.logo = None
        self.saved = self.readSaved()
        self.jokes = self.readJokes()

        root.title("Joke Studio")
        root.geometry("850x760")
        root.minsize(650, 560)
        root.configure(bg=BG)

        # Scrollable page
        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.page = tk.Frame(self.canvas, bg=BG, padx=34, pady=28)
        self.page_id = self.canvas.create_window(
            (0, 0), window=self.page, anchor="nw"
        )
        self.page.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.page_id, width=e.width
            )
        )
        root.bind("<MouseWheel>", self.scroll)

        # Header
        header = tk.Frame(self.page, bg=BG)
        header.pack(fill="x")

        self.logo_label = tk.Label(header, bg=BG)
        self.logo_label.pack(side="left", padx=(0, 12))
        self.loadLogo()

        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left")
        self.label(brand, "Joke Studio", 22, bold=True).pack(anchor="w")
        self.label(brand, "A small break from the serious stuff.",
                   10, MUTED).pack(anchor="w", pady=(3, 0))

        self.saved_button = self.button(
            header, "Favourites", self.showSaved
        )
        self.saved_button.pack(side="right")

        self.rule(self.page, 22)

        intro = tk.Frame(self.page, bg=BG)
        intro.pack(fill="x", pady=(0, 20))
        self.label(intro, "A joke, on demand.", 28, bold=True).pack(
            anchor="w"
        )
        self.counter = self.label(intro, "", 10, MUTED)
        self.counter.pack(anchor="w", pady=(7, 0))

        # The main reading area
        card = tk.Frame(
            self.page, bg=PAPER, padx=28, pady=26,
            highlightbackground=LINE, highlightthickness=1
        )
        card.pack(fill="x")

        card_top = tk.Frame(card, bg=PAPER)
        card_top.pack(fill="x", pady=(0, 20))
        self.section_label = self.label(
            card_top, "YOUR NEXT SMALL DISTRACTION", 9, ACCENT, True
        )
        self.section_label.pack(side="left")
        self.number_label = self.label(card_top, "—", 11, MUTED)
        self.number_label.pack(side="right")

        self.setup_label = self.label(
            card, "Something to smile about.", 25, bold=True
        )
        self.setup_label.configure(wraplength=650)
        self.setup_label.pack(fill="x", pady=(0, 22))

        tk.Frame(card, bg=LINE, height=1).pack(fill="x")

        self.answer_panel = tk.Frame(card, bg=PAPER, pady=20)
        self.answer_panel.pack(fill="x")

        self.answer_caption = self.label(
            self.answer_panel, "THE PUNCHLINE", 9, MUTED, True
        )
        self.answer_caption.pack(anchor="w", pady=(0, 10))

        self.answer_label = self.label(
            self.answer_panel,
            "Ask Jarvis for a joke to get started.",
            17, MUTED
        )
        self.answer_label.configure(wraplength=650)
        self.answer_label.pack(fill="x")
        card.bind("<Configure>", self.resizeCard)

        self.start_button = self.button(
            self.page, "Jarvis tell me a Joke", self.nextJoke, primary=True
        )
        self.start_button.pack(fill="x", pady=(18, 10))

        actions = tk.Frame(self.page, bg=BG)
        actions.pack(fill="x")

        self.reveal_button = self.button(
            actions, "Show Punchline", self.reveal
        )
        self.reveal_button.pack(
            side="left", fill="x", expand=True, padx=(0, 5)
        )
        self.next_button = self.button(
            actions, "Next Joke  →", self.nextJoke
        )
        self.next_button.pack(
            side="left", fill="x", expand=True, padx=(5, 0)
        )

        tools = tk.Frame(self.page, bg=BG)
        tools.pack(fill="x", pady=(12, 0))

        self.save_button = self.button(
            tools, "Save favourite", self.toggleSaved, quiet=True
        )
        self.save_button.pack(side="left")

        self.copy_button = self.button(
            tools, "Copy joke", self.copyJoke, quiet=True
        )
        self.copy_button.pack(side="left", padx=8)

        self.button(
            tools, "Quit", root.destroy, quiet=True
        ).pack(side="right")

        self.status = self.label(self.page, "", 10, MUTED)
        self.status.configure(wraplength=650)
        self.status.pack(anchor="w", pady=(14, 0))

        self.rule(self.page, 18)
        self.label(
            self.page,
            "SPACE  Reveal punchline       →  Next joke",
            9, MUTED
        ).pack(anchor="w")

        root.bind("<space>", self.spaceKey)
        root.bind("<Right>", self.nextKey)

        if not self.jokes:
            self.setup_label.configure(text="The jokes haven't arrived yet.")
            self.answer_label.configure(
                text="Place randomJokes.txt beside this Python file, "
                     "save it as UTF-8, and restart the app."
            )
        self.updateControls()

    # ---------- Interface ----------

    def label(self, parent, text, size=11, color=INK, bold=False):
        return tk.Label(
            parent, text=text, bg=parent["bg"], fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            anchor="w", justify="left"
        )

    def rule(self, parent, padding):
        tk.Frame(parent, bg=LINE, height=1).pack(
            fill="x", pady=padding
        )

    def button(self, parent, text, command, primary=False, quiet=False):
        background = INK if primary else BG if quiet else SOFT
        foreground = PAPER if primary else INK
        hover = "#454039" if primary else "#E5DDD0"

        button = tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 10, "bold"),
            bg=background, fg=foreground,
            activebackground=hover, activeforeground=foreground,
            disabledforeground="#A59D91",
            relief="flat", bd=0, padx=16, pady=12,
            cursor="hand2", highlightthickness=2,
            highlightbackground=background, highlightcolor=ACCENT
        )

        def enter(event):
            if button["state"] != "disabled":
                button.configure(bg=hover)

        button.bind("<Enter>", enter)
        button.bind("<Leave>", lambda e: button.configure(bg=background))
        button.bind("<space>", self.spaceKey)

        def activate(event):
            button.invoke()
            return "break"

        button.bind("<Return>", activate)
        return button

    def resizeCard(self, event):
        width = max(240, event.width - 60)
        self.setup_label.configure(wraplength=width)
        self.answer_label.configure(wraplength=width)

    def scroll(self, event):
        if event.widget.winfo_toplevel() != self.root:
            return
        if self.page.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-3 if event.delta > 0 else 3, "units")

    def loadLogo(self):
        try:
            image = tk.PhotoImage(master=self.root, file=str(LOGO_FILE))
            if not image.width() or not image.height():
                raise ValueError("Empty image")
            factor = max(
                1, math.ceil(max(image.width(), image.height()) / 64)
            )
            self.logo = image.subsample(factor)
            self.logo_label.configure(image=self.logo)
        except (OSError, ValueError, tk.TclError):
            self.logo_label.configure(
                text="JS", fg=ACCENT, font=("Segoe UI", 23, "bold")
            )
            return

        try:
            self.root.iconphoto(True, self.logo)
        except tk.TclError:
            pass

    # ---------- Jokes ----------

    def readJokes(self):
        try:
            lines = JOKES_FILE.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError):
            return []

        jokes = []
        for line in lines:
            setup, separator, punchline = line.strip().partition("?")
            if separator and setup.strip() and punchline.strip():
                joke = (setup.strip() + "?", punchline.strip())
                if joke not in jokes:
                    jokes.append(joke)
        return jokes

    def nextJoke(self):
        if not self.jokes:
            return

        # A shuffled deck shows every joke before repeating.
        if not self.deck:
            self.deck = self.jokes.copy()
            random.shuffle(self.deck)
            if len(self.deck) > 1 and self.deck[-1] == self.current:
                self.deck[0], self.deck[-1] = self.deck[-1], self.deck[0]

        self.current = self.deck.pop()
        self.revealed = False
        self.shown += 1

        self.section_label.configure(text="THE SETUP")
        self.number_label.configure(text=f"{self.shown:02d}")
        self.setup_label.configure(text=self.current[0])
        self.answer_caption.configure(text="TAKE A GUESS", fg=MUTED)
        self.answer_label.configure(
            text="The answer can wait a second.", fg=MUTED
        )
        self.status.configure(text="")
        self.updateControls()
        self.setup_label.focus_set()

    def reveal(self):
        if self.current is None or self.revealed:
            return
        self.revealed = True
        self.answer_caption.configure(text="THE PUNCHLINE", fg=ACCENT)
        self.answer_label.configure(text=self.current[1], fg=INK)
        self.status.configure(text="Keep this one, or try another.")
        self.updateControls()

    def updateControls(self):
        available = bool(self.jokes)
        selected = self.current is not None

        self.start_button.configure(
            state="normal" if available else "disabled"
        )
        self.next_button.configure(
            state="normal" if available else "disabled"
        )
        self.reveal_button.configure(
            state="normal" if selected and not self.revealed else "disabled"
        )
        self.copy_button.configure(
            state="normal" if self.revealed else "disabled"
        )
        self.save_button.configure(
            state="normal" if selected else "disabled",
            text="Remove favourite" if self.current in self.saved
            else "Save favourite"
        )
        self.saved_button.configure(text=f"Favourites  ·  {len(self.saved)}")
        self.counter.configure(
            text=f"{len(self.jokes)} jokes in the collection"
                 f"    /    {self.shown} told this session"
        )

    # ---------- Favourites ----------

    def readSaved(self):
        try:
            data = json.loads(SAVED_FILE.read_text("utf-8"))
            if isinstance(data, list):
                valid = [
                    tuple(item) for item in data
                    if isinstance(item, list) and len(item) == 2
                    and all(isinstance(s, str) and s.strip() for s in item)
                ]
                return list(dict.fromkeys(valid))
        except (OSError, ValueError):
            pass
        return []

    def toggleSaved(self):
        if self.current is None:
            return

        if self.current in self.saved:
            self.saved.remove(self.current)
            message = "Removed from your favourites."
        else:
            self.saved.append(self.current)
            message = "Saved for another day."

        try:
            temporary = SAVED_FILE.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(self.saved, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            temporary.replace(SAVED_FILE)
        except OSError:
            message = "Updated for this session, but couldn't save to disk."

        self.status.configure(text=message)
        self.updateControls()

    def showSaved(self):
        window = tk.Toplevel(self.root)
        window.title("Joke Studio — Favourites")
        window.geometry("620x480")
        window.minsize(400, 300)
        window.configure(bg=BG)

        self.label(window, "Worth keeping.", 25, bold=True).pack(
            anchor="w", padx=25, pady=(24, 6)
        )
        self.label(window, "Your saved jokes, all in one place.", 10, MUTED).pack(
            anchor="w", padx=25, pady=(0, 20)
        )

        frame = tk.Frame(window, bg=PAPER)
        frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        text = tk.Text(
            frame, wrap="word", bg=PAPER, fg=INK,
            font=("Segoe UI", 12), relief="flat", padx=20, pady=20
        )
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        text.tag_configure("setup", font=("Segoe UI", 12, "bold"))

        if not self.saved:
            text.insert("end", "Nothing saved yet. Keep a joke you enjoy.")
        for number, (setup, answer) in enumerate(self.saved, 1):
            text.insert("end", f"{number:02d}   {setup}\n", "setup")
            text.insert("end", f"{answer}\n\n")

        text.configure(state="disabled")

    # ---------- Clipboard and shortcuts ----------

    def copyJoke(self):
        if self.current is None or not self.revealed:
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(self.current))
            self.status.configure(text="Copied. Go make someone groan.")
        except tk.TclError:
            self.status.configure(text="The clipboard is unavailable right now.")

    def spaceKey(self, event=None):
        if event is None or event.widget.winfo_toplevel() == self.root:
            self.reveal()
        return "break"

    def nextKey(self, event=None):
        if event is None or event.widget.winfo_toplevel() == self.root:
            self.nextJoke()
        return "break"


if __name__ == "__main__":
    root = tk.Tk()
    JokeStudio(root)
    root.mainloop()