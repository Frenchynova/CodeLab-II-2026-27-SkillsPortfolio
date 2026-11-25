"""Run this file to open the class register."""
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from student_data import FOLDER, GRADE_BANDS, validate_marks, validate_students, load_students, results, save_students, sync_json

BG, WHITE, INK = "#f1ecdf", "#fffaf0", "#202d3a"
BLUE, MUTED, LINE = "#784135", "#545d60", "#d3cbbb"


class StudentManager:
    def __init__(self, root, folder=FOLDER):
        self.root, self.folder = root, Path(folder)
        self.marks_path = self.folder / "studentMarks.txt"
        self.sort_key, self.descending = "number", False
        self.query = tk.StringVar()
        root.title("Class Ledger · Student Manager")
        self.logo = tk.PhotoImage(file=str(Path(__file__).with_name("ledger.png")))
        root.iconphoto(True, self.logo)
        root.geometry("1080x690")
        root.minsize(980, 675)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, borderwidth=0, font=("Segoe UI", 10),
                        foreground=INK, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", background=INK, foreground=WHITE,
                        font=("Segoe UI", 9, "bold"), padding=6, relief="flat")
        style.map("Treeview.Heading", background=[("active", "#394654")])
        style.map("Treeview", background=[("selected", "#cfdbdf")], foreground=[("selected", INK)])
        main = tk.Frame(root, bg=BG, padx=22, pady=14)
        main.pack(fill="both", expand=True)
        head = tk.Frame(main, bg=BG)
        head.pack(fill="x", pady=(0, 10))
        tk.Label(head, text="Class Ledger", font=("Palatino Linotype", 31), bg=BG, fg=INK, image=self.logo, compound="left", padx=8).pack(side="left")
        self.summary = self.label(head, "", 10, MUTED)
        self.summary.pack(side="right")
        tk.Frame(main, height=2, bg=INK).pack(fill="x", pady=(0, 12))
        bar = tk.Frame(main, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.label(bar, "Name or number", 10).pack(side="left", padx=(0, 6))
        entry = ttk.Entry(bar, textvariable=self.query, width=19)
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        root.bind("<Control-f>", lambda _: (entry.focus_set(), entry.selection_range(0, "end")))
        entry.bind("<Return>", lambda event: self.set_filter("search"))
        for title, mode in [("Find", "search"), ("All", "all"), ("Highest", "highest"), ("Lowest", "lowest")]:
            self.button(bar, title, lambda m=mode: self.set_filter(m), False).pack(side="left", padx=3)

        self.titles = dict(number="Number", name="Student", coursework_total="Coursework /60",
                           exam="Exam /100", percentage="Overall %", grade="Grade")
        spread = tk.Frame(main, bg=BG)
        spread.pack(fill="both", expand=True)
        margin = tk.Frame(spread, bg=INK, width=211, padx=12, pady=8)
        margin.pack(side="right", fill="y", padx=(12, 0))
        margin.pack_propagate(False)
        self.label(margin, "Grade index", 16, WHITE).pack(anchor="w")
        self.bands = {}
        for grade, _ in GRADE_BANDS:
            btn = self.button(margin, grade, lambda g=grade: self.set_filter(g), False)
            btn.configure(anchor="w", font=("Consolas", -14), padx=8, pady=1)
            btn.pack(fill="x", pady=(3, 0))
            self.bands[grade] = btn
        tk.Frame(margin, height=1, bg="#626969").pack(fill="x", pady=8)
        self.label(margin, "Record notes", 15, WHITE).pack(anchor="w")
        self.note = self.label(margin, "", 10, "#ece1cb")
        self.note.configure(wraplength=179, justify="left", font=("Segoe UI", -14))
        self.note.pack(anchor="w", pady=5)
        grid = tk.Frame(spread)
        grid.pack(side="left", fill="both", expand=True)
        self.table = ttk.Treeview(grid, columns=list(self.titles), show="headings", selectmode="browse")
        for key, title in self.titles.items():
            self.table.heading(key, text=title, command=lambda k=key: self.sort(k))
            self.table.column(key, width={"name": 139, "coursework_total": 151}.get(key, 81), minwidth=48, anchor="w" if key == "name" else "center")
        scroll = ttk.Scrollbar(grid, command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)
        self.table.tag_configure("alternate", background="#f3eee4")
        self.table.bind("<Double-1>", lambda e: self.view_selected() if self.table.identify_row(e.y) else None)
        self.table.bind("<<TreeviewSelect>>", self.annotate)
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

    def label(self, parent, text, size=11, color=INK, bold=False, **options):
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                        font=("Palatino Linotype" if size >= 15 else "Segoe UI", size, "bold" if bold else "normal"), **options)

    def button(self, parent, text, command, primary=True):
        return tk.Button(parent, text=text, command=command, bg=BLUE if primary else "#E5E3D8",
                         fg=WHITE if primary else INK, relief="flat", bd=0, padx=12, pady=6, cursor="hand2")

    def reload(self):
        try:
            self.students = load_students(self.folder)
           
            if not self.marks_path.exists():
                warning = save_students(self.students, self.folder)
            else:
                warning = "TXT and JSON are up to date."
                try:
                    sync_json(self.students, self.folder)
                except OSError:
                    warning = "Records loaded; JSON could not be updated. Check folder permissions."
            self.source_bytes = self.marks_path.read_bytes()
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

        # Summarise the whole class before narrowing the rows shown in the table.
        rows = [results(s) for s in self.students]
        percentages = [s["percentage"] for s in rows]
        average = f"{sum(percentages)/len(rows):.1f}%" if rows else "—"
        extent = f"{min(percentages):.1f}–{max(percentages):.1f}%" if rows else "—"
        self.summary.configure(text=f"{len(rows)} students     /     Class mean {average}     /     Range {extent}")
        for grade, btn in self.bands.items():
            count = sum(s["grade"] == grade for s in rows)
            bars = round(9 * count / len(rows)) if rows else 0
            btn.configure(text=f"{grade}   {'━'*bars:<9} {count:>3}", bg=BLUE if self.filter == grade else "#e6decc",
                          fg=WHITE if self.filter == grade else INK)
        if self.filter in self.bands:
            rows = [s for s in rows if s["grade"] == self.filter]
        if self.filter == "search":
            query = self.query.get().strip().casefold()
            rows = [s for s in rows if query in s["name"].casefold() or query == str(s["number"])]
        elif rows and self.filter in ("highest", "lowest"):

            # Compare every total with the extreme so tied students appear together.
            target = (max if self.filter == "highest" else min)(s["total"] for s in rows)
            rows = [s for s in rows if s["total"] == target]
        rows.sort(key=lambda s: s[self.sort_key].casefold() if isinstance(s[self.sort_key], str)
                  else s[self.sort_key], reverse=self.descending)
        self.table.delete(*self.table.get_children())
        for index, s in enumerate(rows):
            self.table.insert("", "end", iid=str(s["number"]), values=(s["number"], s["name"],
                              s["coursework_total"], s["exam"], f'{s["percentage"]:.2f}%', s["grade"]),
                              tags=("alternate",) if index % 2 else ())
        for key, title in self.titles.items():
            arrow = (" ▼" if self.descending else " ▲") if key == self.sort_key else ""
            self.table.heading(key, text=title + arrow)
        view = {"all": "All records", "search": "Search results", "highest": "Highest score (including ties)",
                "lowest": "Lowest score (including ties)"}.get(self.filter, f"Grade {self.filter}")
        self.status.configure(text=f"{view} · {len(rows)} of {len(self.students)} students shown.")

        self.annotate()

    def annotate(self, event=None):
        student = self.selected(prompt=False)
        if student:
            s = results(student)
            gap = s["gap"]
            detail = f"{gap} more mark{'s' if gap != 1 else ''} to the next grade." if gap else "Top grade band."
            marks = " + ".join(map(str, s["coursework"]))
            note = f"{s['name']}\nCoursework {marks}\nExam {s['exam']}/100\n{detail}"
        else:
            note = "Select a student to see their mark breakdown."
        self.note.configure(text=note)

    def sort(self, key):
        self.descending = not self.descending if key == self.sort_key else False
        self.sort_key = key
        self.refresh()

    def selected(self, prompt=True):
        selection = self.table.selection()
        if selection:
            return next((s for s in self.students if s["number"] == int(selection[0])), None)
        if prompt:
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

            # If another editor changed the register, ask for a reload before saving.
            if self.marks_path.read_bytes() != self.source_bytes:
                raise ValueError("The TXT file changed outside the app. Reload files before editing.")
            message = save_students(candidates, self.folder)
        except (OSError, ValueError) as error:
            messagebox.showerror("Not saved", str(error), parent=self.root)
            return False
        self.students = candidates
        self.source_bytes = self.marks_path.read_bytes()
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
        dialog = tk.Toplevel(self.root, bg=WHITE, padx=26, pady=22)
        dialog.title("Edit student" if existing else "Add student")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        values = [student["number"], student["name"], *student["coursework"], student["exam"]] if existing else [""] * 6
        labels = ["Student number (1000–9999)", "Full name", "Coursework 1 /20", "Coursework 2 /20", "Coursework 3 /20", "Exam /100"]
        fields = [tk.StringVar(dialog, value=v) for v in values]
        entries = []
        for row, title in enumerate(labels):
            self.label(dialog, title).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=9)
            entry = ttk.Entry(dialog, textvariable=fields[row], font=("Segoe UI", 12), width=27)
            entry.grid(row=row, column=1, pady=9)
            entries.append(entry)
        def marks_from_form():
            try:
                marks = [int(field.get()) for field in fields[2:]]
            except ValueError:
                raise ValueError("Enter whole numbers for all four marks.") from None
            coursework, exam = marks[:3], marks[3]
            validate_marks(coursework, exam)
            return dict(coursework=coursework, exam=exam)

        def summary(record):
            s = results(record)
            return f"{s['total']}/160  ·  {s['percentage']:.2f}%  ·  Grade {s['grade']}"

        # Typing updates only the preview. Save still checks the complete class
        # (including duplicate numbers) before replacing either data file.
        preview = self.label(dialog, "", 11, BLUE, justify="left")
        preview.grid(row=6, column=0, columnspan=2, sticky="w")
        def update_preview(*_):
            before = f"Saved     {summary(student)}\n" if existing else ""
            try:
                after = summary(marks_from_form())
            except ValueError as error:
                after = str(error)
            preview.configure(text=before + "Preview   " + after)

        for field in fields[2:]:
            field.trace_add("write", update_preview)
        update_preview()
        error_label = self.label(dialog, "", 10, "#AB4037", wraplength=470)
        error_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=10)

        def submit():
            try:
                replacement = dict(number=int(fields[0].get()), name=fields[1].get().strip(), **marks_from_form())
                candidates = [replacement if s is student else s for s in self.students] if existing else self.students + [replacement]
                validate_students(candidates)
            except ValueError as error:
                error_label.configure(text=str(error))
                return
            if self.commit(candidates):
                dialog.destroy()
        self.button(dialog, "Cancel", dialog.destroy, False).grid(row=8, column=0, sticky="w")
        self.button(dialog, "Save student", submit).grid(row=8, column=1, sticky="e")
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
