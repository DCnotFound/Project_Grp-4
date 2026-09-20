CREATE OR REPLACE VIEW analytics.resale_enriched AS
SELECT
    r.transaction_id,
    r.source_row_id,
    r.transaction_month,
    t.town_name,
    ft.flat_type_name,
    fm.flat_model_name,
    b.block_id,
    b.block_no,
    b.street_name,
    b.address_key,
    b.has_property_record,
    r.storey_range,
    r.storey_lower,
    r.storey_upper,
    r.storey_midpoint,
    r.floor_area_sqm,
    r.resale_price,
    ROUND(r.resale_price / NULLIF(r.floor_area_sqm, 0), 2) AS price_per_sqm,
    r.lease_commence_date,
    r.remaining_lease_years,
    r.remaining_lease_extra_months,
    r.remaining_lease_months,
    b.year_completed,
    EXTRACT(YEAR FROM r.transaction_month)::INTEGER - b.year_completed AS building_age_at_sale,
    b.max_floor_lvl,
    b.residential,
    b.commercial,
    b.market_hawker,
    b.miscellaneous,
    b.multistorey_carpark,
    b.precinct_pavilion,
    b.total_dwelling_units,
    r.possible_duplicate,
    r.duplicate_group_size
FROM core.resale_transaction AS r
JOIN core.town AS t
    ON t.town_id = r.town_id
JOIN core.flat_type AS ft
    ON ft.flat_type_id = r.flat_type_id
JOIN core.flat_model AS fm
    ON fm.flat_model_id = r.flat_model_id
JOIN core.hdb_block AS b
    ON b.block_id = r.block_id;
