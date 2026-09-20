INSERT INTO core.hdb_block (
    address_key,
    block_no,
    street_name,
    property_source_row_id,
    has_property_record,
    max_floor_lvl,
    year_completed,
    residential,
    commercial,
    market_hawker,
    miscellaneous,
    multistorey_carpark,
    precinct_pavilion,
    bldg_contract_town,
    total_dwelling_units,
    sold_1room,
    sold_2room,
    sold_3room,
    sold_4room,
    sold_5room,
    sold_executive,
    sold_multigeneration,
    sold_studio_apartment,
    rental_1room,
    rental_2room,
    rental_3room,
    rental_other_room
)
SELECT
    address_key,
    blk_no,
    street,
    property_row_id,
    TRUE,
    max_floor_lvl,
    year_completed,
    residential,
    commercial,
    market_hawker,
    miscellaneous,
    multistorey_carpark,
    precinct_pavilion,
    bldg_contract_town,
    total_dwelling_units,
    "1room_sold",
    "2room_sold",
    "3room_sold",
    "4room_sold",
    "5room_sold",
    exec_sold,
    multigen_sold,
    studio_apartment_sold,
    "1room_rental",
    "2room_rental",
    "3room_rental",
    other_room_rental
FROM staging.hdb_property
ORDER BY property_row_id;

INSERT INTO core.hdb_block (
    address_key,
    block_no,
    street_name,
    has_property_record
)
SELECT DISTINCT ON (r.address_key)
    r.address_key,
    r.block,
    r.street_name,
    FALSE
FROM staging.hdb_resale AS r
LEFT JOIN core.hdb_block AS b
    ON b.address_key = r.address_key
WHERE b.block_id IS NULL
ORDER BY r.address_key, r.source_row_id;

