# scripts/clean.py
# Reads the 3 raw TSV files from data/raw/
# Filters patents to Electronics and Semiconductors field only
# Collects up to 2,000,000 matching patents
# Saves 4 clean CSV files to data/clean/
# Run with: python scripts/clean.py

import os
import pandas as pd

RAW_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

# Maximum matching patents to collect
ROW_LIMIT = 2_000_000

# Keywords that identify Electronics and Semiconductor patents
# A patent matches if its title contains ANY of these words
KEYWORDS = [
    "semiconductor", "transistor", "circuit", "integrated circuit",
    "microchip", "chip", "diode", "capacitor", "resistor",
    "electronic", "electronics", "display", "LED", "OLED",
    "processor", "microprocessor", "memory", "DRAM", "NAND",
    "flash memory", "solar cell", "photovoltaic", "antenna",
    "amplifier", "oscillator", "sensor", "CMOS", "MOSFET",
    "lithography", "wafer", "substrate", "electrode", "battery",
    "printed circuit", "PCB", "signal processing", "rectifier",
    "inverter", "power supply", "voltage", "current regulator",
]

# Build one combined pattern from all keywords
# re.IGNORECASE makes it case-insensitive so LED matches led, Led etc.
PATTERN = "|".join(KEYWORDS)


# ── helper: read a TSV file from data/raw/ ───────────────────
def read_tsv(filename, columns, nrows=None):
    path = os.path.join(RAW_DIR, filename)
    print(f"    Reading {filename} ...")
    df = pd.read_csv(
        path,
        sep="\t",
        usecols=columns,
        dtype=str,
        low_memory=False,
        on_bad_lines="skip",
        nrows=nrows,
    )
    print(f"    {len(df):,} rows loaded")
    return df


# ── helper: save a clean DataFrame to data/clean/ ────────────
def save(df, filename):
    path = os.path.join(CLEAN_DIR, filename)
    df.to_csv(path, index=False)
    print(f"    Saved {filename} — {len(df):,} rows\n")


# ── CLEAN 1: patents ──────────────────────────────────────────
def clean_patents():
    print("[1/4] Cleaning patents (Electronics & Semiconductors filter) ...")

    # Read all patents — we need to filter before limiting
    df = read_tsv(
        "g_patent.tsv",
        columns=["patent_id", "patent_title", "patent_date"],
    )

    # Rename columns to match schema
    df.rename(columns={
        "patent_title": "title",
        "patent_date":  "filing_date",
    }, inplace=True)

    # Drop rows with no patent_id
    df.dropna(subset=["patent_id"], inplace=True)
    df.drop_duplicates(subset=["patent_id"], inplace=True)

    # Clean whitespace
    df["title"] = df["title"].str.strip()

    # ── FILTER: keep only electronics/semiconductor patents ───
    print(f"    Filtering titles by {len(KEYWORDS)} keywords ...")
    mask = df["title"].str.contains(PATTERN, case=False, na=False)
    df = df[mask]
    print(f"    {len(df):,} patents matched the filter")

    # Apply row limit after filtering
    df = df.head(ROW_LIMIT)
    print(f"    Keeping {len(df):,} patents (limit: {ROW_LIMIT:,})")

    # Extract year from date
    df["year"] = pd.to_datetime(df["filing_date"], errors="coerce").dt.year
    df = df[df["year"].between(1976, 2025)]

    # Add empty abstract column to match schema
    df["abstract"] = ""

    save(df[["patent_id", "title", "abstract", "filing_date", "year"]], "clean_patents.csv")

    # Return the filtered patent IDs so other functions can use them
    return set(df["patent_id"].tolist())


