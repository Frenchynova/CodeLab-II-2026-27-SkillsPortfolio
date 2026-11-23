"""Run python -m unittest test_register in the Exercise 3 folder."""
import json
import tempfile
import unittest
from pathlib import Path
from student_data import results, save_students, load_students, validate_students


class RegisterTests(unittest.TestCase):
    def test_each_grade_boundary(self):
        for minimum, below, above in [(64,"F","D"), (80,"D","C"), (96,"C","B"), (112,"B","A")]:
            for total, expected in [(minimum-1, below), (minimum, above)]:
                with self.subTest(total=total):
                    s = results(dict(coursework=[20,20,20], exam=total-60))
                    self.assertEqual(s["grade"], expected)
                    if total < minimum:
                        self.assertEqual(s["gap"], 1)
        self.assertEqual(results(dict(coursework=[20]*3, exam=52))["gap"], 0)

    def test_files_and_validation(self):
        student = dict(number=1001, name="Demo, Student", coursework=[20]*3, exam=51)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            save_students([student], folder)
            updated = dict(student, exam=52)
            save_students([updated], folder)
            with self.assertRaises(ValueError):
                save_students([updated, updated], folder)
            self.assertEqual(load_students(folder), [updated])
            self.assertEqual(json.loads((folder/"studentMarks.json").read_text())["students"], [updated])
            self.assertIn(",51", (folder/"studentMarks.txt.bak").read_text())
            (folder/"studentMarks.txt").unlink()
            self.assertEqual(load_students(folder), [updated])
            save_students([], folder)
            self.assertEqual(load_students(folder), [])
        with self.assertRaises(ValueError):
            validate_students([dict(student, exam=101)])


if __name__ == "__main__":
    unittest.main()
