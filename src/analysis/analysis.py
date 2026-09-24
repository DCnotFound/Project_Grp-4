import pandas as pd
import matplotlib.pyplot as plt

from dbconnection import get_connection


# ============================================================
# HELPER FUNCTION
# ============================================================

def run_query(query):
    """
    Runs a SQL query against PostgreSQL and returns
    the result as a Pandas DataFrame.
    """
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute(query)

    rows = cursor.fetchall()
    columns = [desc.name for desc in cursor.description]

    cursor.close()
    conn.close()

    return pd.DataFrame(rows, columns=columns)


# ============================================================
# ANALYSIS 1
# PRICE TRENDS OVER TIME
# ============================================================

query_price_trend = """
SELECT
    EXTRACT(YEAR FROM transaction_month)::INT AS transaction_year,
    COUNT(*) AS transaction_count,
    ROUND(AVG(resale_price), 2) AS average_resale_price,
    ROUND(
        PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY resale_price)::NUMERIC,
        2
    ) AS median_resale_price
FROM analytics.resale_enriched
GROUP BY transaction_year
ORDER BY transaction_year;
"""

price_trend_df = run_query(query_price_trend)

print("\n==============================")
print("ANALYSIS 1: PRICE TREND")
print("==============================")
print(price_trend_df)

plt.figure(figsize=(10, 6))

plt.plot(
    price_trend_df["transaction_year"],
    price_trend_df["median_resale_price"],
    marker="o"
)

plt.xlabel("Year")
plt.ylabel("Median Resale Price (SGD)")
plt.title("HDB Median Resale Price Over Time")

plt.xticks(price_trend_df["transaction_year"])

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 2
# PRICE PER SQM BY TOWN
# ============================================================

query_town = """
SELECT
    town_name,
    COUNT(*) AS transaction_count,
    ROUND(AVG(price_per_sqm), 2) AS average_price_per_sqm
FROM analytics.resale_enriched
GROUP BY town_name
ORDER BY average_price_per_sqm DESC;
"""

town_price_df = run_query(query_town)

print("\n==============================")
print("ANALYSIS 2: PRICE PER SQM BY TOWN")
print("==============================")
print(town_price_df)

print("\nTop 5 towns:")
print(town_price_df.head())

print("\nBottom 5 towns:")
print(town_price_df.tail())

plt.figure(figsize=(10, 8))

plt.barh(
    town_price_df["town_name"],
    town_price_df["average_price_per_sqm"]
)

plt.xlabel("Average Resale Price per sqm (SGD)")
plt.ylabel("Town")
plt.title("Average HDB Resale Price per sqm by Town")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 3
# FLAT TYPE VS RESALE PRICE
# ============================================================

query_flat_type = """
SELECT
    flat_type_name,
    COUNT(*) AS transaction_count,
    ROUND(AVG(resale_price), 2) AS average_resale_price,
    ROUND(
        PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY resale_price)::NUMERIC,
        2
    ) AS median_resale_price
FROM analytics.resale_enriched
GROUP BY flat_type_name
ORDER BY median_resale_price;
"""

flat_type_df = run_query(query_flat_type)

print("\n==============================")
print("ANALYSIS 3: FLAT TYPE VS PRICE")
print("==============================")
print(flat_type_df)

plt.figure(figsize=(10, 6))

plt.bar(
    flat_type_df["flat_type_name"],
    flat_type_df["median_resale_price"]
)

plt.xlabel("Flat Type")
plt.ylabel("Median Resale Price (SGD)")
plt.title("Median HDB Resale Price by Flat Type")

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 4
# REMAINING LEASE VS PRICE
# ============================================================

query_lease = """
SELECT
    remaining_lease_years,
    COUNT(*) AS transaction_count,
    ROUND(AVG(resale_price), 2) AS average_resale_price,
    ROUND(AVG(price_per_sqm), 2) AS average_price_per_sqm
FROM analytics.resale_enriched
GROUP BY remaining_lease_years
ORDER BY remaining_lease_years;
"""

lease_df = run_query(query_lease)

print("\n==============================")
print("ANALYSIS 4: REMAINING LEASE VS PRICE")
print("==============================")
print(lease_df)

plt.figure(figsize=(10, 6))

plt.plot(
    lease_df["remaining_lease_years"],
    lease_df["average_price_per_sqm"]
)

plt.xlabel("Remaining Lease (Years)")
plt.ylabel("Average Resale Price per sqm (SGD)")
plt.title("Remaining Lease vs HDB Resale Price per sqm")

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 5
# STOREY VS PRICE
# ============================================================

query_storey = """
SELECT
    storey_range,
    storey_lower,
    COUNT(*) AS transaction_count,
    ROUND(AVG(resale_price), 2) AS average_resale_price
FROM analytics.resale_enriched
GROUP BY storey_range, storey_lower
ORDER BY storey_lower;
"""

storey_df = run_query(query_storey)

print("\n==============================")
print("ANALYSIS 5: STOREY VS PRICE")
print("==============================")
print(storey_df)

plt.figure(figsize=(12, 6))