# ── CLEAN 2: inventors ────────────────────────────────────────
def clean_inventors(valid_patent_ids):
    print("[2/4] Cleaning inventors ...")

    df = read_tsv(
        "g_inventor_disambiguated.tsv",
        columns=[
            "inventor_id",
            "patent_id",
            "disambig_inventor_name_first",
            "disambig_inventor_name_last",
        ],
    )

    # Keep only inventors linked to our filtered patents
    print(f"    Filtering inventors to matched patents ...")
    df = df[df["patent_id"].isin(valid_patent_ids)]
    print(f"    {len(df):,} inventor rows after filter")

    df.dropna(subset=["inventor_id"], inplace=True)
    df.drop_duplicates(subset=["inventor_id"], inplace=True)

    # Combine first and last name
    df["name"] = (
        df["disambig_inventor_name_first"].fillna("").str.strip()
        + " "
        + df["disambig_inventor_name_last"].fillna("").str.strip()
    ).str.strip()

    df["country"] = "Unknown"

    df = df[df["name"].str.len() > 1]

    save(df[["inventor_id", "name", "country"]], "clean_inventors.csv")


# ── CLEAN 3: companies ────────────────────────────────────────
def clean_companies(valid_patent_ids):
    print("[3/4] Cleaning companies ...")

    df = read_tsv(
        "g_assignee_disambiguated.tsv",
        columns=["assignee_id", "patent_id", "disambig_assignee_organization"],
    )

    # Keep only companies linked to our filtered patents
    print(f"    Filtering companies to matched patents ...")
    df = df[df["patent_id"].isin(valid_patent_ids)]
    print(f"    {len(df):,} company rows after filter")

    df.dropna(subset=["assignee_id"], inplace=True)
    df.drop_duplicates(subset=["assignee_id"], inplace=True)

    df.rename(columns={
        "assignee_id":                    "company_id",
        "disambig_assignee_organization": "name",
    }, inplace=True)

    df.dropna(subset=["name"], inplace=True)
    df["name"] = df["name"].str.strip()
    df = df[df["name"].str.len() > 0]

    save(df[["company_id", "name"]], "clean_companies.csv")


# ── CLEAN 4: relationships ────────────────────────────────────
def clean_relationships(valid_patent_ids):
    print("[4/4] Building relationships ...")

    # Patent → inventor links
    inv = read_tsv(
        "g_inventor_disambiguated.tsv",
        columns=["patent_id", "inventor_id"],
    )
    inv = inv[inv["patent_id"].isin(valid_patent_ids)]
    inv.dropna(subset=["patent_id", "inventor_id"], inplace=True)

    # Patent → company links
    asg = read_tsv(
        "g_assignee_disambiguated.tsv",
        columns=["patent_id", "assignee_id"],
    )
    asg = asg[asg["patent_id"].isin(valid_patent_ids)]
    asg.rename(columns={"assignee_id": "company_id"}, inplace=True)
    asg.dropna(subset=["patent_id"], inplace=True)

    # Merge on patent_id
    df = pd.merge(inv, asg, on="patent_id", how="outer")
    df = df[df["patent_id"].isin(valid_patent_ids)]

    df.dropna(subset=["patent_id"], inplace=True)
    df.drop_duplicates(inplace=True)

    save(df[["patent_id", "inventor_id", "company_id"]], "clean_relationships.csv")


# ── main ──────────────────────────────────────────────────────
def main():
    print("\n========================================")
    print("  Cleaning Patent Data — Electronics")
    print("  & Semiconductors Field Only")
    print(f"  Target: {ROW_LIMIT:,} patents")
    print("========================================\n")

    # Step 1: clean patents and get the matching IDs
    valid_ids = clean_patents()

    print(f"  Total matched patents: {len(valid_ids):,}")
    print(f"  Passing IDs to other tables ...\n")

    # Steps 2-4: use those IDs to filter inventors, companies, relationships
    clean_inventors(valid_ids)
    clean_companies(valid_ids)
    clean_relationships(valid_ids)

    print("All 4 clean files saved to data/clean/")
    print("Next step: python scripts/load_db.py\n")


if __name__ == "__main__":
    main()