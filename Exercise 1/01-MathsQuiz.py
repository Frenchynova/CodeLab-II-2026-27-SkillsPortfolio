"""Floor Zero: a ten-guest arithmetic game. Run with Python 3 and Tkinter."""
import ctypes
import math
import random
import tkinter as tk
from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None

ASSETS = Path(__file__).resolve().with_name("rooms")
INK, PANEL, GOLD, IVORY, WINE = "#191917", "#292923", "#dfbe86", "#faf0dc", "#893d35"
LEVELS = {"Easy": (0, 9), "Moderate": (10, 99), "Advanced": (1000, 9999)}
GUESTS = [
    ("The bather", "The tide is coming in. I brought my own tub.", "The underground beach"),
    ("The botanist", "My orchids only open after midnight.", "The night garden"),
    ("The astronomer", "Saturn has drifted out of its case again.", "The pocket planetarium"),
    ("The clockmaker", "Someone has ordered a spare Thursday.", "The clock workshop"),
    ("The pastry chef", "Careful with the cake. It has six storeys.", "The sugar salon"),
    ("The explorer", "My sled dogs heard snow behind these doors.", "The winter camp"),
    ("The cellist", "The audience is seated. I have the final note.", "The velvet stage"),
    ("The librarian", "This atlas has started writing itself.", "The endless library"),
    ("The diver", "Tonight the jellyfish are giving a recital.", "The glass ocean"),
    ("The early riser", "A table for one, just above the clouds.", "The sunrise terrace"),
]


def randomInt(level):
    return random.randint(*LEVELS[level])


def decideOperation():
    return random.choice(("+", "−"))


def isCorrect(answer, destination):
    return answer == destination