plt.plot(
    storey_df["storey_range"],
    storey_df["average_resale_price"],
    marker="o"
)

plt.xlabel("Storey Range")
plt.ylabel("Average Resale Price (SGD)")
plt.title("Average HDB Resale Price by Storey Range")

plt.xticks(rotation=90)

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 6A
# EXACT BUILDING AGE VS PRICE PER SQM
# ============================================================

query_age = """
SELECT
    building_age_at_sale,
    COUNT(*) AS transaction_count,
    ROUND(AVG(price_per_sqm), 2) AS average_price_per_sqm
FROM analytics.resale_enriched
WHERE building_age_at_sale IS NOT NULL
GROUP BY building_age_at_sale
ORDER BY building_age_at_sale;
"""

age_df = run_query(query_age)

print("\n==============================")
print("ANALYSIS 6A: BUILDING AGE VS PRICE")
print("==============================")
print(age_df)

plt.figure(figsize=(10, 6))

plt.plot(
    age_df["building_age_at_sale"],
    age_df["average_price_per_sqm"]
)

plt.xlabel("Building Age at Time of Sale (Years)")
plt.ylabel("Average Resale Price per sqm (SGD)")
plt.title("Building Age vs HDB Resale Price per sqm")

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 6B
# BUILDING AGE GROUP VS PRICE PER SQM
# ============================================================

query_age_grouped = """
SELECT
    CASE
        WHEN building_age_at_sale < 10 THEN '0-9'
        WHEN building_age_at_sale < 20 THEN '10-19'
        WHEN building_age_at_sale < 30 THEN '20-29'
        WHEN building_age_at_sale < 40 THEN '30-39'
        WHEN building_age_at_sale < 50 THEN '40-49'
        WHEN building_age_at_sale < 60 THEN '50-59'
        WHEN building_age_at_sale < 70 THEN '60-69'
        ELSE '70+'
    END AS age_group,
    MIN(building_age_at_sale) AS age_group_order,
    COUNT(*) AS transaction_count,
    ROUND(AVG(price_per_sqm), 2) AS average_price_per_sqm
FROM analytics.resale_enriched
WHERE building_age_at_sale IS NOT NULL
GROUP BY age_group
ORDER BY age_group_order;
"""

age_grouped_df = run_query(query_age_grouped)

print("\n==============================")
print("ANALYSIS 6B: BUILDING AGE GROUPS")
print("==============================")
print(age_grouped_df)

plt.figure(figsize=(10, 6))

plt.bar(
    age_grouped_df["age_group"],
    age_grouped_df["average_price_per_sqm"]
)

plt.xlabel("Building Age Group (Years)")
plt.ylabel("Average Resale Price per sqm (SGD)")
plt.title("Average HDB Resale Price per sqm by Building Age Group")

plt.tight_layout()
plt.show()


# ============================================================
# ANALYSIS 6C
# MARKET YEAR VS BUILDING AGE COMPARISON
# ============================================================

query_year_price = """
SELECT
    EXTRACT(YEAR FROM transaction_month)::INT AS transaction_year,
    COUNT(*) AS transaction_count,
    ROUND(AVG(price_per_sqm), 2) AS average_price_per_sqm
FROM analytics.resale_enriched
GROUP BY transaction_year
ORDER BY transaction_year;
"""

year_price_df = run_query(query_year_price)

print("\n==============================")
print("ANALYSIS 6C: PRICE PER SQM BY YEAR")
print("==============================")
print(year_price_df)


# Reuse the grouped building-age query from Analysis 6B
age_grouped_df = run_query(query_age_grouped)


# ------------------------------------------------------------
# TWO GRAPHS IN ONE FIGURE
# ------------------------------------------------------------

fig, axes = plt.subplots(
    1,
    2,
    figsize=(15, 6)
)


# ------------------------------------------------------------
# LEFT GRAPH
# PRICE PER SQM OVER TIME
# ------------------------------------------------------------

axes[0].plot(
    year_price_df["transaction_year"],
    year_price_df["average_price_per_sqm"],
    marker="o"
)

axes[0].set_xlabel("Transaction Year")
axes[0].set_ylabel("Average Resale Price per sqm (SGD)")
axes[0].set_title("HDB Resale Price per sqm Over Time")

axes[0].set_xticks(
    year_price_df["transaction_year"]
)


# ------------------------------------------------------------
# RIGHT GRAPH
# PRICE PER SQM BY BUILDING AGE GROUP
# ------------------------------------------------------------

axes[1].bar(
    age_grouped_df["age_group"],
    age_grouped_df["average_price_per_sqm"]
)

axes[1].set_xlabel("Building Age Group (Years)")
axes[1].set_ylabel("Average Resale Price per sqm (SGD)")
axes[1].set_title("HDB Resale Price per sqm by Building Age")


# ------------------------------------------------------------
# FINAL FIGURE SETTINGS
# ------------------------------------------------------------

fig.suptitle(
    "Comparison of Market Year and Building Age on HDB Resale Price per sqm",
    fontsize=14
)

plt.tight_layout()
plt.show()