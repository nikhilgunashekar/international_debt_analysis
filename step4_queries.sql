-- ── Query 1: All distinct country names ─────────────────────
-- DISTINCT = removes duplicates, gives unique values only
SELECT DISTINCT country_name
FROM countries
ORDER BY country_name;


-- ── Query 2: Total number of countries ──────────────────────
-- COUNT(*) = counts rows
SELECT COUNT(*) AS total_countries
FROM countries;


-- ── Query 3: Total number of indicators ─────────────────────
SELECT COUNT(*) AS total_indicators
FROM indicators;


-- ── Query 4: First 10 records of debt_data ──────────────────
-- JOIN links debt_data with countries and indicators tables
-- This avoids showing just IDs — we get actual names instead
SELECT
    c.country_name,
    c.country_code,
    i.indicator_name,
    i.indicator_code,
    d.debt
FROM debt_data d
JOIN countries  c ON d.country_id   = c.country_id
JOIN indicators i ON d.indicator_id = i.indicator_id
LIMIT 10;


-- ── Query 5: Total global debt ──────────────────────────────
-- SUM = adds up all values in a column
SELECT
    ROUND(SUM(debt), 2)        AS total_debt_usd,
    ROUND(SUM(debt) / 1e9, 4)  AS total_debt_billions
FROM debt_data;


-- ── Query 6: All unique indicator names ─────────────────────
SELECT DISTINCT indicator_name
FROM indicators
ORDER BY indicator_name;


-- ── Query 7: Number of records for each country ─────────────
-- GROUP BY groups rows with same country together
-- COUNT(*) counts how many records per group
SELECT
    c.country_name,
    COUNT(*) AS record_count
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY record_count DESC;


-- ── Query 8: Records where debt > 1 billion USD ─────────────
-- 1 billion = 1,000,000,000 (9 zeros)
SELECT
    c.country_name,
    i.indicator_name,
    ROUND(d.debt, 2) AS debt_usd
FROM debt_data d
JOIN countries  c ON d.country_id   = c.country_id
JOIN indicators i ON d.indicator_id = i.indicator_id
WHERE d.debt > 1000000000
ORDER BY d.debt DESC;


-- ── Query 9: Min, Max, Average debt values ──────────────────
SELECT
    ROUND(MIN(debt), 2)  AS minimum_debt,
    ROUND(MAX(debt), 2)  AS maximum_debt,
    ROUND(AVG(debt), 2)  AS average_debt,
    ROUND(SUM(debt), 2)  AS total_debt
FROM debt_data;


-- ── Query 10: Total number of records in dataset ────────────
SELECT COUNT(*) AS total_records FROM debt_data;


-- ============================================================
--  SECTION B: INTERMEDIATE QUERIES (11–20)
-- ============================================================

-- ── Query 11: Total debt for each country ───────────────────
SELECT
    c.country_name,
    ROUND(SUM(d.debt), 2)       AS total_debt,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY total_debt DESC;


-- ── Query 12: Top 10 countries — highest total debt ─────────
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY total_debt_billions DESC
LIMIT 10;


-- ── Query 13: Average debt per country ──────────────────────
SELECT
    c.country_name,
    ROUND(AVG(d.debt), 2) AS avg_debt_per_indicator
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY avg_debt_per_indicator DESC;


-- ── Query 14: Total debt for each indicator ─────────────────
SELECT
    i.indicator_name,
    ROUND(SUM(d.debt), 2)       AS total_debt,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN indicators i ON d.indicator_id = i.indicator_id
GROUP BY i.indicator_name
ORDER BY total_debt DESC;


-- ── Query 15: Indicator contributing the highest total debt ─
-- We add LIMIT 1 to get just the top one
SELECT
    i.indicator_name,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN indicators i ON d.indicator_id = i.indicator_id
GROUP BY i.indicator_name
ORDER BY total_debt_billions DESC
LIMIT 1;


-- ── Query 16: Country with the lowest total debt ─────────────
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY total_debt_billions ASC
LIMIT 1;


-- ── Query 17: Total debt — each country + indicator combo ────
SELECT
    c.country_name,
    i.indicator_name,
    ROUND(SUM(d.debt), 2) AS total_debt
FROM debt_data d
JOIN countries  c ON d.country_id   = c.country_id
JOIN indicators i ON d.indicator_id = i.indicator_id
GROUP BY c.country_name, i.indicator_name
ORDER BY c.country_name, total_debt DESC;


-- ── Query 18: How many indicators each country has ───────────
SELECT
    c.country_name,
    COUNT(DISTINCT d.indicator_id) AS num_indicators
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY num_indicators DESC;


-- ── Query 19: Countries whose total debt > global average ────
-- Subquery: calculates the global average first, then filters
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
HAVING SUM(d.debt) > (
    SELECT AVG(country_total)
    FROM (
        SELECT SUM(debt) AS country_total
        FROM debt_data
        GROUP BY country_id
    ) AS sub
)
ORDER BY total_debt_billions DESC;


-- ── Query 20: Rank countries by total debt ───────────────────
-- RANK() is a window function — gives rank number to each row
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4)                       AS total_debt_billions,
    RANK() OVER (ORDER BY SUM(d.debt) DESC)            AS debt_rank
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY debt_rank;


-- ============================================================
--  SECTION C: ADVANCED QUERIES (21–30)
-- ============================================================

-- ── Query 21: Top 5 indicators contributing to global debt ───
SELECT
    i.indicator_name,
    ROUND(SUM(d.debt) / 1e9, 4)                       AS total_debt_billions,
    RANK() OVER (ORDER BY SUM(d.debt) DESC)            AS contribution_rank
