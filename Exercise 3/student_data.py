import csv
import io
import json
import os
import tempfile
from pathlib import Path

FOLDER = Path(__file__).resolve().parent

def validate_students(students):
    """Reject invalid records before they can replace the data files."""
    if not isinstance(students, list):
        raise ValueError("Students must be a list.")
    codes = set()
    for student in students:
        if not isinstance(student, dict):
            raise ValueError("Each student must be a record.")
        code, name = student.get("number"), student.get("name")
        marks, exam = student.get("coursework"), student.get("exam")
        if type(code) is not int or not 1000 <= code <= 9999:
            raise ValueError("Student numbers must be integers from 1000 to 9999.")
        if code in codes:
            raise ValueError(f"Student number {code} is already in use.")
        codes.add(code)
        if not isinstance(name, str) or not name.strip() or any(ord(c) < 32 for c in name):
            raise ValueError("Enter a name without blank lines or control characters.")
        if not isinstance(marks, list) or len(marks) != 3 or any(
            type(mark) is not int or not 0 <= mark <= 20 for mark in marks
        ):
            raise ValueError("Enter three whole-number coursework marks from 0 to 20.")
        if type(exam) is not int or not 0 <= exam <= 100:
            raise ValueError("The exam mark must be a whole number from 0 to 100.")


def load_students(folder=FOLDER):
    """TXT is authoritative. Use JSON only when TXT is missing."""
    path = folder / "studentMarks.txt"
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as file:
            rows = [row for row in csv.reader(file) if any(v.strip() for v in row)]
        if not rows or len(rows[0]) != 1:
            raise ValueError("The first line must contain the class size.")
        count = int(rows[0][0])
        students = []
        for line, row in enumerate(rows[1:], 2):
            if len(row) != 6:
                raise ValueError(f"Line {line} must contain six comma-separated values.")
            students.append(dict(number=int(row[0]), name=row[1].strip(),
                                 coursework=[int(v) for v in row[2:5]], exam=int(row[5])))
    else:
        data = json.loads((folder / "studentMarks.json").read_text("utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("JSON must contain student_count and students.")
        count, students = data.get("student_count"), data.get("students")
    validate_students(students)
    if type(count) is not int or count != len(students):
        raise ValueError("The declared student count does not match the records.")
    return students


def results(student):
    coursework = sum(student["coursework"])
    total = coursework + student["exam"]
    percentage = total / 160 * 100
    grade = next(g for minimum, g in [(70, "A"), (60, "B"), (50, "C"), (40, "D"), (0, "F")]
                 if percentage >= minimum)
    return dict(student, coursework_total=coursework, total=total, percentage=percentage, grade=grade)


def atomic_write(path, content):
    """Replace a file only after its new contents have been written successfully."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def sync_json(students, folder=FOLDER):
    payload = {"student_count": len(students), "students": students}
    atomic_write(folder / "studentMarks.json", json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def save_students(students, folder=FOLDER):
    """Save TXT, keeping the previous TXT as a backup; then update the JSON mirror."""
    validate_students(students)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow([len(students)])
    for s in students:
        writer.writerow([s["number"], s["name"], *s["coursework"], s["exam"]])
    path = folder / "studentMarks.txt"
    if path.exists():
        atomic_write(folder / "studentMarks.txt.bak", path.read_text("utf-8-sig"))
    atomic_write(path, output.getvalue())
    try:
        sync_json(students, folder)
    except OSError:
        return "TXT saved, but JSON could not be updated. Reload to try syncing it again."
    return "Changes saved to TXT and JSON."


