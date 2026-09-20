# Data Dictionary

## Clean resale output

`data/processed/hdb_resale_clean.csv` retains the source fields and adds:

| Column | Type | Description |
|---|---|---|
| `source_row_id` | Integer | Reproducible one-based source-row identifier; not a natural transaction key |
| `storey_lower` | Integer | Lower value parsed from `storey_range` |
| `storey_upper` | Integer | Upper value parsed from `storey_range` |
| `storey_midpoint` | Decimal | Midpoint of the published storey range |
| `remaining_lease_years` | Integer | Whole-year component of remaining lease |
| `remaining_lease_extra_months` | Integer | Additional months from 0 to 11 |
| `remaining_lease_months` | Integer | Total remaining lease in months |
| `address_key` | Text | Normalized `block|street_name` join key |
| `possible_duplicate` | Boolean | True for every row in an exact duplicate group |
| `duplicate_group_size` | Integer | Number of identical published rows in that group |

`month` is converted from `YYYY-MM` to the first day of the month (`YYYY-MM-01`). Text identifiers and categories are uppercased and repeated whitespace is removed.

## Clean property output

`data/processed/hdb_property_clean.csv` retains the source fields and adds:

| Column | Type | Description |
|---|---|---|
| `property_row_id` | Integer | Reproducible one-based source-row identifier |
| `address_key` | Text | Normalized `blk_no|street` candidate key |

The six `Y`/`N` facility columns are converted to Boolean values. Counts and years are validated as non-negative integers.

## Main analytical fields

The `analytics.resale_enriched` view combines transaction, category and property information. Important derived fields include:

| Field | Description |
|---|---|
| `price_per_sqm` | Resale price divided by floor area |
| `building_age_at_sale` | Transaction year minus property completion year |
| `remaining_lease_months` | Comparable numeric representation of remaining lease |
| `has_property_record` | Whether the normalized address was found in the property dataset |
