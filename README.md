# ⚡ Global Patent Intelligence Data Pipeline
### Electronics & Semiconductors · USPTO PatentsView · Python · SQL · Streamlit

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=flat-square&logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Cleaning-green?style=flat-square&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Visualizations-purple?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📌 What This Project Does

This project builds a full **end-to-end data pipeline** that:

- **Downloads** real patent data from the USPTO PatentsView database
- **Cleans** the raw data using pandas
- **Stores** it in a structured SQLite database
- **Analyzes** it using 7 advanced SQL queries
- **Reports** findings via console output, CSV exports, and a JSON file
- **Visualizes** insights through an interactive Streamlit dashboard with 10 chart types including a rotating 3D globe

> Built to simulate how a real data engineer handles large-scale government data.

---

## 🗂 Project Structure

```
patent-pipeline/
│
├── data/
│   ├── raw/                  ← Downloaded USPTO files (not pushed to GitHub)
│   └── clean/                ← Cleaned CSV files (not pushed to GitHub)
│
├── reports/                  ← Generated outputs
│   ├── top_inventors.csv
│   ├── top_companies.csv
│   ├── country_trends.csv
│   ├── yearly_trends.csv
│   ├── patent_report.json
│   ├── chart_inventors.png
│   ├── chart_companies.png
│   ├── chart_countries.png
│   └── chart_yearly.png
│
├── scripts/
│   ├── download.py           ← Step 1: Download USPTO data files
│   ├── clean.py              ← Step 2: Clean data with pandas
│   ├── load_db.py            ← Step 3: Load into SQLite database
│   ├── queries.sql           ← Step 4: All 7 SQL analytical queries
│   └── report.py             ← Step 5: Generate all reports and charts
│
├── schema.sql                ← Database table definitions
├── dashboard.py              ← Interactive Streamlit dashboard
├── requirements.txt          ← Python dependencies
├── .gitignore                ← Files excluded from GitHub
└── README.md                 ← This file
```

---

## 🚀 How to Run This Project

### 1. Clone the repository
```bash
git clone https://github.com/AlexMutesasira/patent-pipeline.git
cd patent-pipeline
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the pipeline step by step
```bash
# Step 1 — Download raw data from USPTO
python scripts/download.py

# Step 2 — Clean and filter data
python scripts/clean.py

# Step 3 — Load into SQLite database
python scripts/load_db.py

# Step 4 — Generate all reports and charts
python scripts/report.py

# Step 5 — Launch the interactive dashboard (bonus)
streamlit run dashboard.py
```

---

## 🗄 Database Schema

The database contains **4 tables** connected through a relationships table:

```
patents          inventors         companies
──────────       ──────────        ──────────
patent_id   ←── patent_id    ──→  company_id
title            inventor_id       name
abstract         name
filing_date      country
year
        ↑              ↑                ↑
        └──────── relationships ────────┘
                  patent_id
                  inventor_id
                  company_id
```

---

## 📊 SQL Queries

| Query | Question | SQL Feature |
|-------|----------|-------------|
| Q1 | Who are the top inventors? | `GROUP BY`, `COUNT`, `ORDER BY` |
| Q2 | Which companies own the most patents? | `JOIN`, `COUNT DISTINCT` |
| Q3 | Which countries produce the most? | Subquery for percentage |
| Q4 | How many patents per year? | `GROUP BY year` |
| Q5 | Combined patent + inventor + company view | 3-table `JOIN` |
| Q6 | Companies with inventors from 3+ countries | `CTE` with `WITH` statement |
| Q7 | Rank inventors globally and by country | `RANK()` window function |

---

## 📈 Dashboard Features

Launch with `streamlit run dashboard.py`

| Tab | Visualization |
|-----|---------------|
| 🌍 World Map | Rotating 3D globe · Flat choropleth · Bubble map |
| 📈 Trend | Line chart with regression line and R² score |
| 🥧 Pie Charts | Donut · Sunburst · Animated by year · Funnel |
| 🫧 Bubble | Companies sized by patent count |
| 🌡 Heatmap | Decade × year intensity grid |
| 📦 Box Plot | Patent distribution spread per decade |
| 💧 Waterfall | Decade-over-decade change |
| 🌳 Tree Map | Clickable company patent share blocks |
| 🕸 Network | Inventor–company connection graph |
| 🔍 Search | Real-time keyword search across all titles |

---

## 🔑 Key Results (Sample — 100,000 patents)

### Top Inventors
| Rank | Inventor | Patents |
|------|----------|---------|
| 1 | Shunpei Yamazaki | 36 |
| 2 | Kia Silverbrook | 23 |
| 3 | Tao Luo | 17 |

### Top Companies
| Rank | Company | Patents |
|------|---------|---------|
| 1 | Samsung Electronics Co., Ltd. | 2,067 |
| 2 | IBM Corporation | 1,803 |
| 3 | Canon Kabushiki Kaisha | 1,042 |

---

## 📦 Reports Generated

| File | Type | Contents |
|------|------|----------|
| `top_inventors.csv` | CSV | Ranked inventor list |
| `top_companies.csv` | CSV | Ranked company list |
| `country_trends.csv` | CSV | Patents by country |
| `yearly_trends.csv` | CSV | Patents per year |
| `patent_report.json` | JSON | Full summary report |
| `chart_inventors.png` | Chart | Top 10 inventors bar chart |
| `chart_companies.png` | Chart | Top 10 companies bar chart |
| `chart_countries.png` | Chart | Country share pie chart |
| `chart_yearly.png` | Chart | Yearly trend line chart |

---

## 🛠 Tools and Libraries

| Tool | Purpose |
|------|---------|
| Python 3.12 | Core scripting language |
| pandas | Data cleaning and transformation |
| SQLite | Lightweight relational database |
| SQL | Analytical queries |
| matplotlib | Static chart generation |
| Plotly | Interactive dashboard charts |
| Streamlit | Web dashboard framework |
| networkx | Network graph visualization |
| squarify | Tree map chart |
| scipy | Regression analysis |
| pycountry | Country code lookup for globe |
| requests + tqdm | File download with progress bar |

---

## 📁 Data Source

**PatentsView — USPTO Granted Patent Disambiguated Data**
- URL: https://data.uspto.gov/bulkdata/datasets/pvgpatdis
- Coverage: 1976 – 2025
- Field: Electronics and Semiconductors (keyword filtered)
- Files used:
  - `g_patent.tsv` — patent titles and dates
  - `g_inventor_disambiguated.tsv` — inventor names
  - `g_assignee_disambiguated.tsv` — company names

> Large data files are not included in this repository.
> Run `python scripts/download.py` to fetch them automatically.

---

## ⚙️ Requirements

```
pandas
requests
tqdm
matplotlib
seaborn
streamlit
plotly
networkx
squarify
scipy
pycountry
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 👤 Author

**Alex Mutesasira Ssemujju**
- Project: Global Patent Intelligence Data Pipeline
- Data Source: USPTO PatentsView
- Year: 2026

---

