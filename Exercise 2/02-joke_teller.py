import json
import math
import random
import tkinter as tk
from pathlib import Path

BG = "#F6F2EB"
WHITE = "#FFFFFF"
INK = "#302638"
MUTED = "#817887"
ORANGE = "#F3AE58"
BORDER = "#E7DFD6"

APP_FOLDER = Path(__file__).resolve().parent
JOKE_FILE = APP_FOLDER / "randomJokes.txt"
LOGO_FILE = APP_FOLDER / "joke_studio_logo.png"
FAVOURITES_FILE = Path.home() / ".joke_studio_favourites.json"


class JokeStudio:
    def __init__(self, root):
        self.root = root
        self.jokes = []
        self.bag = []
        self.current = None
        self.revealed = False
        self.shown = 0
        self.logo_image = None
        self.favourites = self.loadFavourites()

        root.title("Jarvis Joke Studio")
        root.geometry("800x720")
        root.minsize(660, 560)
        root.configure(bg=BG)

        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.main = tk.Frame(self.canvas, bg=BG, padx=30, pady=26)
        self.content = self.canvas.create_window(
            (0, 0), window=self.main, anchor="nw"
        )
        self.main.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.content, width=event.width
            )
        )
        root.bind("<MouseWheel>", self.scrollPage)

        # Header
        header = tk.Frame(self.main, bg=BG)
        header.pack(fill="x", pady=(0, 22))

        self.logo_label = tk.Label(header, bg=BG)
        self.logo_label.pack(side="left", padx=(0, 12))
        self.loadLogo()

        self.label(
            header, "Jarvis Joke Studio", 23, bold=True
        ).pack(side="left")
        self.button(
            header, "Favourites", self.showFavourites
        ).pack(side="right")

        self.label(
            self.main, "WHAT JOKE WILL JARVIS TELL YOU?",
            9, MUTED, True
        ).pack(anchor="w", pady=(0, 8))

        title = self.label(
            self.main, "Jarvis Tells Jokes, You Enjoy the Punchline.",
            25, bold=True
        )
        title.configure(wraplength=620)
        title.pack(anchor="w", pady=(0, 12))

        self.stats = self.label(self.main, "", 10, MUTED)
        self.stats.pack(anchor="w", pady=(0, 18))

        self.start_button = self.button(
            self.main, "Jarvis tell me a Joke",
            self.nextJoke, primary=True
        )
        self.start_button.pack(fill="x", pady=(0, 18))

        # Joke card
        card = tk.Frame(
            self.main, bg=WHITE, padx=24, pady=24,
            highlightbackground=BORDER, highlightthickness=1
        )
        card.pack(fill="x")

        self.card_heading = self.label(
            card, "Jarvis Joke", 9, MUTED, True
        )
        self.card_heading.pack(anchor="w", pady=(0, 18))

        self.setup = self.label(
            card, "Ready when you are.", 22, bold=True
        )
        self.setup.configure(wraplength=570)
        self.setup.pack(fill="x", pady=(0, 22))

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=8)

        self.punchline = self.label(
            card, "Ask Jarvis for a joke. The punchline stays hidden.",
            15, MUTED
        )
        self.punchline.configure(wraplength=570)
        self.punchline.pack(fill="x", pady=(18, 12))
        card.bind("<Configure>", self.resizeText)

        # Main controls
        actions = tk.Frame(self.main, bg=BG)
        actions.pack(fill="x", pady=(18, 10))

        self.reveal_button = self.button(
            actions, "Show Punchline",
            self.showPunchline, primary=True
        )
        self.reveal_button.pack(
            side="left", fill="x", expand=True, padx=(0, 5)
        )

        self.next_button = self.button(
            actions, "Next Joke", self.nextJoke
        )
        self.next_button.pack(
            side="left", fill="x", expand=True, padx=(5, 0)
        )

        extras = tk.Frame(self.main, bg=BG)
        extras.pack(fill="x")

        self.favourite_button = self.button(
            extras, "Save favourite", self.toggleFavourite
        )
        self.favourite_button.pack(side="left")

        self.copy_button = self.button(
            extras, "Copy joke", self.copyJoke
        )
        self.copy_button.pack(side="left", padx=8)

        self.button(
            extras, "Quit", root.destroy
        ).pack(side="right")

        self.status = self.label(self.main, "", 10, MUTED)
        self.status.configure(wraplength=620)
        self.status.pack(anchor="w", pady=(18, 8))

        self.label(
            self.main, "SPACE  Reveal    ·    RIGHT ARROW  Next joke",
            9, MUTED
        ).pack(anchor="w")

        root.bind("<Right>", self.nextShortcut)
        root.bind("<space>", self.revealShortcut)
        self.loadJokes()

    # Interface helpers
    def label(self, parent, text, size=11, color=INK, bold=False):
        return tk.Label(
            parent, text=text, bg=parent["bg"], fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            anchor="w", justify="left"
        )

    def button(self, parent, text, command, primary=False):
        normal = INK if primary else "#EBE5DD"
        hover = "#4B3A56" if primary else "#DED6CB"
        foreground = WHITE if primary else INK

        button = tk.Button(
            parent, text=text, command=command,
            bg=normal, fg=foreground,
            activebackground=hover, activeforeground=foreground,
            disabledforeground="#A69BA9",
            font=("Segoe UI", 10, "bold"),
            padx=14, pady=11, relief="flat", bd=0,
            cursor="hand2", highlightthickness=2,
            highlightbackground=normal, highlightcolor=ORANGE
        )
        button.bind("<Enter>", lambda event: button.configure(bg=hover))
        button.bind("<Leave>", lambda event: button.configure(bg=normal))

        def activate(event):
            button.invoke()
            return "break"

        button.bind("<Return>", activate)
        button.bind("<space>", self.revealShortcut)
        return button

    def resizeText(self, event):
        width = max(250, event.width - 52)
        self.setup.configure(wraplength=width)
        self.punchline.configure(wraplength=width)

    def scrollPage(self, event):
        if event.widget.winfo_toplevel() != self.root:
            return
        if self.main.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-3 if event.delta > 0 else 3, "units")

    # Logo loads automatically; no file-picker controls.
    def loadLogo(self):
        try:
            original = tk.PhotoImage(master=self.root, file=str(LOGO_FILE))
            if original.width() == 0 or original.height() == 0:
                raise ValueError("Empty image")

            scale = max(
                1, math.ceil(max(original.width(), original.height()) / 72)
            )
            self.logo_image = original.subsample(scale)
            self.logo_label.configure(image=self.logo_image)

        except (tk.TclError, OSError, ValueError):
            self.logo_label.configure(
                text="JS", font=("Segoe UI", 21, "bold"), fg=INK
            )
            return

        try:
            self.root.iconphoto(True, self.logo_image)
        except tk.TclError:
            pass

    # Read jokes
    def loadJokes(self):
        try:
            lines = JOKE_FILE.read_text(encoding="utf-8-sig").splitlines()

            for line in lines:
                setup, separator, punchline = line.strip().partition("?")
                if separator and setup.strip() and punchline.strip():
                    joke = (setup.strip() + "?", punchline.strip())
                    if joke not in self.jokes:
                        self.jokes.append(joke)

            if not self.jokes:
                raise ValueError("No valid jokes found")

        except (OSError, UnicodeError, ValueError):
            self.setup.configure(text="The joke file could not be loaded.")
            self.punchline.configure(
                text="Place randomJokes.txt in the same folder as this "
                     "program. Save it as UTF-8, then restart the app."
            )
            self.status.configure(text="No jokes available.")
            self.updateControls()
            return

        self.status.configure(text="Jarvis is ready when you are.")
        self.updateControls()

    # Tell jokes
    def nextJoke(self):
        if not self.jokes:
            return

        # Every joke appears once before the collection repeats.
        if not self.bag:
            self.bag = self.jokes.copy()
            random.shuffle(self.bag)

            if len(self.bag) > 1 and self.bag[-1] == self.current:
                self.bag[0], self.bag[-1] = self.bag[-1], self.bag[0]

        self.current = self.bag.pop()
        self.revealed = False
        self.shown += 1

        self.card_heading.configure(text=f"JOKE {self.shown:02d} / THE SETUP")
        self.setup.configure(text=self.current[0])
        self.punchline.configure(
            text="The punchline is one click away.", fg=MUTED
        )
        self.status.configure(text="Have a guess, then reveal the punchline.")
        self.updateControls()
        self.setup.focus_set()

    def showPunchline(self):
        if self.current is None or self.revealed:
            return

        self.revealed = True
        self.punchline.configure(text=self.current[1], fg=INK)
        self.status.configure(
            text="Worth keeping? Save it to your favourites."
        )
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
        self.favourite_button.configure(
            state="normal" if selected else "disabled",
            text="Remove favourite" if self.current in self.favourites
            else "Save favourite"
        )
        self.stats.configure(
            text=f"{len(self.jokes)} jokes available    /    "
                 f"{self.shown} shown    /    "
                 f"{len(self.favourites)} favourites"
        )

    # Favourites
    def loadFavourites(self):
        try:
            data = json.loads(FAVOURITES_FILE.read_text("utf-8"))
            if isinstance(data, list):
                valid = [
                    tuple(item) for item in data
                    if isinstance(item, list)
                    and len(item) == 2
                    and all(
                        isinstance(value, str) and value.strip()
                        for value in item
                    )
                ]
                return list(dict.fromkeys(valid))
        except (OSError, ValueError):
            pass
        return []

    def toggleFavourite(self):
        if self.current is None:
            return

        if self.current in self.favourites:
            self.favourites.remove(self.current)
            message = "Removed from favourites."
        else:
            self.favourites.append(self.current)
            message = "Saved to favourites."

        try:
            temporary = FAVOURITES_FILE.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(self.favourites, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            temporary.replace(FAVOURITES_FILE)
        except OSError:
            message = "Updated for this session, but could not save to disk."

        self.status.configure(text=message)
        self.updateControls()

    def showFavourites(self):
        window = tk.Toplevel(self.root)
        window.title("Joke Studio — Favourites")
        window.geometry("600x460")
        window.minsize(400, 300)
        window.configure(bg=BG)

        self.label(window, "The keepers.", 24, bold=True).pack(
            anchor="w", padx=24, pady=20
        )

        frame = tk.Frame(window, bg=BG)
        frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        text = tk.Text(
            frame, wrap="word", font=("Segoe UI", 12),
            bg=WHITE, fg=INK, relief="flat", padx=18, pady=18
        )
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)

        if self.favourites:
            for number, (setup, punchline) in enumerate(self.favourites, 1):
                text.insert("end", f"{number}. {setup}\n{punchline}\n\n")
        else:
            text.insert("end", "No favourites yet. Save a joke you enjoy.")

        text.configure(state="disabled")

    # Clipboard and shortcuts
    def copyJoke(self):
        if self.current is None or not self.revealed:
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(self.current))
            self.status.configure(text="Joke copied to your clipboard.")
        except tk.TclError:
            self.status.configure(text="The clipboard is currently unavailable.")

    def revealShortcut(self, event=None):
        if event is None or event.widget.winfo_toplevel() == self.root:
            self.showPunchline()
        return "break"

    def nextShortcut(self, event=None):
        if event is None or event.widget.winfo_toplevel() == self.root:
            self.nextJoke()
        return "break"


if __name__ == "__main__":
    root = tk.Tk()
    JokeStudio(root)
    root.mainloop()