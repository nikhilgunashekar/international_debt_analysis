# ── Imports ──────────────────────────────────────────────────
import pandas as pd
import mysql.connector         # To connect to MySQL
from mysql.connector import Error

# ── Database Configuration ───────────────────────────────────
# ⚠️  CHANGE THESE to match YOUR MySQL setup
DB_CONFIG = {
    "host"    : "localhost",    # Usually 'localhost'
    "user"    : "root",         # Your MySQL username
    "password": "your_password", # ← CHANGE THIS to your MySQL password
    "database": "debt_db"       # The database we will create
}

CLEAN_FILE = "data/cleaned_debt.csv"


# ==============================================================
#  HELPER FUNCTION: CONNECT TO MYSQL
# ==============================================================
def connect_to_mysql(include_db=True):
    """
    Creates and returns a MySQL connection.
    include_db=False → connect without specifying a database (for CREATE DATABASE)
    include_db=True  → connect directly to debt_db
    """
    try:
        config = DB_CONFIG.copy()
        if not include_db:
            del config["database"]  # Remove database key for initial connection
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        print("\n💡 Troubleshooting Tips:")
        print("   1. Make sure MySQL server is running")
        print("   2. Check your username and password in DB_CONFIG")
        print("   3. Run: mysql -u root -p  to test connection manually")
        return None


# ==============================================================
#  STEP 3A: CREATE DATABASE
# ==============================================================
print("=" * 60)
print("  STEP 3: DATABASE SETUP & DATA INSERTION")
print("=" * 60)

print("\n📡 Connecting to MySQL server...")
conn = connect_to_mysql(include_db=False)
if conn is None:
    exit(1)

cursor = conn.cursor()

# Create the database if it doesn't exist yet
cursor.execute("CREATE DATABASE IF NOT EXISTS debt_db")
print("✅ Database 'debt_db' created (or already exists)")

cursor.close()
conn.close()


# ==============================================================
#  STEP 3B: CREATE TABLES
# ==============================================================
print("\n📋 Creating tables...")
conn = connect_to_mysql(include_db=True)
cursor = conn.cursor()

# ── TABLE 1: countries ───────────────────────────────────────
create_countries_table = """
CREATE TABLE IF NOT EXISTS countries (
    country_id   INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(150) NOT NULL,
    country_code VARCHAR(10)  NOT NULL,
    UNIQUE KEY uq_country_code (country_code)   -- No duplicate country codes
);
"""

# ── TABLE 2: indicators ──────────────────────────────────────
create_indicators_table = """
CREATE TABLE IF NOT EXISTS indicators (
    indicator_id   INT AUTO_INCREMENT PRIMARY KEY,
    indicator_name VARCHAR(400) NOT NULL,
    indicator_code VARCHAR(50)  NOT NULL,
    UNIQUE KEY uq_indicator_code (indicator_code)
);
"""

# ── TABLE 3: debt_data ───────────────────────────────────────
# This is the "fact table" — it links countries + indicators + debt value
create_debt_data_table = """
CREATE TABLE IF NOT EXISTS debt_data (
    debt_id      INT AUTO_INCREMENT PRIMARY KEY,
    country_id   INT            NOT NULL,
    indicator_id INT            NOT NULL,
    debt         DECIMAL(25, 2) NOT NULL,
    FOREIGN KEY (country_id)   REFERENCES countries(country_id)   ON DELETE CASCADE,
    FOREIGN KEY (indicator_id) REFERENCES indicators(indicator_id) ON DELETE CASCADE
);
"""

# Execute the CREATE TABLE statements
for sql, name in [
    (create_countries_table,  "countries"),
    (create_indicators_table, "indicators"),
    (create_debt_data_table,  "debt_data")
]:
    cursor.execute(sql)
    print(f"   ✅ Table '{name}' ready")

conn.commit()


# ==============================================================
#  STEP 3C: LOAD CLEANED DATA
# ==============================================================
print("\n📂 Loading cleaned CSV...")
df = pd.read_csv(CLEAN_FILE)
print(f"   Rows loaded: {len(df)}")


