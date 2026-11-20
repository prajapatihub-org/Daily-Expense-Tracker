import csv
import json
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports"
JSON_FILE = DATA_DIR / "expenses.json"
CSV_FILE = DATA_DIR / "expenses.csv"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Education", "Health", "Entertainment", "Other"]

class ExpenseTracker:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        REPORT_DIR.mkdir(exist_ok=True)
        self.expenses = self.load_data()

    def load_data(self):
        if not JSON_FILE.exists():
            return []
        try:
            data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("Expense data must be a list")
            return [x for x in data if self.valid_record(x)]
        except (json.JSONDecodeError, OSError, ValueError):
            print("Warning: expense file is missing or damaged. Starting with an empty list.")
            return []

    @staticmethod
    def valid_record(item):
        try:
            datetime.strptime(item["date"], "%Y-%m-%d")
            return float(item["amount"]) > 0 and bool(item["category"]) and bool(item["description"])
        except (KeyError, TypeError, ValueError):
            return False

    def save_data(self):
        JSON_FILE.write_text(json.dumps(self.expenses, indent=2), encoding="utf-8")
        with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "amount", "category", "description"])
            writer.writeheader()
            writer.writerows(self.expenses)

    def ask_amount(self):
        while True:
            raw = input("Amount (₹): ").strip()
            try:
                value = float(raw)
                if value <= 0 or value > 10000000:
                    raise ValueError
                return round(value, 2)
            except ValueError:
                print("Enter a valid amount greater than 0 and not above 1 crore.")

    def ask_date(self):
        while True:
            raw = input("Date (YYYY-MM-DD, blank for today): ").strip()
            if not raw:
                return date.today().isoformat()
            try:
                return datetime.strptime(raw, "%Y-%m-%d").date().isoformat()
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD.")

    def add_expense(self):
        print("\n--- Add Expense ---")
        amount = self.ask_amount()
        print("Categories:", ", ".join(CATEGORIES))
        while True:
            category = input("Category: ").strip().title()
            if category in CATEGORIES:
                break
            print("Choose one of the listed categories.")
        description = input("Description: ").strip()
        while not description or len(description) > 100:
            print("Description is required (maximum 100 characters).")
            description = input("Description: ").strip()
        entry = {
            "id": max([e.get("id", 0) for e in self.expenses], default=0) + 1,
            "date": self.ask_date(), "amount": amount,
            "category": category, "description": description
        }
        self.expenses.append(entry)
        self.save_data()
        print("Expense saved successfully.")

    def show_expenses(self, records=None):
        records = self.expenses if records is None else records
        if not records:
            print("No matching expenses found.")
            return
        print(f"\n{'ID':<5} {'DATE':<12} {'AMOUNT':>12} {'CATEGORY':<16} DESCRIPTION")
        print("-" * 75)
        for e in sorted(records, key=lambda x: (x["date"], x["id"]), reverse=True):
            print(f"{e['id']:<5} {e['date']:<12} ₹{float(e['amount']):>10.2f} {e['category']:<16} {e['description']}")
        print(f"\nRecords: {len(records)}")

    def search(self):
        term = input("Search description/category keyword: ").strip().lower()
        if not term:
            print("Search term cannot be blank.")
            return
        self.show_expenses([e for e in self.expenses if term in e["description"].lower() or term in e["category"].lower()])

    def monthly_summary(self):
        month = input("Month (YYYY-MM, blank for current month): ").strip()
        if not month:
            month = date.today().strftime("%Y-%m")
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            print("Invalid month. Use YYYY-MM.")
            return
        rows = [e for e in self.expenses if e["date"].startswith(month)]
        total = sum(float(e["amount"]) for e in rows)
        avg = total / len(rows) if rows else 0
        by_category = defaultdict(float)
        for e in rows:
            by_category[e["category"]] += float(e["amount"])
        print(f"\n--- Summary for {month} ---")
        print(f"Transactions : {len(rows)}")
        print(f"Total spent  : ₹{total:,.2f}")
        print(f"Average      : ₹{avg:,.2f}")
        if by_category:
            print("\nCategory breakdown:")
            for cat, value in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat:<18} ₹{value:,.2f}")
        else:
            print("No expenses recorded for this month.")

    def export_report(self):
        month = input("Month (YYYY-MM): ").strip()
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            print("Invalid month.")
            return
        rows = [e for e in self.expenses if e["date"].startswith(month)]
        total = sum(float(e["amount"]) for e in rows)
        path = REPORT_DIR / f"summary_{month}.md"
        lines = [f"# Expense Summary - {month}", "", f"- Transactions: {len(rows)}", f"- Total spent: ₹{total:,.2f}", "", "| Date | Amount | Category | Description |", "|---|---:|---|---|"]
        lines += [f"| {e['date']} | ₹{float(e['amount']):.2f} | {e['category']} | {e['description']} |" for e in rows]
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Report exported: {path.relative_to(ROOT)}")

    def plot_chart(self):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("Matplotlib is not installed. Run: pip install matplotlib")
            return
        if not self.expenses:
            print("Add expenses before creating a chart.")
            return
        totals = defaultdict(float)
        for e in self.expenses:
            totals[e["category"]] += float(e["amount"])
        plt.figure(figsize=(9, 5))
        plt.bar(totals.keys(), totals.values())
        plt.title("Spending by Category")
        plt.ylabel("Amount (₹)")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        path = REPORT_DIR / "category_spending.png"
        plt.savefig(path)
        plt.close()
        print(f"Chart saved: {path.relative_to(ROOT)}")

    def run(self):
        while True:
            print("\n================================")
            print("       DAILY EXPENSE TRACKER")
            print("================================")
            print("1. Add expense")
            print("2. View all expenses")
            print("3. Search expenses")
            print("4. Monthly summary")
            print("5. Export Markdown report")
            print("6. Generate category chart")
            print("7. Exit")
            choice = input("Choose an option (1-7): ").strip()
            if choice == "1": self.add_expense()
            elif choice == "2": self.show_expenses()
            elif choice == "3": self.search()
            elif choice == "4": self.monthly_summary()
            elif choice == "5": self.export_report()
            elif choice == "6": self.plot_chart()
            elif choice == "7":
                print("Thank you for using Daily Expense Tracker!")
                break
            else:
                print("Invalid option. Please enter a number from 1 to 7.")
