# Database Architecture

## Loading model

```text
Raw HDB files
      ↓
Python profiling and preprocessing
      ↓
Clean HDB CSV files
      ↓
staging schema
      ↓
normalized core schema
      ↓
analytics.resale_enriched view
      ↓
SQL and Python analysis
```

The project uses a reproducible full refresh:

1. Keep source files unchanged.
2. Generate validated processed files.
3. Truncate and reload staging tables.
4. Rebuild normalized core tables in one transaction.
5. Validate counts before committing.
6. Query the analytics view.

## Schemas

- `staging`: file-shaped landing tables plus a load audit
- `core`: authoritative normalized tables with keys, constraints and indexes
- `analytics`: a convenient read-only view that joins the core model

The analytics schema is a semantic query layer, not a separate warehouse or compute environment.

## Duplicate and unmatched-address handling

Full-refresh staging prevents repeated runs from appending copies of the same files. Primary and unique constraints protect identifiers. Duplicate-looking sales remain separate transactions and carry warning fields. The resale-only address is added to `core.hdb_block` with `has_property_record = FALSE`, so its transactions are not lost.

## Execution

```bash
docker compose up -d
python -m src.run_preprocessing
python -m src.ingestion.load_to_postgres
```
