# Floor Zero test sheet

Run `python -m unittest test_scoring` in this folder to check the four scoring outcomes without opening the game.

| Case | Input | Expected | Observed |
|---|---|---|---|
| Invalid text | Enter hello | Stay on take one with no recorded stop | Passed |
| Negative destination | For 4 − 6, try 2 | Hint says to go down 4 floors | Passed |
| Correct retry | Next enter -2 | Award 5 points and log both floors | Passed |
| Shift receipt | Finish the other nine guests on take one | Show 95/100, ten entries, and stops 2 → -2 for the first guest | Passed |
| Full rounds | First-try answers, second-try answers, or two misses throughout | Final scores of 100, 50, and 0 respectively | Passed |

For a live demo, choose Easy and use any question: enter a word, then an incorrect floor, then the correct floor. At the end of the shift open **Review shift receipt** and find that guest.