class Hotel:
    def __init__(self, root):
        self.root = root
        root.title("Floor Zero  ·  The Impossible Hotel")
        root.resizable(False, False)
        self.c = tk.Canvas(root, width=900, height=540, bg=INK, highlightthickness=0)
        self.c.pack()
        self.art = {p.stem: tk.PhotoImage(file=str(p)) for p in ASSETS.glob("*.png")}
        self.best, self.muted = {}, False
        root.iconphoto(True, self.art["crest"])
        if winsound:
            root.iconbitmap(str(ASSETS / "hotel.ico"))
        self.music_on = True
        self.player = ctypes.windll.winmm.mciSendStringW if winsound else None
        if self.player and self.player(f'open "{ASSETS / "lounge.wav"}" type waveaudio alias hotelradio', None, 0, 0):
            self.player = None
        root.bind("<Destroy>", lambda e: self.radio("close hotelradio") if e.widget is root else None)
        self.loop_music()
        self.home()

    def text(self, x, y, value, size=15, color=IVORY, face="Georgia", **opts):
        return self.c.create_text(x, y, text=value, anchor="nw", fill=color,
                                  font=(face, -size), **opts)

    def image(self, x, y, name):
        return self.c.create_image(x, y, image=self.art[str(name)], anchor="nw")

    def button(self, x, y, w, h, title, action, color=PANEL):
        b = tk.Button(self.c, text=title, command=action, bg=color, fg=IVORY, bd=0,
                      activebackground="#685540", activeforeground=IVORY, cursor="hand2",
                      font=("Segoe UI", -15, "bold"), relief="flat", highlightthickness=0)
        if len(title) == 1:
            b.config(image=self.art["keycap"], compound="center", fg=GOLD)
        b.bind("<Enter>", lambda _: b.config(bg="#655a43"))
        b.bind("<Leave>", lambda _: b.config(bg=color))
        self.c.create_window(x, y, window=b, anchor="nw", width=w, height=h)
        return b

    def clear(self):
        self.root.unbind("<Return>")
        self.c.delete("all")
        for w in self.c.winfo_children():
            w.destroy()

    def sound(self, name):
        if self.muted:
            return
        if winsound:
            try:
                winsound.PlaySound(str(ASSETS / (name + ".wav")), winsound.SND_FILENAME | winsound.SND_ASYNC)
            except RuntimeError:
                pass
        elif name in ("bell", "finish"):
            self.root.bell()

    def radio(self, command):
        if self.player:
            result = ctypes.create_unicode_buffer(64)
            self.player(command, result, len(result), 0)
            return result.value

    def mix(self):
        if not self.player:
            return
        mode = self.radio("status hotelradio mode")
        if self.muted or not self.music_on:
            if mode == "playing":
                self.radio("pause hotelradio")
        elif mode in ("stopped", "paused"):
            self.radio("resume hotelradio" if mode == "paused" else "play hotelradio from 0")

    def loop_music(self):
        if self.player:
            self.mix()
            self.root.after(300, self.loop_music)

    def audio(self):
        def toggle(music):
            if music:
                self.music_on = not self.music_on
                radio.config(text="Radio on" if self.music_on else "Radio off")
            else:
                self.muted = not self.muted
                master.config(text="Sound off" if self.muted else "Sound on")
                if winsound and self.muted:
                    winsound.PlaySound(None, 0)
            self.mix()
        master = self.button(802, 12, 82, 28, "Sound off" if self.muted else "Sound on", lambda: toggle(False))
        if self.player:
            radio = self.button(712, 12, 84, 28, "Radio on" if self.music_on else "Radio off", lambda: toggle(True))

    def home(self):
        self.clear()
        self.image(0, 0, "title")
        self.text(40, 507, "Radio  ·  Local Forecast – Elevator / Kevin MacLeod", 12, GOLD, "Segoe UI")
        self.button(36, 435, 200, 48, "Enter the hotel   →", self.displayMenu, WINE)
        self.root.bind("<Return>", lambda _: self.displayMenu())
        self.audio()

    def displayMenu(self):
        self.clear()
        self.image(33, 22, "crest")
        self.text(95, 39, "F L O O R   Z E R O", 14, GOLD, "Bahnschrift")
        self.text(32, 80, "Choose your shift", 48)
        self.text(35, 153, "Guide ten guests. A first-stop arrival earns 10 points. A second stop earns 5.", 17)
        for i, (level, room) in enumerate(zip(LEVELS, (0, 2, 9))):
            x = 35 + 284*i
            self.image(x, 211, f"ticket{room}")
            self.button(x, 353, 262, 55, level + "   →", lambda choice=level: self.start(choice), WINE)
            low, high = LEVELS[level]
            detail = f"Operands {low:,}–{high:,}"
            if level in self.best:
                detail += f"   ·   Best {self.best[level]}/100"
            self.text(x, 421, detail, 15, GOLD, "Segoe UI")
        self.button(35, 480, 128, 34, "←   Lobby", self.home)
        self.audio()

    def start(self, level):
        self.level, self.scores = level, []
        self.guests = random.sample(range(10), 10)
        self.displayProblem()

    def displayProblem(self):
        if len(self.scores) == 10:
            return self.displayResults()
        self.clear()
        self.guest = self.guests[len(self.scores)]
        name, quote, _ = GUESTS[self.guest]
        a, b, op = randomInt(self.level), randomInt(self.level), decideOperation()
        self.target = a + b if op == "+" else a - b
        self.floor, self.take, self.state = a, 1, "answer"
        self.room = self.image(125, 114, 10)
        self.doors = [self.image(x, 114, side) for x, side in [(125,"left"), (238,"right")]]
        self.image(0, 0, "wall")
        self.image(480, 0, "console")
        self.needle = self.c.create_line(239, 94, 239, 29, fill="#f4cb80", width=3)
        self.indicator = self.c.create_text(240, 526, fill=GOLD, font=("Consolas", -20))
        self.dial(a)
        self.text(505, 27, f"{self.level.upper()}   /   GUEST {len(self.scores)+1:02d} OF 10", 14, GOLD, "Bahnschrift")
        self.text(503, 69, name, 37)
        self.text(505, 121, f"“{quote}”", 18, IVORY, "Georgia", width=362)
        self.text(505, 188, "REQUEST   /   " + ("GO UP" if op == "+" else "GO DOWN"), 13, GOLD, "Bahnschrift")
        self.text(504, 210, f"{a}  {op}  {b}  =", 34)
        self.number = tk.StringVar()
        self.entry = tk.Entry(self.c, textvariable=self.number, justify="center", bg="#fbf0d8",
                              fg=INK, font=("Consolas", -26), bd=0)
        self.c.create_window(505, 271, anchor="nw", window=self.entry, width=224, height=40)
        self.go = self.button(738, 271, 132, 40, "GO   ↵", self.dispatch, WINE)
        for i, symbol in enumerate("123456789±0⌫"):
            self.button(505+(i%3)*76, 320+(i//3)*37, 71, 33, symbol, lambda s=symbol: self.key(s))
        self.points = self.text(743, 327, f"{sum(self.scores)} / 100", 21, GOLD)
        self.text(743, 360, "SHIFT SCORE", 12, GOLD, "Bahnschrift")
        self.lamps()
        self.feedback = self.text(505, 475, "Enter a floor number or use the keypad.", 17, IVORY, "Segoe UI", width=370)
        self.entry.focus_set()
        self.root.bind("<Return>", lambda _: self.dispatch())
        self.audio()

    def lamps(self):
        self.c.delete("lamp")
        for i in range(10):
            x, y = 746 + (i % 5)*22, 402 + (i//5)*20
            fill = {10: GOLD, 5: "#86ad9b", 0: "#bc6b5e"}[self.scores[i]] if i < len(self.scores) else PANEL
            self.c.create_oval(x, y, x+10, y+10, fill=fill, outline="#91866b", tags="lamp")

    def key(self, symbol):
        if self.state != "answer":
            return
        value = self.number.get()
        if symbol == "⌫":
            value = value[:-1]
        elif symbol == "±":
            value = value[1:] if value.startswith("-") else "-" + value
        elif len(value) < 6:
            value += symbol
        self.number.set(value)
        self.sound("key")
        self.entry.focus_set()

    def dispatch(self):
        if self.state == "next":
            return self.displayProblem()
        if self.state != "answer":
            return
        try:
            floor = int(self.number.get())
            if abs(floor) > 99999:
                raise ValueError
        except ValueError:
            self.c.itemconfig(self.feedback, text="Enter a whole floor from −99,999 to 99,999.")
            return
        self.state = "riding"
        self.entry.config(state="disabled")
        self.go.config(state="disabled")
        self.c.itemconfig(self.feedback, text="Lift in motion…")
        self.sound("ride")
        self.travel(floor, 0)

    def dial(self, floor):
        limit = 2 * LEVELS[self.level][1]
        angle = math.radians(90 - 69 * max(-1, min(1, floor / limit)))
        self.c.coords(self.needle, 239, 94, 239+66*math.cos(angle), 94-66*math.sin(angle))
        self.c.itemconfig(self.indicator, text=f"FLOOR   {floor}")

    def travel(self, floor, tick):
        # Close after a retry, move the counter, then slide both doors behind the facade.
        gap = max(0, 1-tick/5) if self.take == 2 else 0
        gap = max(gap, min(1, max(0, (tick-15)/10)))
        for door, x, direction in zip(self.doors, (125,238), (-1,1)):
            self.c.coords(door, x + direction*113*gap, 114)
        progress = min(1, max(0, (tick-5)/10))
        shown = round(self.floor + (floor-self.floor)*progress)
        self.dial(shown)
        if tick == 6:
            self.c.itemconfig(self.room, image=self.art[str(self.guest if isCorrect(floor,self.target) else 10)])
        if tick == 25:
            return self.arrive(floor)
        self.root.after(30, self.travel, floor, tick+1)

    def arrive(self, floor):
        self.floor = floor
        correct = isCorrect(floor, self.target)
        self.sound("bell" if correct else "miss")
        self.go.config(state="normal")
        if not correct and self.take == 1:
            self.state, self.take = "answer", 2
            distance = self.target-floor
            direction = "up" if distance > 0 else "down"
            message = f"Wrong landing. Go {direction} {abs(distance):,} more. Enter the new floor."
            self.entry.config(state="normal")
            self.number.set("")
            self.entry.focus_set()
        else:
            points = (10 if self.take == 1 else 5) if correct else 0
            self.scores.append(points)
            self.lamps()
            self.state = "next"
            room = GUESTS[self.guest][2]
            message = f"{room}. Guest delivered!  +{points}" if correct else f"Missed stop. {room} was on floor {self.target}."
            self.c.itemconfig(self.points, text=f"{sum(self.scores)} / 100")
            self.go.config(text="Finish shift" if len(self.scores)==10 else "Next guest   →")
        self.c.itemconfig(self.feedback, text=message)

    def displayResults(self):
        self.clear()
        score = sum(self.scores)
        self.best[self.level] = max(score, self.best.get(self.level, 0))
        grade = next(g for mark,g in [(91,"A+"),(80,"A"),(70,"B"),(60,"C"),(50,"D"),(0,"F")] if score >= mark)
        self.image(125, 114, 11)
        self.image(0, 0, "wall")
        self.image(480, 0, "console")
        self.text(507, 75, "H O T E L   R E G I S T E R", 14, GOLD, "Bahnschrift")
        self.text(505, 116, "Shift complete", 43)
        self.text(507, 200, f"{score} / 100", 47, GOLD)
        self.text(507, 272, f"Grade {grade}    ·    {self.level} best {self.best[self.level]}/100", 19)
        self.text(507, 326, f"{self.scores.count(10)} first stops   ·   {self.scores.count(5)} second stops\n{self.scores.count(0)} missed destinations", 17)
        self.button(507, 419, 178, 43, "Another shift", self.displayMenu, WINE)
        self.button(694, 419, 122, 43, "Lobby", self.home)
        self.audio()
        self.sound("finish")


if __name__ == "__main__":
    window = tk.Tk()
    Hotel(window)
    window.mainloop()
