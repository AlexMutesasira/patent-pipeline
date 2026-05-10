# scripts/load_db.py
# Loads the 4 clean CSV files into a SQLite database
# Creates patents.db in the root USPTO folder
# Run with: python scripts/load_db.py

import os
import sqlite3
import pandas as pd

BASE_DIR  = os.path.join(os.path.dirname(__file__), "..")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
SCHEMA    = os.path.join(BASE_DIR, "schema.sql")
DB_PATH   = os.path.join(BASE_DIR, "patents.db")

# Each CSV file maps to one table in the database
# Order matters — patents, inventors, companies must be
# loaded before relationships because relationships
# references all three via foreign keys
TABLES = [
    ("clean_patents.csv",       "patents"),
    ("clean_inventors.csv",     "inventors"),
    ("clean_companies.csv",     "companies"),
    ("clean_relationships.csv", "relationships"),
]

# Insert rows in chunks to avoid running out of memory
# 50,000 rows at a time is safe for most computers
CHUNK_SIZE = 50_000


# ── Step 1: create all 4 tables from schema.sql ──────────────
def create_tables(conn):
    print("  Creating tables from schema.sql ...")
    with open(SCHEMA, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    print("  Tables created.\n")


# ── Step 2: load one CSV into one table ──────────────────────
def load_csv(conn, csv_file, table):
    path = os.path.join(CLEAN_DIR, csv_file)

    # Warn and skip if the file does not exist
    if not os.path.exists(path):
        print(f"  [SKIP] {csv_file} not found — run clean.py first")
        return

    print(f"  Loading {csv_file} → table '{table}'")
    total = 0

    # Read the CSV in chunks and insert each chunk
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, dtype=str):
        chunk.to_sql(
            table,
            conn,
            if_exists="append",  # add rows to existing table
            index=False,
        )
        total += len(chunk)
        print(f"    {total:,} rows inserted ...", end="\r")

    print(f"  Done — {total:,} rows loaded into '{table}'        ")


# ── Step 3: print row counts to verify everything loaded ─────
def verify(conn):
    print("\n  ── Verifying row counts ─────────────────────")
    for table in ["patents", "inventors", "companies", "relationships"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<20} {n:>12,} rows")
    print("  ─────────────────────────────────────────────")


# ── main ─────────────────────────────────────────────────────
def main():
    print("\n========================================")
    print("  Loading Data into SQLite Database")
    print("========================================\n")

    # Delete old database if it exists so we start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("  Removed old patents.db — starting fresh\n")

    # Open a connection — this creates patents.db
    conn = sqlite3.connect(DB_PATH)

    try:
        create_tables(conn)

        for csv_file, table in TABLES:
            load_csv(conn, csv_file, table)
            print()

        verify(conn)

    finally:
        conn.close()

    print(f"\n  Database saved: patents.db")
    print("  Next step: python scripts/report.py\n")


if __name__ == "__main__":
    main()