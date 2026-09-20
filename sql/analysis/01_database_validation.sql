SELECT 'staging.hdb_resale' AS object_name, COUNT(*) AS row_count
FROM staging.hdb_resale
UNION ALL
SELECT 'staging.hdb_property', COUNT(*) FROM staging.hdb_property
UNION ALL
SELECT 'core.hdb_block', COUNT(*) FROM core.hdb_block
UNION ALL
SELECT 'core.resale_transaction', COUNT(*) FROM core.resale_transaction
UNION ALL
SELECT 'analytics.resale_enriched', COUNT(*) FROM analytics.resale_enriched
ORDER BY object_name;

SELECT COUNT(*) AS resale_rows_without_property_details
FROM core.resale_transaction AS r
JOIN core.hdb_block AS b ON b.block_id = r.block_id
WHERE NOT b.has_property_record;
