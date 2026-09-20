# Dataset preprocessing

The workflow preserves the two original HDB source files and writes reproducible cleaned outputs to `data/processed`.

## Run

```bash
python -m src.run_preprocessing
```

Generated files:

- `hdb_resale_clean.csv`
- `hdb_property_clean.csv`
- `profile_report.json`
- `validation_report.json`

The workflow normalizes join fields, parses analytical fields, validates required values and flags possible duplicate resale records. It does not delete duplicate-looking records because separate transactions may have identical published attributes.
