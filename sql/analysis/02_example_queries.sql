SELECT
    town_name,
    COUNT(*) AS transaction_count,
    ROUND(AVG(price_per_sqm), 2) AS average_price_per_sqm
FROM analytics.resale_enriched
GROUP BY town_name
ORDER BY average_price_per_sqm DESC;

SELECT
    DATE_TRUNC('year', transaction_month)::DATE AS transaction_year,
    flat_type_name,
    COUNT(*) AS transaction_count,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)::NUMERIC, 2)
        AS median_resale_price
FROM analytics.resale_enriched
GROUP BY transaction_year, flat_type_name
ORDER BY transaction_year, flat_type_name;

