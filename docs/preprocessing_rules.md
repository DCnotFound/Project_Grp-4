# Preprocessing Rules

## General rules

- Preserve source files in `data/raw` without modification.
- Write generated files only to `data/processed`.
- Normalize identifiers and categories to uppercase with surrounding and repeated whitespace removed.
- Stop with an explicit error when required columns or formats are missing.
- Record profile and validation counts in JSON reports.

## HDB resale transactions

- Parse `month` as the first day of its month in ISO format.
- Keep `block` as text because block identifiers may contain letters.
- Create `address_key` from normalized block and street values.
- Parse `storey_range` into lower, upper and midpoint storeys.
- Parse `remaining_lease` into years, extra months and total months.
- Require positive floor area and resale price values.
- Preserve exact duplicate-looking rows because the source has no transaction identifier.
- Add `possible_duplicate` and `duplicate_group_size` rather than deleting those rows.
- Add `source_row_id` for reproducible traceability.

## HDB property information

- Create `address_key` with the same normalization used for resale records.
- Convert `Y` and `N` facility fields to Boolean values.
- Convert counts and years to integers and reject missing or negative values.
- Require one property record per normalized address key.

## Matching policy

Property attributes are joined by exact normalized `address_key`. The single resale-only address is retained as a core HDB block with null property attributes, allowing all transactions to preserve a valid foreign-key relationship.
