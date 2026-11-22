"""Second Impression — a two-colour joke press. Python 3 + Tkinter."""
import json
import random
import tkinter as tk
from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None

HERE = Path(__file__).resolve().parent
INK, RED, PAPER, DESK = "#262820", "#973827", "#fbf2dd", "#e6e0d1"
ZINE = Path.home() / ".second-impression" / "zine.json"


def read_jokes(path):
    pairs = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        setup, sep, answer = line.strip().partition("?")
        if sep and setup.strip() and answer.strip():
            pairs.append((setup.strip() + "?", answer.strip()))
    return list(dict.fromkeys(pairs))


class Press:
    def __init__(self, root):
        self.root = root
        root.title("Ink Dog Press  ·  Second Impression")
        root.resizable(False, False)
        self.c = tk.Canvas(root, width=900, height=550, bg=DESK, highlightthickness=0)
        self.c.pack()
        self.art = {p.stem: tk.PhotoImage(file=str(p)) for p in (HERE/"ink").glob("*.png")}
        root.iconphoto(True, self.art["mark"])
        try:
            self.jokes = read_jokes(HERE/"randomJokes.txt")
        except (OSError, UnicodeError):
            self.jokes = []
        try:
            saved = json.loads(ZINE.read_text(encoding="utf-8"))
            self.saved = []
            for pair in saved if isinstance(saved, list) else []:
                if isinstance(pair, list) and len(pair)==2 and all(isinstance(v,str) for v in pair):
                    if tuple(pair) not in self.saved:
                        self.saved.append(tuple(pair))
        except (OSError, ValueError):
            self.saved = []
        self.deck, self.current, self.turn = [], None, 0
        self.revealed, self.mute, self.timer = False, False, None
        self.page = None
        self.notice = ""
        self.draw()
        root.bind("<Return>", lambda _: self.reveal())
        root.bind("n", lambda _: self.next() if self.page is None else None)
        root.bind("<Escape>", lambda _: self.view(None))

    def text(self,x,y,s,size=15,color=INK,face="Georgia",**kw):
        return self.c.create_text(x,y,text=s,anchor="nw",fill=color,font=(face,-size),**kw)

    def button(self,x,y,w,h,s,fn,colour=INK):
        b=tk.Button(self.c,text=s,command=fn,font=("Segoe UI",-14,"bold"),relief="flat",
                    bd=0,bg=colour,fg=PAPER,activebackground="#505465",activeforeground="white",cursor="hand2")
        self.c.create_window(x,y,anchor="nw",width=w,height=h,window=b)
        return b

    def image(self,x,y,key):
        self.c.create_image(x,y,image=self.art[key],anchor="nw")

    def sound(self,key):
        if not self.mute and winsound:
            try:
                winsound.PlaySound(str(HERE/"ink"/(key+".wav")),winsound.SND_FILENAME|winsound.SND_ASYNC)
            except RuntimeError:
                pass

    def view(self,page):
        if self.timer:
            self.root.after_cancel(self.timer)
            self.timer=None
        self.page, self.notice = page, ""
        self.draw()

    def next(self):
        if not self.jokes or self.page is not None:
            return
        if not self.deck:
            self.deck=self.jokes.copy()
            random.shuffle(self.deck)
            if len(self.deck)>1 and self.deck[-1]==self.current:
                self.deck[0],self.deck[-1]=self.deck[-1],self.deck[0]
        self.current=self.deck.pop()
        self.turn+=1
        self.revealed=False
        self.view(None)
        self.sound("feed")
        self.c.addtag_enclosed("sheet", 324, 65, 879, 513)
        self.c.move("sheet", 12, 0)
        self.c.move("dog", 8, 0)
        def feed(steps):
            self.c.move("sheet", -3, 0)
            self.c.move("dog", -2, 0)
            self.timer = self.root.after(16, feed, steps-1) if steps>1 else None
        feed(4)

    def reveal(self):
        if not self.current or self.revealed or self.page is not None:
            return
        self.revealed=True
        self.sound("impress")
        self.draw()
        # The moving mask exposes the second ink layer from top to bottom.
        mask=self.c.create_rectangle(329,309,864,444,fill=PAPER,outline="")
        roller=self.c.create_line(332,309,834,309,fill=RED,width=3)
        def roll(y):
            self.c.coords(roller,332,y,834,y)
            self.c.coords(mask,329,y,864,444)
            if y<444:
                self.timer=self.root.after(16,roll,y+9)
            else:
                self.c.delete(mask,roller)
                self.timer=None
        roll(309)

    def bookmark(self,joke):
        updated=self.saved.copy()
        if joke in updated: updated.remove(joke)
        else: updated.append(joke)
        try:
            ZINE.parent.mkdir(parents=True,exist_ok=True)
            tmp=ZINE.with_suffix(".tmp")
            tmp.write_text(json.dumps(updated,ensure_ascii=False),encoding="utf-8")
            tmp.replace(ZINE)
        except OSError:
            self.notice="Couldn’t save your zine to disk."
        else:
            self.saved=updated
            self.sound("clip")
            self.notice="Clipped into your zine." if joke in updated else "Page removed."
            if self.page is not None: self.page=max(0,min(self.page,len(updated)-1))
        self.draw()

    def copy(self,joke):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(joke))
            self.notice="Joke copied."
        except tk.TclError:
            self.notice="Clipboard unavailable."
        self.draw()

    def toggle(self):
        self.mute=not self.mute
        self.draw()

    def draw(self):
        if self.timer:
            self.root.after_cancel(self.timer)
            self.timer=None
        self.c.delete("all")
        for w in self.c.winfo_children(): w.destroy()
        rect=self.c.create_rectangle
        self.image(0,0,"workbench")
        self.text(310,17,"Second Impression",25,INK,"Georgia")
        self.button(626,12,105,32,f"My zine ({len(self.saved)})",lambda:self.view(0))
        self.button(739,12,83,32,"Sound off" if self.mute else "Sound on",self.toggle)
        self.button(830,12,50,32,"Quit",self.root.destroy)
        self.c.create_line(310,54,876,54,fill=INK,width=1)
        browsing=self.page is not None
        joke=(self.saved[self.page] if self.saved else None) if browsing else self.current
        printed=browsing or self.revealed
        self.c.create_image(2,151,image=self.art["dog"+str(int(printed))],anchor="nw",tags="dog")
        self.text(21,307,"Your clippings" if browsing else "Fetch a joke.",22,INK,"Georgia")
        if browsing:
            self.button(24,340,241,46,"←  Back to press",lambda:self.view(None))
            for i in range(min(len(self.saved),24)):
                x,y=26+(i%12)*18,449+(i//12)*10
                rect(x,y,x+12,y+5,fill=(INK,RED)[i%2],outline="")
            if self.saved:
                for x,title,delta in [(24,"← Previous",-1),(150,"Next →",1)]:
                    self.button(x,399,116,37,title,lambda d=delta:self.view((self.page+d)%len(self.saved)))
        else:
            start=self.button(24,338,241,46,"Next Joke" if joke else "Alexa tell me a Joke",self.next)
            if not self.jokes: start.config(state="disabled")
            reveal=self.button(24,395,241,46,"Show Punchline",self.reveal,RED)
            if not joke or printed: reveal.config(state="disabled",disabledforeground="#ddc6b2")
        self.text(25,489,self.notice or (f"{len(self.saved)} saved prints" if browsing else
                  f"{len(self.jokes)} jokes in the drawer"),15,INK,"Consolas",width=248)
        number=(self.page+1 if self.saved else 0) if browsing else self.turn
        self.text(342,91,f'{"ZINE PAGE" if browsing else "PRESS SHEET"}   /   {number:03}',14,INK,"Consolas")
        kind="press"
        if joke:
            for word,art in [('boil a clown','pot'),('pizza','pizza'),('bike','bike'),('mushroom','fungi')]:
                if word in joke[0].lower(): kind=art; break
        self.image(669,63,kind+str(int(printed)))
        title=joke[0] if joke else ("Your first issue starts here." if browsing else "The dog has the paper.")
        self.text(339,186,title,34 if len(title)<50 else 26,width=514)
        self.c.create_line(340,293,848,293,fill="#b9ad97",dash=(4,4))
        answer=joke[1] if joke and printed else ("Save a revealed joke to add a page." if browsing else
               "Press Show Punchline for the second ink." if joke else
               "Ask for a joke to load the first sheet." if self.jokes else "Check randomJokes.txt beside the program.")
        self.text(338,324,answer,30 if joke and printed else 18,RED if printed else INK,width=505)
        if joke and printed:
            self.button(339,449,165,35,"Unclip favourite" if joke in self.saved else "Save favourite",
                        lambda:self.bookmark(joke))
            self.button(513,449,110,35,"Copy joke",lambda:self.copy(joke))
        self.c.create_line(340,497,847,497,fill=INK)



if __name__=="__main__":
    root=tk.Tk()
    Press(root)
    root.mainloop()
