CREATE INDEX IF NOT EXISTS idx_staging_resale_address_key
    ON staging.hdb_resale(address_key);

CREATE INDEX IF NOT EXISTS idx_staging_property_address_key
    ON staging.hdb_property(address_key);

CREATE INDEX IF NOT EXISTS idx_resale_transaction_month
    ON core.resale_transaction(transaction_month);

CREATE INDEX IF NOT EXISTS idx_resale_transaction_town_month
    ON core.resale_transaction(town_id, transaction_month);

CREATE INDEX IF NOT EXISTS idx_resale_transaction_block
    ON core.resale_transaction(block_id);

CREATE INDEX IF NOT EXISTS idx_resale_transaction_flat_type
    ON core.resale_transaction(flat_type_id);
