"""Generate a realistic sample sales dataset and load it into SQLite."""
import csv
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "sample_sales_data.csv"
DB_PATH = DATA_DIR / "sales.db"

PRODUCTS = ["Laptop", "Smartphone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse", "Webcam"]
REGIONS = ["North", "South", "East", "West"]

PRODUCT_PRICE = {
    "Laptop": (800, 1500),
    "Smartphone": (400, 1000),
    "Tablet": (250, 600),
    "Headphones": (50, 200),
    "Monitor": (200, 600),
    "Keyboard": (30, 120),
    "Mouse": (15, 60),
    "Webcam": (40, 150),
}

MARGIN = {
    "Laptop": 0.18,
    "Smartphone": 0.22,
    "Tablet": 0.20,
    "Headphones": 0.35,
    "Monitor": 0.15,
    "Keyboard": 0.40,
    "Mouse": 0.45,
    "Webcam": 0.30,
}


def generate_rows(n: int = 250):
    start = datetime(2024, 1, 1)
    rows = []
    for _ in range(n):
        date = start + timedelta(days=random.randint(0, 364))
        product = random.choice(PRODUCTS)
        region = random.choice(REGIONS)
        lo, hi = PRODUCT_PRICE[product]
        quantity = random.randint(1, 20)
        unit_price = round(random.uniform(lo, hi), 2)
        sales = round(unit_price * quantity, 2)
        # March intentional dip
        if date.month == 3:
            sales = round(sales * random.uniform(0.4, 0.7), 2)
        profit = round(sales * MARGIN[product] * random.uniform(0.7, 1.1), 2)
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "product": product,
            "region": region,
            "quantity": quantity,
            "unit_price": unit_price,
            "sales": sales,
            "profit": profit,
        })
    rows.sort(key=lambda r: r["date"])
    return rows


def write_csv(rows):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "product", "region", "quantity", "unit_price", "sales", "profit"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV written: {CSV_PATH} ({len(rows)} rows)")


def load_sqlite(rows):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sales")
    cur.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product TEXT NOT NULL,
            region TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            sales REAL NOT NULL,
            profit REAL NOT NULL
        )
    """)
    for r in rows:
        cur.execute(
            "INSERT INTO sales (date, product, region, quantity, unit_price, sales, profit) VALUES (?,?,?,?,?,?,?)",
            (r["date"], r["product"], r["region"], r["quantity"], r["unit_price"], r["sales"], r["profit"]),
        )
    conn.commit()
    conn.close()
    print(f"SQLite DB written: {DB_PATH}")


if __name__ == "__main__":
    rows = generate_rows()
    write_csv(rows)
    load_sqlite(rows)
