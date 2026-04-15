import pandas as pd
import matplotlib.pyplot as plt   # Base plotting library
import seaborn as sns             # Pretty charts built on matplotlib
import os

# ── File Paths ───────────────────────────────────────────────
CLEAN_FILE  = "data/cleaned_debt.csv"
CHARTS_DIR  = "charts/"
os.makedirs(CHARTS_DIR, exist_ok=True)  # Create charts folder if it doesn't exist

# ── Style Settings ───────────────────────────────────────────
sns.set_theme(style="whitegrid")           # Clean white background with gridlines
plt.rcParams["figure.dpi"]    = 120        # Chart resolution
plt.rcParams["figure.figsize"] = (12, 6)   # Default chart size (width, height in inches)


# ==============================================================
#  LOAD CLEANED DATA
# ==============================================================
print("=" * 60)
print("  STEP 2: EXPLORATORY DATA ANALYSIS (EDA)")
print("=" * 60)

df = pd.read_csv(CLEAN_FILE)
print(f"\n✅ Cleaned data loaded: {df.shape[0]} rows × {df.shape[1]} columns")


# ==============================================================
#  ANALYSIS 1: GLOBAL DEBT OVERVIEW
# ==============================================================
print("\n" + "-" * 60)
print("  ANALYSIS 1: GLOBAL OVERVIEW")
print("-" * 60)

total_global_debt = df["debt"].sum()
avg_debt          = df["debt"].mean()
min_debt          = df["debt"].min()
max_debt          = df["debt"].max()
num_countries     = df["country_name"].nunique()
num_indicators    = df["indicator_name"].nunique()

print(f"\n🌍 Total Global Debt  : ${total_global_debt:,.2f}")
print(f"📊 Average Debt Value : ${avg_debt:,.2f}")
print(f"⬇️  Minimum Debt Value : ${min_debt:,.2f}")
print(f"⬆️  Maximum Debt Value : ${max_debt:,.2f}")
print(f"🏳️  Number of Countries: {num_countries}")
print(f"📌 Number of Indicators: {num_indicators}")


# ==============================================================
#  ANALYSIS 2: COUNTRY-WISE TOTAL DEBT
# ==============================================================
print("\n" + "-" * 60)
print("  ANALYSIS 2: COUNTRY-WISE DEBT")
print("-" * 60)

# Group by country and sum all their debts
country_debt = (
    df.groupby("country_name")["debt"]
    .sum()
    .sort_values(ascending=False)   # Highest debt first
    .reset_index()
)
country_debt.columns = ["country_name", "total_debt"]

print("\n🏆 Top 10 Countries by Total Debt:")
print(country_debt.head(10).to_string(index=False))

print("\n📉 Bottom 5 Countries by Total Debt:")
print(country_debt.tail(5).to_string(index=False))


# ── CHART 1: Top 10 Countries Bar Chart ─────────────────────
top10 = country_debt.head(10)

fig, ax = plt.subplots(figsize=(14, 7))
bars = ax.barh(
    top10["country_name"][::-1],            # Reverse so highest is at top
    top10["total_debt"][::-1] / 1e9,        # Convert to billions for readability
    color=sns.color_palette("Blues_d", 10)  # Blue gradient colors
)

# Add value labels on each bar
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.5, bar.get_y() + bar.get_height() / 2,
        f"${width:.1f}B",
        va="center", ha="left", fontsize=9
    )

ax.set_xlabel("Total Debt (Billions USD)", fontsize=12)
ax.set_title("Top 10 Countries by Total External Debt", fontsize=15, fontweight="bold")
ax.set_xlim(0, top10["total_debt"].max() / 1e9 * 1.2)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}chart1_top10_countries.png")
plt.close()
print(f"\n✅ Chart 1 saved: chart1_top10_countries.png")


# ── CHART 2: Debt Distribution — All Countries (Pie Chart) ──
top5  = country_debt.head(5)
other = pd.DataFrame([{
    "country_name": "All Others",
    "total_debt": country_debt.iloc[5:]["total_debt"].sum()
}])
pie_data = pd.concat([top5, other], ignore_index=True)

