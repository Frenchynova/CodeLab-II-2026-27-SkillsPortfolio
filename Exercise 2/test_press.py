"""Run with python -m unittest test_press from the Exercise 2 folder."""
import runpy
import tempfile
import unittest
from pathlib import Path

app = runpy.run_path(str(Path(__file__).with_name("02-joke_teller.py")))


class PressTests(unittest.TestCase):
    def test_mixed_joke_file(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "jokes.txt"
            file.write_text("First?One!\nInvalid line\nFirst?One!\nSecond?Really? Yes.\n",
                            encoding="utf-8-sig")
            self.assertEqual(app["read_jokes"](file), [("First?", "One!"), ("Second?", "Really? Yes.")])

    def test_export_preserves_print_order_and_literal_text(self):
        booklet = app["zine_html"]([("First?", "Tea & toast"), ("Second?", "<b>bold</b>")])
        self.assertIn("Tea &amp; toast", booklet)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt;", booklet)
        self.assertLess(booklet.index("First?"), booklet.index("Second?"))


if __name__ == "__main__":
    unittest.main()
