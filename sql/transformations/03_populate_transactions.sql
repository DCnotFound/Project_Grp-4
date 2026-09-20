INSERT INTO core.resale_transaction (
    source_row_id,
    transaction_month,
    town_id,
    flat_type_id,
    flat_model_id,
    block_id,
    storey_range,
    storey_lower,
    storey_upper,
    storey_midpoint,
    floor_area_sqm,
    lease_commence_date,
    remaining_lease_years,
    remaining_lease_extra_months,
    remaining_lease_months,
    resale_price,
    possible_duplicate,
    duplicate_group_size
)
SELECT
    r.source_row_id,
    r.month,
    t.town_id,
    ft.flat_type_id,
    fm.flat_model_id,
    b.block_id,
    r.storey_range,
    r.storey_lower,
    r.storey_upper,
    r.storey_midpoint,
    r.floor_area_sqm,
    r.lease_commence_date,
    r.remaining_lease_years,
    r.remaining_lease_extra_months,
    r.remaining_lease_months,
    r.resale_price,
    r.possible_duplicate,
    r.duplicate_group_size
FROM staging.hdb_resale AS r
JOIN core.town AS t
    ON t.town_name = r.town
JOIN core.flat_type AS ft
    ON ft.flat_type_name = r.flat_type
JOIN core.flat_model AS fm
    ON fm.flat_model_name = r.flat_model
JOIN core.hdb_block AS b
    ON b.address_key = r.address_key
ORDER BY r.source_row_id;