fig, ax = plt.subplots(figsize=(10, 7))
wedges, texts, autotexts = ax.pie(
    pie_data["total_debt"],
    labels=pie_data["country_name"],
    autopct="%1.1f%%",              # Show percentage on each slice
    startangle=140,
    colors=sns.color_palette("Set2", len(pie_data)),
    pctdistance=0.82,
    wedgeprops=dict(edgecolor="white", linewidth=2)
)
ax.set_title("Global Debt Distribution — Top 5 Countries vs Others",
             fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}chart2_debt_distribution_pie.png")
plt.close()
print(f"✅ Chart 2 saved: chart2_debt_distribution_pie.png")


# ==============================================================
#  ANALYSIS 3: INDICATOR-WISE DEBT
# ==============================================================
print("\n" + "-" * 60)
print("  ANALYSIS 3: INDICATOR-WISE DEBT")
print("-" * 60)

# Shorten long indicator names for display
def shorten_name(name, max_len=45):
    return name if len(name) <= max_len else name[:max_len] + "..."

indicator_debt = (
    df.groupby("indicator_name")["debt"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
indicator_debt.columns = ["indicator_name", "total_debt"]
indicator_debt["short_name"] = indicator_debt["indicator_name"].apply(shorten_name)

print("\n📊 All Indicators by Total Debt:")
for _, row in indicator_debt.iterrows():
    print(f"   ${row['total_debt']/1e9:.2f}B — {row['short_name']}")


# ── CHART 3: Indicator-wise Total Debt ──────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette("RdYlGn_r", len(indicator_debt))  # Red=high, Green=low

ax.barh(
    indicator_debt["short_name"][::-1],
    indicator_debt["total_debt"][::-1] / 1e9,
    color=colors
)
ax.set_xlabel("Total Debt (Billions USD)", fontsize=12)
ax.set_title("Total Debt by Indicator Type", fontsize=15, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}chart3_indicator_debt.png")
plt.close()
print(f"\n✅ Chart 3 saved: chart3_indicator_debt.png")


# ==============================================================
#  ANALYSIS 4: DEBT STATISTICS PER COUNTRY
# ==============================================================
print("\n" + "-" * 60)
print("  ANALYSIS 4: DEBT STATISTICS PER COUNTRY")
print("-" * 60)

country_stats = df.groupby("country_name")["debt"].agg(
    total_debt="sum",
    avg_debt="mean",
    max_debt="max",
    min_debt="min",
    num_indicators="count"
).sort_values("total_debt", ascending=False).reset_index()

print("\n📋 Country Statistics (Top 10):")
print(country_stats.head(10).to_string(index=False))

# Average debt per country above the global average
global_avg = df.groupby("country_name")["debt"].sum().mean()
above_avg   = country_debt[country_debt["total_debt"] > global_avg]
print(f"\n📈 Countries above global average total debt ({global_avg/1e9:.2f}B):")
for _, row in above_avg.iterrows():
    print(f"   {row['country_name']}: ${row['total_debt']/1e9:.2f}B")


# ── CHART 4: Box Plot of Debt Distribution per Top Country ──
top8_names = country_debt.head(8)["country_name"].tolist()
top8_df    = df[df["country_name"].isin(top8_names)]

fig, ax = plt.subplots(figsize=(14, 7))
sns.boxplot(
    data=top8_df,
    x="country_name",
    y="debt",
    palette="Set3",
    order=top8_names,
    ax=ax
)
ax.set_ylabel("Debt Value (USD)", fontsize=12)
ax.set_xlabel("Country", fontsize=12)
ax.set_title("Debt Value Spread for Top 8 Countries (Box Plot)", fontsize=14, fontweight="bold")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e9:.1f}B"))
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}chart4_boxplot_top8.png")
plt.close()
print(f"\n✅ Chart 4 saved: chart4_boxplot_top8.png")


# ==============================================================
#  ANALYSIS 5: DEBT CATEGORIZATION
# ==============================================================
print("\n" + "-" * 60)
print("  ANALYSIS 5: DEBT CATEGORIZATION")
print("-" * 60)

# Define thresholds (you can adjust these for your real dataset)
HIGH_THRESHOLD   = country_debt["total_debt"].quantile(0.75)  # Top 25%
MEDIUM_THRESHOLD = country_debt["total_debt"].quantile(0.25)  # Bottom 25%

def categorize(debt):
    if debt >= HIGH_THRESHOLD:
        return "High Debt"
    elif debt >= MEDIUM_THRESHOLD:
        return "Medium Debt"
    else:
        return "Low Debt"

