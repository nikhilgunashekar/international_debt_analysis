import pandas as pd
import mysql.connector
import os

# ── Database Config — CHANGE to match yours ─────────────────
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "root",
    "password": "your_password",   # ← CHANGE THIS
    "database": "debt_db"
}

OUTPUT_FILE = "outputs/query_results.txt"
os.makedirs("outputs", exist_ok=True)

# ==============================================================
#  CONNECT TO DATABASE
# ==============================================================
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("✅ Connected to debt_db\n")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

results_log = []

def run_query(query_num, title, sql):
    """Runs a query, prints + saves results."""
    print(f"{'='*60}")
    print(f"  Q{query_num:02d}: {title}")
    print(f"{'='*60}")

    try:
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"  ❌ Error: {e}")
        df = pd.DataFrame()

    print()
    log_entry = f"\n{'='*60}\nQ{query_num:02d}: {title}\n{'='*60}\n{df.to_string(index=False)}\n"
    results_log.append(log_entry)


# ==============================================================
#  RUN ALL 30 QUERIES
# ==============================================================

# ── BASIC (1–10) ─────────────────────────────────────────────

run_query(1, "All Distinct Country Names", """
    SELECT DISTINCT country_name FROM countries ORDER BY country_name
""")

run_query(2, "Total Number of Countries", """
    SELECT COUNT(*) AS total_countries FROM countries
""")

run_query(3, "Total Number of Indicators", """
    SELECT COUNT(*) AS total_indicators FROM indicators
""")

run_query(4, "First 10 Records", """
    SELECT c.country_name, i.indicator_name, d.debt
    FROM debt_data d
    JOIN countries c ON d.country_id = c.country_id
    JOIN indicators i ON d.indicator_id = i.indicator_id
    LIMIT 10
""")

run_query(5, "Total Global Debt", """
    SELECT ROUND(SUM(debt), 2) AS total_usd,
           ROUND(SUM(debt)/1e9, 4) AS total_billions
    FROM debt_data
""")

run_query(6, "All Unique Indicator Names", """
    SELECT DISTINCT indicator_name FROM indicators ORDER BY indicator_name
""")

run_query(7, "Number of Records per Country", """
    SELECT c.country_name, COUNT(*) AS record_count
    FROM debt_data d
    JOIN countries c ON d.country_id = c.country_id
    GROUP BY c.country_name ORDER BY record_count DESC
""")

run_query(8, "Records Where Debt > 1 Billion USD", """
    SELECT c.country_name, i.indicator_name, ROUND(d.debt, 2) AS debt
    FROM debt_data d
    JOIN countries c ON d.country_id = c.country_id
    JOIN indicators i ON d.indicator_id = i.indicator_id
    WHERE d.debt > 1000000000 ORDER BY d.debt DESC
""")

run_query(9, "Min / Max / Average Debt Values", """
    SELECT ROUND(MIN(debt),2) AS min_debt,
           ROUND(MAX(debt),2) AS max_debt,
           ROUND(AVG(debt),2) AS avg_debt
    FROM debt_data
""")

run_query(10, "Total Records in Dataset", """
    SELECT COUNT(*) AS total_records FROM debt_data
""")

# ── INTERMEDIATE (11–20) ──────────────────────────────────────

run_query(11, "Total Debt for Each Country", """
    SELECT c.country_name, ROUND(SUM(d.debt)/1e9,4) AS total_billions
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY total_billions DESC
""")

run_query(12, "Top 10 Countries — Highest Total Debt", """
    SELECT c.country_name, ROUND(SUM(d.debt)/1e9,4) AS total_billions
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY total_billions DESC LIMIT 10
""")

run_query(13, "Average Debt per Country", """
    SELECT c.country_name, ROUND(AVG(d.debt),2) AS avg_debt
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY avg_debt DESC
""")

