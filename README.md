# HDB Resale Database Project

This project investigates the property, location and transaction characteristics associated with Singapore HDB resale prices. It integrates two official data.gov.sg datasets: HDB resale transactions and HDB property information.

## Project structure

- `data/raw`: original source files; do not edit manually
- `data/processed`: reproducible cleaned files and validation reports
- `docs`: project scope, data documentation, database design and ER diagram
- `sql`: staging tables, normalized schema, transformations, views and example queries
- `src`: Python profiling, preprocessing and database-loading programs
- `notebooks`: analysis notebooks that must retrieve data from PostgreSQL
- `presentation`: final presentation material

## Python setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Preprocess the datasets

```bash
python -m src.run_preprocessing
```

Generated outputs:

- `data/processed/hdb_resale_clean.csv`
- `data/processed/hdb_property_clean.csv`
- `data/processed/profile_report.json`
- `data/processed/validation_report.json`

No source transactions are silently deleted. Exact duplicate-looking rows are retained and flagged because the public data does not provide an official transaction identifier.

## Start PostgreSQL and load the database

1. Copy `.env.example` to `.env` and choose a local database password.
2. Start PostgreSQL:

```bash
docker compose up -d
```

3. Load and validate the processed data:

```bash
python -m src.ingestion.load_to_postgres
```

The loader performs a full refresh, builds the `staging`, `core` and `analytics` schemas, checks row counts and writes `data/processed/database_load_report.json`.

Analysis code must query PostgreSQL—normally `analytics.resale_enriched`—instead of reading the CSV files directly. See `docs/database_implementation_guide.md` for the complete explanation.
