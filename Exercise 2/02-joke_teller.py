import random
import tkinter as tk
from pathlib import Path

BACKGROUND = "#F4F2ED"
NAVY = "#19283B"
GREEN = "#247568"
MUTED = "#6D7783"


class JokeStudio:
    def __init__(self, root):
        self.root = root
        self.jokes = []
        self.current = None

        root.title("Joke Studio")
        root.geometry("650x600")
        root.minsize(600, 580)
        root.configure(bg=BACKGROUND)

        main = tk.Frame(root, bg=BACKGROUND, padx=35, pady=30)
        main.pack(fill="both", expand=True)

        tk.Label(
            main, text="JOKE STUDIO",
            font=("Segoe UI", 11, "bold"),
            bg=BACKGROUND, fg=GREEN
        ).pack(pady=(0, 8))

        tk.Label(
            main, text="A little laugh goes a long way.",
            font=("Segoe UI", 23, "bold"),
            bg=BACKGROUND, fg=NAVY
        ).pack(pady=(0, 22))

        self.start_button = self.makeButton(
            main, "Alexa tell me a Joke", self.nextJoke
        )
        self.start_button.pack(fill="x", pady=(0, 18))

        card = tk.Frame(main, bg="white", padx=24, pady=22)
        card.pack(fill="both", expand=True)

        self.setup_label = tk.Label(
            card, text="Ready for a joke?\nClick the button above.",
            font=("Segoe UI", 18, "bold"),
            bg="white", fg=NAVY,
            wraplength=480, justify="center"
        )
        self.setup_label.pack(fill="x", pady=(5, 15))

        self.punchline_label = tk.Label(
            card, text="",
            font=("Segoe UI", 15),
            bg="white", fg=GREEN,
            wraplength=480, justify="center"
        )
        self.punchline_label.pack(fill="x", pady=10)

        self.reveal_button = self.makeButton(
            main, "Show Punchline", self.showPunchline
        )
        self.reveal_button.pack(fill="x", pady=(18, 8))
        self.reveal_button.config(state="disabled")

        controls = tk.Frame(main, bg=BACKGROUND)
        controls.pack(fill="x")

        self.next_button = self.makeButton(
            controls, "Next Joke", self.nextJoke
        )
        self.next_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.makeButton(
            controls, "Quit", root.destroy
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.status = tk.Label(
            main, text="", font=("Segoe UI", 9),
            bg=BACKGROUND, fg=MUTED
        )
        self.status.pack(pady=(12, 0))

        self.loadJokes()

    def makeButton(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 11, "bold"),
            bg=NAVY, fg="white",
            activebackground=GREEN, activeforeground="white",
            disabledforeground="#AAB4BF",
            relief="flat", cursor="hand2", pady=12
        )

    def loadJokes(self):
        """Read the supplied text file and split each joke once."""
        path = Path(__file__).resolve().parent / "randomJokes.txt"

        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()

            for line in lines:
                setup, separator, punchline = line.strip().partition("?")
                if separator and setup.strip() and punchline.strip():
                    joke = (setup.strip() + "?", punchline.strip())
                    if joke not in self.jokes:
                        self.jokes.append(joke)

            if not self.jokes:
                raise ValueError("No valid jokes were found in randomJokes.txt.")

        except (OSError, UnicodeError, ValueError) as error:
            self.setup_label.config(text="The joke file could not be loaded.")
            self.punchline_label.config(
                text="Save randomJokes.txt as UTF-8 in the same folder "
                     "as this Python file, then restart the app."
            )
            self.start_button.config(state="disabled")
            self.next_button.config(state="disabled")
            self.status.config(text=type(error).__name__)
            return

        self.status.config(text=f"{len(self.jokes)} jokes ready to tell")

    def nextJoke(self):
        """Choose a joke and hide the previous punchline."""
        if not self.jokes:
            return

        choices = [joke for joke in self.jokes if joke != self.current]
        self.current = random.choice(choices or self.jokes)

        self.setup_label.config(text=self.current[0])
        self.punchline_label.config(text="")
        self.reveal_button.config(state="normal")
        self.status.config(text="Think you know the answer? Reveal the punchline.")

    def showPunchline(self):
        """Reveal the answer to the current joke."""
        if self.current is not None:
            self.punchline_label.config(text=self.current[1])
            self.reveal_button.config(state="disabled")
            self.status.config(text="Ready for another? Click Next Joke.")


if __name__ == "__main__":
    window = tk.Tk()
    JokeStudio(window)
    window.mainloop()