run_query(14, "Total Debt for Each Indicator", """
    SELECT i.indicator_name, ROUND(SUM(d.debt)/1e9,4) AS total_billions
    FROM debt_data d JOIN indicators i ON d.indicator_id=i.indicator_id
    GROUP BY i.indicator_name ORDER BY total_billions DESC
""")

run_query(15, "Indicator with Highest Total Debt", """
    SELECT i.indicator_name, ROUND(SUM(d.debt)/1e9,4) AS total_billions
    FROM debt_data d JOIN indicators i ON d.indicator_id=i.indicator_id
    GROUP BY i.indicator_name ORDER BY total_billions DESC LIMIT 1
""")

run_query(16, "Country with Lowest Total Debt", """
    SELECT c.country_name, ROUND(SUM(d.debt)/1e9,4) AS total_billions
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY total_billions ASC LIMIT 1
""")

run_query(17, "Total Debt — Country + Indicator Combo", """
    SELECT c.country_name, i.indicator_name, ROUND(SUM(d.debt),2) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_id=c.country_id
    JOIN indicators i ON d.indicator_id=i.indicator_id
    GROUP BY c.country_name, i.indicator_name
    ORDER BY c.country_name, total_debt DESC LIMIT 30
""")

run_query(18, "Number of Indicators per Country", """
    SELECT c.country_name, COUNT(DISTINCT d.indicator_id) AS num_indicators
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY num_indicators DESC
""")

run_query(19, "Countries Above Global Average Debt", """
    SELECT c.country_name, ROUND(SUM(d.debt)/1e9,4) AS total_billions
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name
    HAVING SUM(d.debt) > (
        SELECT AVG(ct) FROM (SELECT SUM(debt) AS ct FROM debt_data GROUP BY country_id) s
    )
    ORDER BY total_billions DESC
""")

run_query(20, "Country Rankings by Total Debt", """
    SELECT c.country_name,
           ROUND(SUM(d.debt)/1e9,4) AS total_billions,
           RANK() OVER (ORDER BY SUM(d.debt) DESC) AS debt_rank
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY debt_rank
""")

# ── ADVANCED (21–30) ──────────────────────────────────────────

run_query(21, "Top 5 Indicators by Global Contribution", """
    SELECT i.indicator_name,
           ROUND(SUM(d.debt)/1e9,4) AS total_billions,
           RANK() OVER (ORDER BY SUM(d.debt) DESC) AS rank_num
    FROM debt_data d JOIN indicators i ON d.indicator_id=i.indicator_id
    GROUP BY i.indicator_name ORDER BY rank_num LIMIT 5
""")

run_query(22, "% Contribution of Each Country", """
    SELECT c.country_name,
           ROUND(SUM(d.debt)/1e9,4) AS total_billions,
           ROUND(SUM(d.debt)/(SELECT SUM(debt) FROM debt_data)*100,2) AS pct_global
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY pct_global DESC
""")

run_query(23, "Top 3 Countries per Indicator", """
    WITH ranked AS (
        SELECT i.indicator_name, c.country_name,
               ROUND(SUM(d.debt)/1e9,4) AS total_billions,
               ROW_NUMBER() OVER (PARTITION BY i.indicator_id ORDER BY SUM(d.debt) DESC) AS rn
        FROM debt_data d
        JOIN countries c ON d.country_id=c.country_id
        JOIN indicators i ON d.indicator_id=i.indicator_id
        GROUP BY i.indicator_id, i.indicator_name, c.country_id, c.country_name
    )
    SELECT indicator_name, country_name, total_billions, rn AS rank_in_indicator
    FROM ranked WHERE rn<=3 ORDER BY indicator_name, rn LIMIT 30
""")

run_query(24, "Max-Min Debt Range per Country", """
    SELECT c.country_name,
           ROUND(MAX(d.debt),2) AS max_debt,
           ROUND(MIN(d.debt),2) AS min_debt,
           ROUND(MAX(d.debt)-MIN(d.debt),2) AS debt_range
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_name ORDER BY debt_range DESC
""")