country_debt["category"] = country_debt["total_debt"].apply(categorize)
print(f"\n📊 Debt Category Thresholds:")
print(f"   High Debt   : >= ${HIGH_THRESHOLD/1e9:.2f}B")
print(f"   Medium Debt : ${MEDIUM_THRESHOLD/1e9:.2f}B — ${HIGH_THRESHOLD/1e9:.2f}B")
print(f"   Low Debt    : < ${MEDIUM_THRESHOLD/1e9:.2f}B")

category_counts = country_debt["category"].value_counts()
print(f"\n🏷️  Countries per category:")
print(category_counts.to_string())


# ── CHART 5: Debt Category Count ────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
category_colors = {"High Debt": "#e74c3c", "Medium Debt": "#f39c12", "Low Debt": "#2ecc71"}
bars = ax.bar(
    category_counts.index,
    category_counts.values,
    color=[category_colors[c] for c in category_counts.index],
    edgecolor="white", linewidth=2
)
for bar in bars:
    ax.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
        str(int(bar.get_height())),
        ha="center", va="bottom", fontsize=13, fontweight="bold"
    )
ax.set_ylabel("Number of Countries", fontsize=12)
ax.set_title("Countries by Debt Category", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}chart5_debt_categories.png")
plt.close()
print(f"\n✅ Chart 5 saved: chart5_debt_categories.png")


# ==============================================================
#  ANALYSIS 6: PERCENTAGE CONTRIBUTION
# ==============================================================
print("\n" + "-" * 60)
print("  ANALYSIS 6: % CONTRIBUTION TO GLOBAL DEBT")
print("-" * 60)

country_debt["pct_contribution"] = (
    country_debt["total_debt"] / total_global_debt * 100
).round(2)

print("\n🌐 Top 10 Countries by % Contribution:")
print(country_debt[["country_name", "pct_contribution"]].head(10).to_string(index=False))

above_5pct = country_debt[country_debt["pct_contribution"] > 5]
print(f"\n⚠️  Countries contributing more than 5% of global debt: {len(above_5pct)}")
for _, row in above_5pct.iterrows():
    print(f"   {row['country_name']}: {row['pct_contribution']}%")


# ── CHART 6: Heatmap — Country vs Indicator Debt ────────────
# Pivot table: rows = countries, columns = indicators
pivot = df.pivot_table(
    index="country_name",
    columns="indicator_code",
    values="debt",
    aggfunc="sum"
).fillna(0)  # Fill missing combinations with 0

# Keep only top 10 countries for readability
top10_names = country_debt.head(10)["country_name"].tolist()
pivot_top10 = pivot.loc[pivot.index.isin(top10_names)]

fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(
    pivot_top10 / 1e9,          # Convert to billions
    annot=True,                 # Show values inside cells
    fmt=".1f",                  # 1 decimal place
    cmap="YlOrRd",              # Yellow → Orange → Red
    linewidths=0.5,
    ax=ax,
    cbar_kws={"label": "Debt (Billions USD)"}
)
ax.set_title("Debt Heatmap — Top 10 Countries × Indicators (Billions USD)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Indicator Code", fontsize=11)
ax.set_ylabel("Country", fontsize=11)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}chart6_heatmap.png")
plt.close()
print(f"\n✅ Chart 6 saved: chart6_heatmap.png")


# ==============================================================
#  FINAL SUMMARY
# ==============================================================
print("\n" + "=" * 60)
print("  EDA COMPLETE — KEY INSIGHTS")
print("=" * 60)
print(f"""
🔑 KEY FINDINGS:
   1. Total Global Debt analysed  : ${total_global_debt/1e9:.2f} Billion USD
   2. Highest debt country        : {country_debt.iloc[0]['country_name']} (${country_debt.iloc[0]['total_debt']/1e9:.2f}B)
   3. Lowest debt country         : {country_debt.iloc[-1]['country_name']} (${country_debt.iloc[-1]['total_debt']/1e9:.2f}B)
   4. Top debt indicator          : {indicator_debt.iloc[0]['short_name']}
   5. Countries above avg debt    : {len(above_avg)} out of {num_countries}
   6. Countries with >5% global   : {len(above_5pct)}
   7. Charts saved                : {CHARTS_DIR}