# ==============================================================
#  STEP 3D: INSERT INTO COUNTRIES TABLE
# ==============================================================
print("\n⬆️  Inserting countries...")

# Get unique countries from the dataset
unique_countries = df[["country_name", "country_code"]].drop_duplicates()

insert_country_sql = """
    INSERT IGNORE INTO countries (country_name, country_code)
    VALUES (%s, %s)
"""
# INSERT IGNORE → skip if country_code already exists (no crash on re-run)

country_data = list(unique_countries.itertuples(index=False, name=None))
cursor.executemany(insert_country_sql, country_data)
conn.commit()
print(f"   ✅ {cursor.rowcount} new country rows inserted")


# ==============================================================
#  STEP 3E: INSERT INTO INDICATORS TABLE
# ==============================================================
print("\n⬆️  Inserting indicators...")

unique_indicators = df[["indicator_name", "indicator_code"]].drop_duplicates()

insert_indicator_sql = """
    INSERT IGNORE INTO indicators (indicator_name, indicator_code)
    VALUES (%s, %s)
"""
indicator_data = list(unique_indicators.itertuples(index=False, name=None))
cursor.executemany(insert_indicator_sql, indicator_data)
conn.commit()
print(f"   ✅ {cursor.rowcount} new indicator rows inserted")


# ==============================================================
#  STEP 3F: BUILD ID LOOKUP MAPS
# ==============================================================
# We need to convert country_name → country_id and indicator_code → indicator_id
# because debt_data stores IDs, not text

print("\n🔍 Building ID lookup maps...")

# Fetch country IDs from MySQL
cursor.execute("SELECT country_id, country_code FROM countries")
country_id_map = {row[1]: row[0] for row in cursor.fetchall()}
# Example: {"CHN": 1, "USA": 2, ...}

# Fetch indicator IDs from MySQL
cursor.execute("SELECT indicator_id, indicator_code FROM indicators")
indicator_id_map = {row[1]: row[0] for row in cursor.fetchall()}

print(f"   Country IDs mapped  : {len(country_id_map)}")
print(f"   Indicator IDs mapped: {len(indicator_id_map)}")


# ==============================================================
#  STEP 3G: INSERT INTO DEBT_DATA TABLE
# ==============================================================
print("\n⬆️  Inserting debt data...")

# Clear old debt_data before re-inserting (so script can run multiple times)
cursor.execute("DELETE FROM debt_data")
conn.commit()

insert_debt_sql = """
    INSERT INTO debt_data (country_id, indicator_id, debt)
    VALUES (%s, %s, %s)
"""

debt_rows = []
skipped   = 0

for _, row in df.iterrows():
    c_id = country_id_map.get(row["country_code"])
    i_id = indicator_id_map.get(row["indicator_code"])

    if c_id is None or i_id is None:
        skipped += 1
        continue  # Skip if we can't find the ID (shouldn't happen)

    debt_rows.append((c_id, i_id, float(row["debt"])))

# Insert all rows at once (faster than one-by-one)
cursor.executemany(insert_debt_sql, debt_rows)
conn.commit()

print(f"   ✅ {len(debt_rows)} debt rows inserted")
if skipped:
    print(f"   ⚠️  {skipped} rows skipped (unmapped IDs)")


# ==============================================================
#  STEP 3H: VERIFY THE DATA
# ==============================================================
print("\n" + "-" * 60)
print("  VERIFICATION: CHECKING DATABASE")
print("-" * 60)

verification_queries = {
    "Total countries"  : "SELECT COUNT(*) FROM countries",
    "Total indicators" : "SELECT COUNT(*) FROM indicators",
    "Total debt rows"  : "SELECT COUNT(*) FROM debt_data",
    "Total global debt": "SELECT ROUND(SUM(debt)/1e9, 2) FROM debt_data",
}

for label, query in verification_queries.items():
    cursor.execute(query)
    result = cursor.fetchone()[0]
    print(f"   {label:<22}: {result}")


# ==============================================================
#  CLOSE CONNECTION
# ==============================================================
cursor.close()
conn.close()

print(f"""
✅ Database setup complete!
   Database : debt_db
   Tables   : countries, indicators, debt_data
   
