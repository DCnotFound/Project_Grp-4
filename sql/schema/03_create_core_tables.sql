CREATE TABLE IF NOT EXISTS core.town (
    town_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    town_name TEXT NOT NULL UNIQUE,
    CONSTRAINT ck_town_name_not_blank CHECK (BTRIM(town_name) <> '')
);

CREATE TABLE IF NOT EXISTS core.flat_type (
    flat_type_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    flat_type_name TEXT NOT NULL UNIQUE,
    CONSTRAINT ck_flat_type_name_not_blank CHECK (BTRIM(flat_type_name) <> '')
);

CREATE TABLE IF NOT EXISTS core.flat_model (
    flat_model_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    flat_model_name TEXT NOT NULL UNIQUE,
    CONSTRAINT ck_flat_model_name_not_blank CHECK (BTRIM(flat_model_name) <> '')
);

CREATE TABLE IF NOT EXISTS core.hdb_block (
    block_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    address_key TEXT NOT NULL UNIQUE,
    block_no TEXT NOT NULL,
    street_name TEXT NOT NULL,
    property_source_row_id BIGINT UNIQUE,
    has_property_record BOOLEAN NOT NULL,
    max_floor_lvl SMALLINT,
    year_completed SMALLINT,
    residential BOOLEAN,
    commercial BOOLEAN,
    market_hawker BOOLEAN,
    miscellaneous BOOLEAN,
    multistorey_carpark BOOLEAN,
    precinct_pavilion BOOLEAN,
    bldg_contract_town TEXT,
    total_dwelling_units INTEGER,
    sold_1room INTEGER,
    sold_2room INTEGER,
    sold_3room INTEGER,
    sold_4room INTEGER,
    sold_5room INTEGER,
    sold_executive INTEGER,
    sold_multigeneration INTEGER,
    sold_studio_apartment INTEGER,
    rental_1room INTEGER,
    rental_2room INTEGER,
    rental_3room INTEGER,
    rental_other_room INTEGER,
    CONSTRAINT ck_hdb_block_address_not_blank CHECK (BTRIM(address_key) <> ''),
    CONSTRAINT ck_hdb_block_max_floor CHECK (max_floor_lvl IS NULL OR max_floor_lvl > 0),
    CONSTRAINT ck_hdb_block_year_completed CHECK (
        year_completed IS NULL OR year_completed BETWEEN 1900 AND 2100
    ),
    CONSTRAINT ck_hdb_block_unit_counts CHECK (
        (total_dwelling_units IS NULL OR total_dwelling_units >= 0)
        AND (sold_1room IS NULL OR sold_1room >= 0)
        AND (sold_2room IS NULL OR sold_2room >= 0)
        AND (sold_3room IS NULL OR sold_3room >= 0)
        AND (sold_4room IS NULL OR sold_4room >= 0)
        AND (sold_5room IS NULL OR sold_5room >= 0)
        AND (sold_executive IS NULL OR sold_executive >= 0)
        AND (sold_multigeneration IS NULL OR sold_multigeneration >= 0)
        AND (sold_studio_apartment IS NULL OR sold_studio_apartment >= 0)
        AND (rental_1room IS NULL OR rental_1room >= 0)
        AND (rental_2room IS NULL OR rental_2room >= 0)
        AND (rental_3room IS NULL OR rental_3room >= 0)
        AND (rental_other_room IS NULL OR rental_other_room >= 0)
    )
);

CREATE TABLE IF NOT EXISTS core.resale_transaction (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_row_id BIGINT NOT NULL UNIQUE,
    transaction_month DATE NOT NULL,
    town_id SMALLINT NOT NULL REFERENCES core.town(town_id),
    flat_type_id SMALLINT NOT NULL REFERENCES core.flat_type(flat_type_id),
    flat_model_id SMALLINT NOT NULL REFERENCES core.flat_model(flat_model_id),
    block_id BIGINT NOT NULL REFERENCES core.hdb_block(block_id),
    storey_range TEXT NOT NULL,
    storey_lower SMALLINT NOT NULL,
    storey_upper SMALLINT NOT NULL,
    storey_midpoint NUMERIC(4, 1) NOT NULL,
    floor_area_sqm NUMERIC(6, 1) NOT NULL,
    lease_commence_date SMALLINT NOT NULL,
    remaining_lease_years SMALLINT NOT NULL,
    remaining_lease_extra_months SMALLINT NOT NULL,
    remaining_lease_months SMALLINT NOT NULL,
    resale_price NUMERIC(12, 2) NOT NULL,
    possible_duplicate BOOLEAN NOT NULL,
    duplicate_group_size SMALLINT NOT NULL,
    CONSTRAINT ck_resale_month_first_day CHECK (
        EXTRACT(DAY FROM transaction_month) = 1
    ),
    CONSTRAINT ck_resale_storeys CHECK (
        storey_lower > 0
        AND storey_upper >= storey_lower
        AND storey_midpoint BETWEEN storey_lower AND storey_upper
    ),
    CONSTRAINT ck_resale_floor_area CHECK (floor_area_sqm > 0),
    CONSTRAINT ck_resale_price CHECK (resale_price > 0),
    CONSTRAINT ck_resale_lease_month_component CHECK (
        remaining_lease_extra_months BETWEEN 0 AND 11
    ),
    CONSTRAINT ck_resale_lease_total CHECK (
        remaining_lease_months = remaining_lease_years * 12 + remaining_lease_extra_months
    ),
    CONSTRAINT ck_resale_duplicate_group CHECK (duplicate_group_size >= 1)
);
