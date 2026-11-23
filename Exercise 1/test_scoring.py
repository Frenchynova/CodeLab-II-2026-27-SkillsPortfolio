"""Run with: python -m unittest test_scoring"""
import runpy
import unittest
from pathlib import Path

quiz = runpy.run_path(str(Path(__file__).with_name("01-MathsQuiz.py")))
assess = quiz["assess_attempt"]


class ScoringTests(unittest.TestCase):
    def test_first_try(self):
        self.assertEqual(assess(-2, -2, 1, "Beach")[0], 10)

    def test_first_miss(self):
        for floor, hint in [(2, "down 4"), (-5, "up 3")]:
            with self.subTest(floor=floor):
                points, feedback = assess(floor, -2, 1, "Beach")
                self.assertIsNone(points)
                self.assertIn(hint, feedback)

    def test_second_try(self):
        self.assertEqual(assess(-2, -2, 2, "Beach")[0], 5)

    def test_second_miss(self):
        points, feedback = assess(0, -2, 2, "Beach")
        self.assertEqual(points, 0)
        self.assertIn("floor -2", feedback)


if __name__ == "__main__":
    unittest.main()