FROM debt_data d
JOIN indicators i ON d.indicator_id = i.indicator_id
GROUP BY i.indicator_name
ORDER BY contribution_rank
LIMIT 5;


-- ── Query 22: % contribution of each country ─────────────────
-- We divide each country's debt by the global total × 100
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4)                                    AS total_debt_billions,
    ROUND(SUM(d.debt) / (SELECT SUM(debt) FROM debt_data) * 100, 2) AS pct_of_global
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY pct_of_global DESC;


-- ── Query 23: Top 3 countries per indicator ───────────────────
-- ROW_NUMBER() assigns 1,2,3 within each indicator group
WITH ranked AS (
    SELECT
        i.indicator_name,
        c.country_name,
        ROUND(SUM(d.debt) / 1e9, 4)                              AS total_debt_billions,
        ROW_NUMBER() OVER (
            PARTITION BY i.indicator_id
            ORDER BY SUM(d.debt) DESC
        )                                                          AS row_num
    FROM debt_data d
    JOIN countries  c ON d.country_id   = c.country_id
    JOIN indicators i ON d.indicator_id = i.indicator_id
    GROUP BY i.indicator_id, i.indicator_name, c.country_id, c.country_name
)
SELECT indicator_name, country_name, total_debt_billions, row_num AS rank_within_indicator
FROM ranked
WHERE row_num <= 3
ORDER BY indicator_name, row_num;


-- ── Query 24: Difference between max and min debt per country ─
SELECT
    c.country_name,
    ROUND(MAX(d.debt), 2)              AS max_debt,
    ROUND(MIN(d.debt), 2)              AS min_debt,
    ROUND(MAX(d.debt) - MIN(d.debt), 2) AS debt_range
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_name
ORDER BY debt_range DESC;


-- ── Query 25: VIEW — Top 10 countries by highest debt ─────────
-- A VIEW is like a saved query — you can SELECT from it later
-- DROP first so we can re-create it cleanly if script is re-run
DROP VIEW IF EXISTS vw_top10_countries;

CREATE VIEW vw_top10_countries AS
SELECT
    c.country_name,
    c.country_code,
    ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_id, c.country_name, c.country_code
ORDER BY total_debt_billions DESC
LIMIT 10;

-- Use the view like a table:
SELECT * FROM vw_top10_countries;


-- ── Query 26: Categorize countries — High / Medium / Low Debt ─
-- CASE WHEN = if-else logic inside SQL
WITH country_totals AS (
    SELECT
        c.country_name,
        ROUND(SUM(d.debt) / 1e9, 4) AS total_debt_billions
    FROM debt_data d
    JOIN countries c ON d.country_id = c.country_id
    GROUP BY c.country_name
),
percentiles AS (
    SELECT
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_debt_billions) AS p75,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_debt_billions) AS p25
    FROM country_totals
)
SELECT
    ct.country_name,
    ct.total_debt_billions,
    CASE
        WHEN ct.total_debt_billions >= p.p75 THEN 'High Debt'
        WHEN ct.total_debt_billions >= p.p25 THEN 'Medium Debt'
        ELSE 'Low Debt'
    END AS debt_category
FROM country_totals ct, percentiles p
ORDER BY ct.total_debt_billions DESC;


-- ── Query 27: Cumulative debt per country (window function) ───
-- SUM() OVER (ORDER BY...) = running total
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4)                          AS country_total_billions,
    ROUND(
        SUM(SUM(d.debt)) OVER (ORDER BY SUM(d.debt) DESC) / 1e9, 4
    )                                                      AS cumulative_total_billions
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_id, c.country_name
ORDER BY country_total_billions DESC;


-- ── Query 28: Indicators where avg debt > overall avg ─────────
SELECT
    i.indicator_name,
    ROUND(AVG(d.debt), 2)              AS avg_debt,
    ROUND(
        (SELECT AVG(debt) FROM debt_data), 2
    )                                  AS overall_avg,
    ROUND(AVG(d.debt) - (SELECT AVG(debt) FROM debt_data), 2) AS difference
FROM debt_data d
JOIN indicators i ON d.indicator_id = i.indicator_id
GROUP BY i.indicator_id, i.indicator_name
HAVING AVG(d.debt) > (SELECT AVG(debt) FROM debt_data)
ORDER BY avg_debt DESC;


-- ── Query 29: Countries contributing more than 5% of global ───
SELECT
    c.country_name,
    ROUND(SUM(d.debt) / 1e9, 4)                                    AS total_debt_billions,
    ROUND(SUM(d.debt) / (SELECT SUM(debt) FROM debt_data) * 100, 2) AS pct_contribution
FROM debt_data d
JOIN countries c ON d.country_id = c.country_id
GROUP BY c.country_id, c.country_name
HAVING pct_contribution > 5
ORDER BY pct_contribution DESC;


-- ── Query 30: Most dominant indicator per country ──────────────
-- For each country, find which indicator has the highest debt
WITH indicator_ranks AS (
    SELECT
        c.country_name,
        i.indicator_name,
        ROUND(SUM(d.debt) / 1e9, 4)                                AS total_debt_billions,
        ROW_NUMBER() OVER (
            PARTITION BY c.country_id
            ORDER BY SUM(d.debt) DESC
        )                                                            AS rank_in_country
    FROM debt_data d
    JOIN countries  c ON d.country_id   = c.country_id
    JOIN indicators i ON d.indicator_id = i.indicator_id
    GROUP BY c.country_id, c.country_name, i.indicator_id, i.indicator_name
)
SELECT
    country_name,
    indicator_name AS dominant_indicator,
    total_debt_billions
FROM indicator_ranks
WHERE rank_in_country = 1
ORDER BY total_debt_billions DESC;