# Create view first, then query it
try:
    cursor = conn.cursor()
    cursor.execute("DROP VIEW IF EXISTS vw_top10_countries")
    cursor.execute("""
        CREATE VIEW vw_top10_countries AS
        SELECT c.country_name, c.country_code,
               ROUND(SUM(d.debt)/1e9,4) AS total_debt_billions
        FROM debt_data d JOIN countries c ON d.country_id=c.country_id
        GROUP BY c.country_id, c.country_name, c.country_code
        ORDER BY total_debt_billions DESC LIMIT 10
    """)
    conn.commit()
    cursor.close()
except: pass

run_query(25, "View: Top 10 Countries", "SELECT * FROM vw_top10_countries")

run_query(26, "Categorize Countries (High/Medium/Low)", """
    WITH totals AS (
        SELECT c.country_name, SUM(d.debt)/1e9 AS total_b
        FROM debt_data d JOIN countries c ON d.country_id=c.country_id
        GROUP BY c.country_name
    )
    SELECT country_name, ROUND(total_b,4) AS total_billions,
        CASE
            WHEN total_b >= (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_b) FROM totals) THEN 'High Debt'
            WHEN total_b >= (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_b) FROM totals) THEN 'Medium Debt'
            ELSE 'Low Debt'
        END AS debt_category
    FROM totals ORDER BY total_b DESC
""")

run_query(27, "Cumulative Debt per Country", """
    SELECT c.country_name,
           ROUND(SUM(d.debt)/1e9,4) AS country_total,
           ROUND(SUM(SUM(d.debt)) OVER (ORDER BY SUM(d.debt) DESC)/1e9,4) AS cumulative_total
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_id, c.country_name
    ORDER BY country_total DESC
""")

run_query(28, "Indicators Where Avg Debt > Overall Avg", """
    SELECT i.indicator_name,
           ROUND(AVG(d.debt),2) AS avg_debt,
           ROUND((SELECT AVG(debt) FROM debt_data),2) AS overall_avg
    FROM debt_data d JOIN indicators i ON d.indicator_id=i.indicator_id
    GROUP BY i.indicator_id, i.indicator_name
    HAVING AVG(d.debt) > (SELECT AVG(debt) FROM debt_data)
    ORDER BY avg_debt DESC
""")

run_query(29, "Countries Contributing > 5% of Global Debt", """
    SELECT c.country_name,
           ROUND(SUM(d.debt)/1e9,4) AS total_billions,
           ROUND(SUM(d.debt)/(SELECT SUM(debt) FROM debt_data)*100,2) AS pct
    FROM debt_data d JOIN countries c ON d.country_id=c.country_id
    GROUP BY c.country_id, c.country_name
    HAVING pct > 5 ORDER BY pct DESC
""")

run_query(30, "Most Dominant Indicator per Country", """
    WITH ranked AS (
        SELECT c.country_name, i.indicator_name,
               ROUND(SUM(d.debt)/1e9,4) AS total_b,
               ROW_NUMBER() OVER (PARTITION BY c.country_id ORDER BY SUM(d.debt) DESC) AS rn
        FROM debt_data d
        JOIN countries c ON d.country_id=c.country_id
        JOIN indicators i ON d.indicator_id=i.indicator_id
        GROUP BY c.country_id, c.country_name, i.indicator_id, i.indicator_name
    )
    SELECT country_name, indicator_name AS dominant_indicator, total_b AS debt_billions
    FROM ranked WHERE rn=1 ORDER BY debt_billions DESC
""")

# Save all results to file
with open(OUTPUT_FILE, "w") as f:
    f.write("INTERNATIONAL DEBT ANALYSIS — ALL 30 SQL QUERY RESULTS\n")
    f.write("=" * 60 + "\n")
    f.writelines(results_log)

conn.close()
print(f"\n✅ All 30 queries complete!")
print(f"📄 Results saved to: {OUTPUT_FILE}")
print(f"\n🎉 Step 4 Complete! Now run step5_dashboard.py")
