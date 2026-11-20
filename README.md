# Daily Expense Tracker

A beginner-friendly Python 3.10+ terminal application for recording, searching and analysing daily expenses.

## Features
- Menu-driven terminal interface
- Validated amount, date, category and description inputs
- Automatic JSON persistence (`data/expenses.json`) and CSV mirror (`data/expenses.csv`)
- View and keyword-search expense records
- Monthly totals, transaction count, average and category breakdown
- Markdown monthly report export
- Matplotlib category chart export
- Handles missing or malformed JSON safely

## Run
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Optional: `python -m venv .venv`
4. Activate the environment.
5. Install chart dependency: `pip install -r requirements.txt`
6. Start: `python main.py`

The tracker works without Matplotlib; only chart generation requires it.

## Project structure
```
Daily_Expense_Tracker/
├── main.py
├── tracker.py
├── requirements.txt
├── README.md
├── data/
└── reports/
```
