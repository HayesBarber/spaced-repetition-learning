# 🧠 `srl` — Spaced Repetition Learning CLI

A lightweight command-line tool for mastering LeetCode-style data structures and algorithm problems using **spaced repetition**.

## 📚 Overview

This tool helps you practice LeetCode problems more effectively using spaced repetition. When you attempt a problem, rate yourself from `1-5`:

| Rating | Meaning                            | Next Attempt |
| ------ | ---------------------------------- | ------------ |
| 1      | Couldn’t solve / needed a solution | 1 day        |
| 2      | Solved with significant struggle   | 2 days       |
| 3      | Solved with minor struggle         | 3 days       |
| 4      | Solved smoothly with few gaps      | 4 days       |
| 5      | Solved perfectly, confidently      | 5 days       |

If you rate a problem `5` two times in a row, it’s considered mastered and moved to the **mastered list**.

## 💾 Data Storage

Your progress is saved to:

```

~/.srl/problems_in_progress.json
~/.srl/problems_mastered.json

```

These files are created automatically.

## ⚡ Installation

1. Clone the repo:

```bash
git clone https://github.com/HayesBarber/spaced-repetition-learning.git
```

2. Create an alias for ease of use:

```bash
alias spl="python3 /path/to/src/cli.py"
```

Now you can run `srl` from anywhere.

## 🧑‍💻 Usage

### Add or Update a Problem Attempt

```bash
srl add "Two Sum" 3
```

- Adds a new attempt or updates an existing one.
- Rating must be between `1` and `5`.

---

### List Problems Due Today

```bash
srl list
```

Lists all problems scheduled for today, sorted by:

1. Earliest last attempt.
2. Lower ratings first.

You can limit the number of problems shown:

```bash
srl list -n 3
```

---

### View Mastered Problems

```bash
srl mastered
```

Shows all problems you’ve marked as mastered (achieved `5` twice in a row).

You can show the count of mastered problems by passing in the `-c` flag.

```bash
srl mastered -c
```

---

### Manage the Next Up Queue

Add problems to your Next Up queue — problems you'd like to tackle next when nothing is due:

```bash
srl nextup add "Sliding Window Maximum"
```

List problems in the queue:

```bash
srl nextup list
```

---

## 💡 Example Workflow

1. Solve a LeetCode problem.
2. Run:

```bash
srl add "Merge Intervals" 2
```

3. The next day, check what to review:

```bash
srl list
```

4. Rinse and repeat until mastery!
