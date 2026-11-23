"""Run this file to open the class register."""
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from student_data import FOLDER, validate_students, load_students, results, save_students, sync_json

BG, WHITE, INK = "#F6F4ED", "#FFFFFF", "#273B37"
BLUE, MUTED, LINE = "#315F53", "#52665F", "#DEE5EE"


class StudentManager:
    def __init__(self, root, folder=FOLDER):
        self.root, self.folder = root, Path(folder)
        self.students, self.loaded = [], False
        self.filter = "all"
        self.sort_key, self.descending = "number", False
        self.query = tk.StringVar()
        root.title("Student Manager")
        root.geometry("1120x780")
        root.minsize(980, 700)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 11), background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", WHITE)])

        head = tk.Frame(root, bg=INK, padx=28, pady=16)
        head.pack(fill="x")
        self.label(head, "Class register", 25, WHITE, True).pack(side="left")
        self.label(head, "Student Manager", 11, "#DAD8C9").pack(side="right")
        main = tk.Frame(root, bg=BG, padx=24, pady=16)
        main.pack(fill="both", expand=True)
        cards = tk.Frame(main, bg=BG)
        cards.pack(fill="x", pady=(0, 16))
        self.stats = []
        for title in ("Students", "Class average", "Highest mark", "Lowest mark"):
            card = tk.Frame(cards, bg=WHITE, padx=16, pady=8)
            card.pack(side="left", fill="x", expand=True, padx=3)
            self.label(card, title, 10, MUTED).pack(anchor="w")
            value = self.label(card, "—", 22, BLUE, True)
            value.pack(anchor="w")
            self.stats.append(value)

        bar = tk.Frame(main, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.label(bar, "Name or number", 10).pack(side="left", padx=(0, 6))
        entry = ttk.Entry(bar, textvariable=self.query, width=19)
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        entry.bind("<Return>", lambda event: self.set_filter("search"))
        for title, mode in [("Find", "search"), ("All", "all"), ("Highest", "highest"), ("Lowest", "lowest")]:
            self.button(bar, title, lambda m=mode: self.set_filter(m), False).pack(side="left", padx=3)

        self.titles = dict(number="Number", name="Student", coursework_total="Coursework /60",
                           exam="Exam /100", percentage="Overall %", grade="Grade")
        grid = tk.Frame(main)
        grid.pack(fill="both", expand=True)
        self.table = ttk.Treeview(grid, columns=list(self.titles), show="headings", selectmode="browse")
        for key, title in self.titles.items():
            self.table.heading(key, text=title, command=lambda k=key: self.sort(k))
            self.table.column(key, width=185 if key == "name" else 110, anchor="w" if key == "name" else "center")
        scroll = ttk.Scrollbar(grid, command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)
        self.table.tag_configure("alternate", background="#F3F2EB")
        self.table.bind("<Double-1>", lambda e: self.view_selected() if self.table.identify_row(e.y) else None)
        self.table.bind("<Return>", lambda e: self.view_selected())

        tools = tk.Frame(main, bg=BG)
        tools.pack(fill="x", pady=12)
        self.mutation_buttons = []
        for title, command in [("Add student", self.edit), ("Edit", lambda: self.edit(True)), ("Delete", self.delete)]:
            btn = self.button(tools, title, command, title == "Add student")
            btn.pack(side="left", padx=3)
            self.mutation_buttons.append(btn)
        self.button(tools, "View record", self.view_selected, False).pack(side="left", padx=3)
        self.button(tools, "Reload", self.reload, False).pack(side="right")
        self.status = self.label(main, "", 10, MUTED)
        self.status.pack(anchor="w")
        self.reload()

    def label(self, parent, text, size=11, color=INK, bold=False):
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def button(self, parent, text, command, primary=True):
        return tk.Button(parent, text=text, command=command, bg=BLUE if primary else "#E5E3D8",
                         fg=WHITE if primary else INK, relief="flat", padx=12, pady=7, cursor="hand2")

    def reload(self):
        try:
            self.students = load_students(self.folder)
           
            if not (self.folder / "studentMarks.txt").exists():
                warning = save_students(self.students, self.folder)
            else:
                warning = "TXT and JSON are up to date."
                try:
                    sync_json(self.students, self.folder)
                except OSError:
                    warning = "Records loaded; JSON could not be updated. Check folder permissions."
            self.source_bytes = (self.folder / "studentMarks.txt").read_bytes()
            self.loaded = True
        except (OSError, ValueError, UnicodeError) as error:
            self.students, self.loaded = [], False
            warning = f"Could not load records: {error}"
        for button in self.mutation_buttons:
            button.configure(state="normal" if self.loaded else "disabled")
        self.set_filter("all")
        self.status.configure(text=warning)

    def set_filter(self, mode):
        self.filter = mode
        if mode != "search":
            self.query.set("")
        self.refresh()

    def refresh(self):
        rows = [results(s) for s in self.students]
        percentages = [s["percentage"] for s in rows]
        values = [str(len(rows)), f"{sum(percentages) / len(rows):.2f}%" if rows else "—",
                  f"{max(percentages):.2f}%" if rows else "—", f"{min(percentages):.2f}%" if rows else "—"]
        for label, value in zip(self.stats, values):
            label.configure(text=value)
        if self.filter == "search":
            query = self.query.get().strip().casefold()
            rows = [s for s in rows if query in s["name"].casefold() or query == str(s["number"])]
        elif rows and self.filter in ("highest", "lowest"):
            target = (max if self.filter == "highest" else min)(s["total"] for s in rows)
            rows = [s for s in rows if s["total"] == target]
        rows.sort(key=lambda s: s[self.sort_key].casefold() if isinstance(s[self.sort_key], str)
                  else s[self.sort_key], reverse=self.descending)
        for item in self.table.get_children():
            self.table.delete(item)
        for index, s in enumerate(rows):
            self.table.insert("", "end", iid=str(s["number"]), values=(s["number"], s["name"],
                              s["coursework_total"], s["exam"], f'{s["percentage"]:.2f}%', s["grade"]),
                              tags=("alternate",) if index % 2 else ())
        for key, title in self.titles.items():
            arrow = (" ▼" if self.descending else " ▲") if key == self.sort_key else ""
            self.table.heading(key, text=title + arrow)
        view = {"all": "All records", "search": "Search results", "highest": "Highest score (including ties)",
                "lowest": "Lowest score (including ties)"}[self.filter]
        self.status.configure(text=f"{view} · {len(rows)} of {len(self.students)} students shown.")

    def sort(self, key):
        self.descending = not self.descending if key == self.sort_key else False
        self.sort_key = key
        self.refresh()

    def selected(self):
        selection = self.table.selection()
        if selection:
            return next(s for s in self.students if s["number"] == int(selection[0]))
        messagebox.showinfo("Select a student", "Click a student in the table first.", parent=self.root)

    def view_selected(self):
        student = self.selected()
        if student is None:
            return
        s = results(student)
        marks = " + ".join(map(str, s["coursework"]))
        messagebox.showinfo(s["name"], (
            f"Student {s['number']}   ·   Grade {s['grade']}\n\n"
            f"Coursework: {marks} = {s['coursework_total']}/60\n"
            f"Exam: {s['exam']}/100\n"
            f"Overall: {s['total']}/160 ({s['percentage']:.2f}%)"
        ), parent=self.root)

    def commit(self, candidates):
        try:
            if (self.folder / "studentMarks.txt").read_bytes() != self.source_bytes:
                raise ValueError("The TXT file changed outside the app. Reload files before editing.")
            message = save_students(candidates, self.folder)
        except (OSError, ValueError) as error:
            messagebox.showerror("Not saved", str(error), parent=self.root)
            return False
        self.students = candidates
        self.source_bytes = (self.folder / "studentMarks.txt").read_bytes()
        self.set_filter("all")
        self.status.configure(text=message)
        if message.startswith("TXT saved,"):
            messagebox.showwarning("JSON needs updating", message, parent=self.root)
        return True

    def edit(self, existing=False):
        if not self.loaded:
            return
        student = self.selected() if existing else None
        if existing and student is None:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit student" if existing else "Add student")
        dialog.configure(bg=WHITE, padx=26, pady=22)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        values = [student["number"], student["name"], *student["coursework"], student["exam"]] if existing else [""] * 6
        labels = ["Student number (1000–9999)", "Full name", "Coursework 1 /20", "Coursework 2 /20", "Coursework 3 /20", "Exam /100"]
        entries = []
        for row, (title, value) in enumerate(zip(labels, values)):
            self.label(dialog, title).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=9)
            entry = ttk.Entry(dialog, font=("Segoe UI", 12), width=27)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, pady=9)
            entries.append(entry)
        error_label = self.label(dialog, "", 10, "#AB4037")
        error_label.configure(wraplength=470)
        error_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=10)

        def submit():
            try:
                raw = [entry.get().strip() for entry in entries]
                replacement = dict(number=int(raw[0]), name=raw[1], coursework=[int(v) for v in raw[2:5]], exam=int(raw[5]))
                candidates = [replacement if s is student else s for s in self.students] if existing else self.students + [replacement]
                validate_students(candidates)
            except ValueError as error:
                error_label.configure(text=str(error))
                return
            if self.commit(candidates):
                dialog.destroy()
        self.button(dialog, "Cancel", dialog.destroy, False).grid(row=7, column=0, sticky="w")
        self.button(dialog, "Save student", submit).grid(row=7, column=1, sticky="e")
        entries[0].focus_set()

    def delete(self):
        if not self.loaded:
            return
        student = self.selected()
        if student is not None and messagebox.askyesno("Delete student?",
                f'Delete {student["name"]} ({student["number"]}) from the saved records?', parent=self.root):
            self.commit([s for s in self.students if s is not student])


if __name__ == "__main__":
    root = tk.Tk()
    StudentManager(root)
    root.mainloop()
