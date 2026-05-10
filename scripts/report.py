# scripts/report.py
# Generates all 3 required report types:
#   A. Console report printed to terminal
#   B. CSV exports saved to reports/
#   C. JSON report saved to reports/
# Plus bonus matplotlib charts
# Run with: python scripts/report.py

import os
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR    = os.path.join(os.path.dirname(__file__), "..")
DB_PATH     = os.path.join(BASE_DIR, "patents.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# ── run any SQL query and return a DataFrame ─────────────────
def run(sql):
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql_query(sql, conn)
    conn.close()
    return df


# ── SQL queries for each section ─────────────────────────────

SQL_TOTAL = "SELECT COUNT(*) AS total FROM patents"

SQL_INVENTORS = """
    SELECT
        i.name                      AS inventor_name,
        i.country,
        COUNT(DISTINCT r.patent_id) AS patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name, i.country
    ORDER BY patent_count DESC
    LIMIT 20
"""

SQL_COMPANIES = """
    SELECT
        c.name                      AS company_name,
        COUNT(DISTINCT r.patent_id) AS patent_count
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC
    LIMIT 20
"""

SQL_COUNTRIES = """
    SELECT
        i.country,
        COUNT(DISTINCT r.patent_id) AS patent_count,
        ROUND(COUNT(DISTINCT r.patent_id) * 100.0
              / (SELECT COUNT(*) FROM patents), 2) AS share_pct
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL AND i.country != ''
    GROUP BY i.country
    ORDER BY patent_count DESC
    LIMIT 20
"""

SQL_YEARLY = """
    SELECT year, COUNT(*) AS total_patents
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year ASC
"""


# ── A. CONSOLE REPORT ─────────────────────────────────────────
def console_report(total, inventors, companies, countries):
    W = 56
    print("\n" + "=" * W)
    print("  PATENT INTELLIGENCE REPORT".center(W))
    print("=" * W)
    print(f"\n  Total Patents in Database : {total:,}\n")

    print("  TOP 10 INVENTORS")
    print("  " + "─" * 52)
    for rank, row in inventors.head(10).iterrows():
        print(
            f"  {rank+1:>2}. "
            f"{row['inventor_name']:<28} "
            f"{row['patent_count']:>5,} patents  "
            f"[{row['country']}]"
        )

    print(f"\n  TOP 10 COMPANIES")
    print("  " + "─" * 52)
    for rank, row in companies.head(10).iterrows():
        print(
            f"  {rank+1:>2}. "
            f"{row['company_name']:<34} "
            f"{row['patent_count']:>5,} patents"
        )

    print(f"\n  TOP 10 COUNTRIES")
    print("  " + "─" * 52)
    for rank, row in countries.head(10).iterrows():
        print(
            f"  {rank+1:>2}. "
            f"{row['country']:<12} "
            f"{row['patent_count']:>8,} patents  "
            f"({row['share_pct']}%)"
        )

    print("\n" + "=" * W + "\n")


# ── B. CSV EXPORTS ────────────────────────────────────────────
def export_csvs(inventors, companies, countries, yearly):
    print("  Saving CSV files ...")

    inventors.to_csv(os.path.join(REPORTS_DIR, "top_inventors.csv"),  index=False)
    companies.to_csv(os.path.join(REPORTS_DIR, "top_companies.csv"),  index=False)
    countries.to_csv(os.path.join(REPORTS_DIR, "country_trends.csv"), index=False)
    yearly.to_csv(os.path.join(REPORTS_DIR,    "yearly_trends.csv"),  index=False)

    print("  Saved:")
    print("    reports/top_inventors.csv")
    print("    reports/top_companies.csv")
    print("    reports/country_trends.csv")
    print("    reports/yearly_trends.csv")


# ── C. JSON REPORT ────────────────────────────────────────────
def export_json(total, inventors, companies, countries):
    print("\n  Saving JSON report ...")

    report = {
        "total_patents": int(total),
        "top_inventors": [
            {
                "rank":    rank + 1,
                "name":    row["inventor_name"],
                "country": row["country"],
                "patents": int(row["patent_count"]),
            }
            for rank, row in inventors.head(10).iterrows()
        ],
        "top_companies": [
            {
                "rank":    rank + 1,
                "name":    row["company_name"],
                "patents": int(row["patent_count"]),
            }
            for rank, row in companies.head(10).iterrows()
        ],
        "top_countries": [
            {
                "rank":      rank + 1,
                "country":   row["country"],
                "patents":   int(row["patent_count"]),
                "share_pct": float(row["share_pct"]),
            }
            for rank, row in countries.head(10).iterrows()
        ],
    }

    path = os.path.join(REPORTS_DIR, "patent_report.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    print("  Saved: reports/patent_report.json")


# ── BONUS: Charts ─────────────────────────────────────────────
def make_charts(inventors, companies, countries, yearly):
    print("\n  Generating charts ...")

    # Chart 1: Top 10 inventors — horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    data = inventors.head(10).iloc[::-1]
    ax.barh(data["inventor_name"], data["patent_count"], color="steelblue")
    ax.set_xlabel("Number of Patents")
    ax.set_title("Top 10 Inventors by Patent Count")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "chart_inventors.png"), dpi=150)
    plt.close()

    # Chart 2: Top 10 companies — horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    data = companies.head(10).iloc[::-1]
    ax.barh(data["company_name"], data["patent_count"], color="darkorange")
    ax.set_xlabel("Number of Patents")
    ax.set_title("Top 10 Companies by Patent Count")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "chart_companies.png"), dpi=150)
    plt.close()

    # Chart 3: Country share — pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    top5   = countries.head(5)
    others = countries["patent_count"].sum() - top5["patent_count"].sum()
    labels = list(top5["country"]) + ["Other"]
    sizes  = list(top5["patent_count"]) + [int(others)]
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.set_title("Patent Share by Country")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "chart_countries.png"), dpi=150)
    plt.close()

    # Chart 4: Patents per year — line chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        yearly["year"].astype(int),
        yearly["total_patents"],
        color="green",
        linewidth=2,
        marker="o",
        markersize=3,
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Patents Granted")
    ax.set_title("Patent Grants Per Year")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "chart_yearly.png"), dpi=150)
    plt.close()

    print("  Saved:")
    print("    reports/chart_inventors.png")
    print("    reports/chart_companies.png")
    print("    reports/chart_countries.png")
    print("    reports/chart_yearly.png")


# ── main ──────────────────────────────────────────────────────
def main():
    print("\n========================================")
    print("  Generating Patent Reports")
    print("========================================")

    # Run all queries
    total     = run(SQL_TOTAL)["total"][0]
    inventors = run(SQL_INVENTORS)
    companies = run(SQL_COMPANIES)
    countries = run(SQL_COUNTRIES)
    yearly    = run(SQL_YEARLY)

    # A — console
    console_report(total, inventors, companies, countries)

    # B — CSVs
    export_csvs(inventors, companies, countries, yearly)

    # C — JSON
    export_json(total, inventors, companies, countries)

    # Bonus — charts
    make_charts(inventors, companies, countries, yearly)

    print("\n  All reports complete.")
    print("  Check your reports/ folder.\n")


if __name__ == "__main__":
    main()