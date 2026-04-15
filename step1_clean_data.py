# ── Imports ──────────────────────────────────────────────────
import pandas as pd   # For working with tables (DataFrames)
import numpy as np    # For math operations
import os             # For file paths

# ── File Paths ───────────────────────────────────────────────
RAW_FILE    = "data/international_debt.csv"   # Your downloaded dataset
CLEAN_FILE  = "data/cleaned_debt.csv"         # Output: cleaned version


# ==============================================================
#  SECTION 1: LOAD THE DATA
# ==============================================================
print("=" * 55)
print("  STEP 1: LOADING THE DATA")
print("=" * 55)

# pd.read_csv() reads a CSV file and turns it into a DataFrame
df = pd.read_csv(RAW_FILE)

print(f"\n✅ File loaded successfully!")
print(f"   Rows    : {df.shape[0]}")        # shape[0] = number of rows
print(f"   Columns : {df.shape[1]}")        # shape[1] = number of columns
print(f"\n📋 Column names:")
for col in df.columns:
    print(f"   - {col}")

# .head() shows first 5 rows — always do this first to understand data
print(f"\n📄 First 5 rows of raw data:")
print(df.head())

# .dtypes shows what type each column is (int, float, object/text)
print(f"\n🔢 Data types:")
print(df.dtypes)


# ==============================================================
#  SECTION 2: UNDERSTAND THE DATA (INSPECTION)
# ==============================================================
print("\n" + "=" * 55)
print("  STEP 2: INSPECTING THE DATA")
print("=" * 55)

# .info() gives a quick summary of the DataFrame
print("\n📊 Dataset Info:")
df.info()

# Check for missing values in each column
print("\n❓ Missing values per column:")
missing = df.isnull().sum()  # Count nulls in each column
missing_pct = (missing / len(df) * 100).round(2)  # As percentage
missing_report = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_pct
})
print(missing_report)

# Check for duplicate rows
duplicate_count = df.duplicated().sum()
print(f"\n🔁 Duplicate rows found: {duplicate_count}")

# Basic statistics for numeric columns
print("\n📈 Statistical summary of 'debt' column:")
print(df["debt"].describe())


# ==============================================================
#  SECTION 3: CLEAN THE DATA
# ==============================================================
print("\n" + "=" * 55)
print("  STEP 3: CLEANING THE DATA")
print("=" * 55)

# --- 3a. Clean column names ---
# Remove extra spaces, make lowercase, replace spaces with underscore
# Example: "Country Name" → "country_name"
df.columns = (
    df.columns
    .str.strip()           # Remove leading/trailing spaces
    .str.lower()           # Convert to lowercase
    .str.replace(" ", "_") # Replace spaces with underscore
)
print(f"\n✅ Column names cleaned: {list(df.columns)}")


# --- 3b. Remove duplicate rows ---
before_dedup = len(df)
df.drop_duplicates(inplace=True)   # inplace=True modifies df directly
after_dedup = len(df)
print(f"\n✅ Duplicates removed: {before_dedup - after_dedup} rows dropped")
print(f"   Rows remaining: {after_dedup}")


# --- 3c. Handle missing values in the 'debt' column ---
# Strategy: Drop rows where debt is completely missing
# (We cannot guess financial values — dropping is safer than guessing)
before_null = len(df)
df.dropna(subset=["debt"], inplace=True)   # Drop rows where debt is NaN
after_null = len(df)
print(f"\n✅ Rows with missing 'debt' removed: {before_null - after_null} rows dropped")
print(f"   Rows remaining: {after_null}")


# --- 3d. Convert data types ---
# Make sure 'debt' is a number (float), not text
df["debt"] = pd.to_numeric(df["debt"], errors="coerce")
# errors="coerce" → if conversion fails, set value to NaN (instead of crashing)

# Drop any rows that became NaN after conversion
df.dropna(subset=["debt"], inplace=True)
print(f"\n✅ Data types after conversion:")
print(df.dtypes)


# --- 3e. Remove rows with zero or negative debt (not meaningful) ---
before_zero = len(df)
df = df[df["debt"] > 0]
print(f"\n✅ Zero/negative debt rows removed: {before_zero - len(df)} rows dropped")


# --- 3f. Reset the index after all row removals ---
# After dropping rows, the index numbers have gaps — reset them to 0,1,2,3...
df.reset_index(drop=True, inplace=True)


# ==============================================================
#  SECTION 4: VERIFY THE CLEANED DATA
# ==============================================================
print("\n" + "=" * 55)
print("  STEP 4: VERIFYING CLEANED DATA")
print("=" * 55)

print(f"\n📊 Final dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\n❓ Missing values after cleaning:")
print(df.isnull().sum())
print(f"\n🔁 Duplicate rows after cleaning: {df.duplicated().sum()}")
print(f"\n📄 Sample of cleaned data:")
print(df.head(10))

# Quick summary stats
print(f"\n📈 Debt column summary:")
print(f"   Min  : ${df['debt'].min():,.2f}")
print(f"   Max  : ${df['debt'].max():,.2f}")
print(f"   Mean : ${df['debt'].mean():,.2f}")
print(f"   Total: ${df['debt'].sum():,.2f}")

print(f"\n🌍 Unique countries: {df['country_name'].nunique()}")
print(f"📌 Unique indicators: {df['indicator_name'].nunique()}")


# ==============================================================
#  SECTION 5: SAVE CLEANED DATA
# ==============================================================
df.to_csv(CLEAN_FILE, index=False)
print(f"\n✅ Cleaned data saved to: '{CLEAN_FILE}'")
print("\n🎉 Step 1 Complete! Now run step2_eda.py")
