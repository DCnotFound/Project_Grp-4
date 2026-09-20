# Database Implementation Guide

## 1. Purpose

The database integrates two official Singapore HDB datasets: 240,807 resale transactions and 13,357 property records. It supports analysis of price trends, towns, flat characteristics, remaining lease, storey level and building age.

## 2. Architecture

```text
data.gov.sg source files
          ↓
Python preprocessing and validation
          ↓
staging.hdb_resale + staging.hdb_property
          ↓
normalized core tables
          ↓
analytics.resale_enriched
          ↓
SQL/Python analysis
```

PostgreSQL runs locally in Docker. A named Docker volume preserves the database between container restarts. `.env` stores local connection settings and is excluded from Git.

## 3. Staging schema

`staging.hdb_resale` and `staging.hdb_property` closely match the processed CSV files. They form a controlled landing area where loaded row counts can be checked before normalization. `staging.load_audit` records successful database loads.

The loader truncates staging before every import. Therefore, rerunning it replaces the staging snapshot instead of appending another 240,807 rows.

## 4. Core schema

| Table | Purpose |
|---|---|
| `core.town` | One record per town |
| `core.flat_type` | One record per flat-type category |
| `core.flat_model` | One record per flat-model category |
| `core.hdb_block` | One record per normalized block and street address |
| `core.resale_transaction` | One record per published resale source row |

The category tables remove repeated category text from the transaction table. `core.resale_transaction` references them and `core.hdb_block` through foreign keys.

The property file provides 13,357 unique addresses. One additional address, `82|MACPHERSON LANE`, appears only in the resale file. The block transformation creates it with `has_property_record = FALSE` and null property attributes. This retains all three of its transactions without inventing property values.

## 5. Integrity rules

The core model enforces:

- Primary keys for every table
- Unique town, flat-type and flat-model names
- Unique HDB `address_key`
- Unique resale `source_row_id`
- Foreign keys from every transaction to its categories and block
- Positive floor area and resale price
- Valid storey bounds
- Valid lease month components
- Non-negative dwelling-unit counts

Duplicate-looking resale rows are not removed. Since the source omits transaction and unit identifiers, identical published attributes may represent separate legitimate sales. The fields `possible_duplicate` and `duplicate_group_size` make the uncertainty visible.

## 6. Analytics view

`analytics.resale_enriched` joins the normalized model and exposes readable category names and property attributes. It derives:

```sql
resale_price / NULLIF(floor_area_sqm, 0) AS price_per_sqm
```

and:

```sql
EXTRACT(YEAR FROM transaction_month) - year_completed AS building_age_at_sale
```

Analysts can query this view without repeatedly writing four joins. The view does not copy the data and is not a separate warehouse.

## 7. Indexes

Indexes support common joins and filters:

- Staging address keys
- Transaction month
- Town plus transaction month
- Transaction block
- Flat type

## 8. Loading order

1. Create the PostgreSQL schemas.
2. Create staging tables.
3. Create core tables and indexes.
4. Truncate staging and copy the two processed CSV files.
5. Reset core tables.
6. Populate towns, flat types and flat models.
7. Populate HDB blocks.
8. Populate resale transactions.
9. Create the analytics view.
10. Validate row counts and commit the transaction.

## 9. Expected validation results

| Check | Expected value |
|---|---:|
| Staging resale rows | 240,807 |
| Staging property rows | 13,357 |
| Core resale transactions | 240,807 |
| Core HDB blocks | 13,358 |
| Analytics rows | 240,807 |
| Blocks without property details | 1 |

A mismatch between staging transactions, core transactions and analytics rows causes the loader to fail instead of silently committing incomplete data.

## 10. Running the project

```bash
source .venv/bin/activate
docker compose up -d
python -m src.run_preprocessing
python -m src.ingestion.load_to_postgres
```

The loader writes `data/processed/database_load_report.json`. In DBeaver, refresh the connection and expand `Schemas` to inspect `staging`, `core` and `analytics`.

## 11. Team analysis rule

After database loading, Python or R must use PostgreSQL as the only analytical data channel. Analysis code should query `analytics.resale_enriched`; it should not read the raw or processed CSV files directly.
