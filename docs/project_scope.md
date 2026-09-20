# Project Scope

## Main research question

What property, location and transaction characteristics are associated with Singapore HDB resale prices and price per square metre?

## Supporting questions

1. How have resale prices changed over time?
2. Which towns have the highest typical resale price and price per square metre?
3. How do flat type, flat model and floor area relate to price?
4. What is the relationship between remaining lease and resale price?
5. Do storey level and building age show meaningful price differences?

## Datasets in scope

- HDB resale transactions from data.gov.sg
- HDB property information from data.gov.sg

The datasets are joined using a normalized key formed from block number and street name.

## Technical constraint

After ingestion, all analysis must retrieve data through PostgreSQL. Python or R analysis must not read the original CSV files directly.
