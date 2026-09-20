INSERT INTO core.town (town_name)
SELECT DISTINCT town
FROM staging.hdb_resale
ORDER BY town;

INSERT INTO core.flat_type (flat_type_name)
SELECT DISTINCT flat_type
FROM staging.hdb_resale
ORDER BY flat_type;

INSERT INTO core.flat_model (flat_model_name)
SELECT DISTINCT flat_model
FROM staging.hdb_resale
ORDER BY flat_model;

