-- scripts/queries.sql
-- All 7 required analytical queries for the patent database
-- These are called automatically by report.py
-- You can also run them manually in any SQLite viewer


-- ============================================================
-- Q1: TOP INVENTORS
-- Who has filed the most patents?
-- ============================================================
SELECT
    i.name                          AS inventor_name,
    i.country,
    COUNT(DISTINCT r.patent_id)     AS patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name, i.country
ORDER BY patent_count DESC
LIMIT 20;


-- ============================================================
-- Q2: TOP COMPANIES
-- Which companies own the most patents?
-- ============================================================
SELECT
    c.name                          AS company_name,
    COUNT(DISTINCT r.patent_id)     AS patent_count
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 20;


-- ============================================================
-- Q3: TOP COUNTRIES
-- Which countries produce the most patents?
-- ============================================================
SELECT
    i.country,
    COUNT(DISTINCT r.patent_id)     AS patent_count,
    ROUND(
        COUNT(DISTINCT r.patent_id) * 100.0
        / (SELECT COUNT(*) FROM patents), 2
    )                               AS share_pct
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country IS NOT NULL
  AND i.country != ''
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 20;


-- ============================================================
-- Q4: TRENDS OVER TIME
-- How many patents are granted each year?
-- ============================================================
SELECT
    year,
    COUNT(*)                        AS total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year ASC;


-- ============================================================
-- Q5: JOIN QUERY
-- Combine patents with their inventors and companies
-- in one single result
-- ============================================================
SELECT
    p.patent_id,
    p.title,
    p.year,
    i.name                          AS inventor_name,
    i.country                       AS inventor_country,
    c.name                          AS company_name
FROM patents p
JOIN relationships r   ON p.patent_id   = r.patent_id
JOIN inventors i       ON r.inventor_id = i.inventor_id
LEFT JOIN companies c  ON r.company_id  = c.company_id
ORDER BY p.year DESC
LIMIT 100;


-- ============================================================
-- Q6: CTE QUERY (WITH statement)
-- Break a complex question into readable steps
-- Find companies whose inventors span 3 or more countries
-- ============================================================
WITH company_countries AS (
    -- Step 1: pair each company with every country
    --         its inventors come from
    SELECT DISTINCT
        c.company_id,
        c.name      AS company_name,
        i.country
    FROM companies c
    JOIN relationships r ON c.company_id  = r.company_id
    JOIN inventors i     ON r.inventor_id = i.inventor_id
    WHERE i.country IS NOT NULL
      AND i.country != ''
),
country_counts AS (
    -- Step 2: count distinct countries per company
    SELECT
        company_name,
        COUNT(DISTINCT country)     AS country_count
    FROM company_countries
    GROUP BY company_id, company_name
)
-- Step 3: only show companies that are truly international
SELECT
    company_name,
    country_count
FROM country_counts
WHERE country_count >= 3
ORDER BY country_count DESC
LIMIT 20;


-- ============================================================
-- Q7: RANKING QUERY (Window Function)
-- Rank inventors by patent count
-- both globally and within their own country
-- ============================================================
WITH inventor_counts AS (
    SELECT
        i.inventor_id,
        i.name                          AS inventor_name,
        i.country,
        COUNT(DISTINCT r.patent_id)     AS patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name, i.country
)
SELECT
    inventor_name,
    country,
    patent_count,
    RANK() OVER (
        ORDER BY patent_count DESC
    )                                   AS global_rank,
    RANK() OVER (
        PARTITION BY country
        ORDER BY patent_count DESC
    )                                   AS rank_in_country
FROM inventor_counts
WHERE country IS NOT NULL
  AND country != ''
ORDER BY global_rank
LIMIT 50;