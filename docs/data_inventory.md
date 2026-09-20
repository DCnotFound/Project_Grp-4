# Data Inventory

## HDB resale transactions

- File: `data/raw/hdb_resale.csv`
- Source: HDB via data.gov.sg
- Rows: 240,807
- Source columns: 11
- Date range: January 2017 to September 2026 in the supplied snapshot
- Natural transaction key: Not supplied
- Added traceability field: `source_row_id`
- Join fields: `block` and `street_name`, normalized into `address_key`
- Missing values: None in the supplied file
- Exact duplicate rows beyond their first occurrence: 318
- Rows belonging to duplicate groups: 635
- Unique normalized addresses: 9,749
- Rows matched to property information: 240,804 of 240,807 (99.9988%)
- Unmatched address: `82|MACPHERSON LANE`, affecting three transactions

Duplicate-looking transactions are retained because separate sales can share every published attribute and the source does not provide unit numbers or an official transaction identifier.

## HDB property information

- File: `data/raw/hdb_property.csv`
- Source: HDB via data.gov.sg
- Rows: 13,357
- Source columns: 24
- Candidate key: Normalized `blk_no` and `street`, stored as `address_key`
- Missing values: None in the supplied file
- Duplicate normalized address keys: None
- Facility flags: Published as `Y` and `N`, converted to Boolean values

## Relationship between the datasets

```text
hdb_resale.block + hdb_resale.street_name
                    ↓ normalize
                 address_key
                    ↑ normalize
hdb_property.blk_no + hdb_property.street
```

The property file contributes building-level attributes such as completion year, maximum floor, facility flags and dwelling-unit counts. The resale file contributes transaction date, flat characteristics, remaining lease and resale price.
