#!/usr/bin/env python3
"""
Expense Tracker (Python + SQLite fallback)
Author: Himanshu Goswami
Date: 21-06-2025

Fallback version of command-line app to manage and track personal expenses using SQLite.
Use this version if cx_Oracle or Oracle DB is not available.
Adapted to run in non-interactive environments with predefined test data.
"""

import sqlite3
import csv
import os
from datetime import datetime

DB_FILE = "expenses.db"

# ──────────────────────────────────────────────────────────────────────────────
# DB Initialization
# ──────────────────────────────────────────────────────────────────────────────

def connect_db():
    return sqlite3.connect(DB_FILE)

def init_db():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT,
                category TEXT,
                amount REAL,
                note TEXT
            )
        """)
        conn.commit()
        print("[✓] SQLite database and table ready.")

# ──────────────────────────────────────────────────────────────────────────────
# Core Functions
# ──────────────────────────────────────────────────────────────────────────────

def add_expense_auto(date_str, category, amount, note):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")  # validate format
    except ValueError:
        print(f"[!] Invalid date format: {date_str}")
        return
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO expenses (expense_date, category, amount, note)
            VALUES (?, ?, ?, ?)
        """, (date_str, category, amount, note))
        conn.commit()
        print(f"[+] Expense added: {date_str}, {category}, ₹{amount}, {note}")

def view_expenses():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, expense_date, category, amount, note FROM expenses ORDER BY expense_date DESC")
        rows = cur.fetchall()
        if not rows:
            print("No expenses recorded.")
            return
        print("\n{:<4} {:<12} {:<15} {:<10} {:<30}".format("ID", "Date", "Category", "Amount", "Note"))
        print("-" * 75)
        for r in rows:
            print("{:<4} {:<12} {:<15} {:<10.2f} {:<30}".format(*r))
        print("-" * 75 + "\n")

def monthly_summary():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT substr(expense_date, 1, 7) AS month,
                   SUM(amount) AS total
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
        """)
        rows = cur.fetchall()
        if not rows:
            print("No data to summarize.")
            return
        print("\n{:<10} {:<10}".format("Month", "Total"))
        print("-" * 25)
        for month, total in rows:
            print(f"{month:<10} ₹{total:<10.2f}")
        print("-" * 25 + "\n")

def export_csv(fname="expenses.csv"):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT expense_date, category, amount, note FROM expenses")
        rows = cur.fetchall()
        if not rows:
            print("[!] No data to export.")
            return
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Note"])
            writer.writerows(rows)
        print(f"[✓] Exported to {os.path.abspath(fname)}")

# ──────────────────────────────────────────────────────────────────────────────
# Main Flow for Testing
# ──────────────────────────────────────────────────────────────────────────────

def main():
    init_db()

    # Predefined test data
    test_data = [
        ("2025-06-01", "Groceries", 450.0, "Weekly veggies"),
        ("2025-06-02", "Transport", 100.0, "Auto fare"),
        ("2025-06-03", "Snacks", 50.5, "Coffee and samosa"),
        ("2025-06-10", "Books", 600.0, "Python workbook"),
        ("2025-06-15", "Gym", 300.0, "Monthly fees")
    ]

    for date, cat, amt, note in test_data:
        add_expense_auto(date, cat, amt, note)

    view_expenses()
    monthly_summary()
    export_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[✘] Interrupted by user. Exiting...")
