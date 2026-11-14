import tkinter as tk
from pathlib import Path


def load_students():
    students = []
    path = Path(__file__).resolve().parent / "studentMarks.txt"

    with path.open(encoding="utf-8-sig") as file:
        student_count = int(file.readline().strip())

        for line in file:
            if line.strip():
                details = line.strip().split(",")

                student = {
                    "number": int(details[0]),
                    "name": details[1],
                    "coursework": [
                        int(details[2]),
                        int(details[3]),
                        int(details[4])
                    ],
                    "exam": int(details[5])
                }

                students.append(student)

    return student_count, students


def show_students():
    output.delete("1.0", tk.END)

    try:
        student_count, students = load_students()
    except (OSError, ValueError, IndexError):
        output.insert(
            tk.END,
            "Could not read the student file.\n"
            "Check that studentMarks.txt is in the same folder "
            "and contains the correct data."
        )
        return

    output.insert(tk.END, f"Students in class: {student_count}\n\n")

    for student in students:
        coursework_total = sum(student["coursework"])

        output.insert(tk.END, f"Name: {student['name']}\n")
        output.insert(tk.END, f"Number: {student['number']}\n")
        output.insert(
            tk.END,
            f"Coursework: {coursework_total}/60\n"
        )
        output.insert(tk.END, f"Exam: {student['exam']}/100\n\n")


window = tk.Tk()
window.title("Student Manager")
window.geometry("550x500")

heading = tk.Label(
    window,
    text="Student Manager",
    font=("Arial", 20)
)
heading.pack(pady=15)

view_button = tk.Button(
    window,
    text="View all students",
    command=show_students
)
view_button.pack(pady=5)

output = tk.Text(
    window,
    width=58,
    height=20,
    font=("Arial", 11),
    wrap="word"
)
output.pack(padx=15, pady=15, fill="both", expand=True)

window.mainloop()