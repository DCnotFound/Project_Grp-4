"""Clean the HDB resale and property CSV files without changing the raw files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.common import address_key, normalize_text


RESALE_TEXT_COLUMNS = [
    "town",
    "flat_type",
    "block",
    "street_name",
    "storey_range",
    "flat_model",
    "remaining_lease",
]

PROPERTY_FLAG_COLUMNS = [
    "residential",
    "commercial",
    "market_hawker",
    "miscellaneous",
    "multistorey_carpark",
    "precinct_pavilion",
]

PROPERTY_INTEGER_COLUMNS = [
    "max_floor_lvl",
    "year_completed",
    "total_dwelling_units",
    "1room_sold",
    "2room_sold",
    "3room_sold",
    "4room_sold",
    "5room_sold",
    "exec_sold",
    "multigen_sold",
    "studio_apartment_sold",
    "1room_rental",
    "2room_rental",
    "3room_rental",
    "other_room_rental",
]


def _require_columns(frame: pd.DataFrame, required: list[str], dataset: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{dataset} is missing required columns: {missing}")


def _normalize_series(series: pd.Series) -> pd.Series:
    return series.map(normalize_text).astype("string")


def clean_resale(source: Path, destination: Path) -> dict[str, Any]:
    raw = pd.read_csv(source, dtype={"block": "string"}, low_memory=False)
    required = [
        "month",
        "town",
        "flat_type",
        "block",
        "street_name",
        "storey_range",
        "floor_area_sqm",
        "flat_model",
        "lease_commence_date",
        "remaining_lease",
        "resale_price",
    ]
    _require_columns(raw, required, "HDB resale data")

    cleaned = raw.copy()
    duplicate_mask = raw.duplicated(keep=False)
    duplicate_sizes = raw.groupby(required, dropna=False)["month"].transform("size")

    for column in RESALE_TEXT_COLUMNS:
        cleaned[column] = _normalize_series(cleaned[column])

    parsed_month = pd.to_datetime(cleaned["month"], format="%Y-%m", errors="coerce")
    if parsed_month.isna().any():
        examples = cleaned.loc[parsed_month.isna(), "month"].head(5).tolist()
        raise ValueError(f"Invalid resale month values: {examples}")
    cleaned["month"] = parsed_month.dt.strftime("%Y-%m-%d")

    for column in ["floor_area_sqm", "resale_price"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        if cleaned[column].isna().any() or (cleaned[column] <= 0).any():
            raise ValueError(f"{column} contains missing, non-numeric, or non-positive values")

    cleaned["lease_commence_date"] = pd.to_numeric(
        cleaned["lease_commence_date"], errors="coerce"
    ).astype("Int64")
    if cleaned["lease_commence_date"].isna().any():
        raise ValueError("lease_commence_date contains invalid values")

    storeys = cleaned["storey_range"].str.extract(
        r"^(?P<storey_lower>\d{2}) TO (?P<storey_upper>\d{2})$"
    )
    if storeys.isna().any(axis=None):
        examples = cleaned.loc[storeys.isna().any(axis=1), "storey_range"].head(5).tolist()
        raise ValueError(f"Unrecognized storey ranges: {examples}")
    cleaned["storey_lower"] = storeys["storey_lower"].astype("int64")
    cleaned["storey_upper"] = storeys["storey_upper"].astype("int64")
    cleaned["storey_midpoint"] = (
        cleaned["storey_lower"] + cleaned["storey_upper"]
    ) / 2

    leases = cleaned["remaining_lease"].str.extract(
        r"^(?P<lease_years>\d+) YEARS?(?: (?P<lease_months>\d{1,2}) MONTHS?)?$"
    )
    if leases["lease_years"].isna().any():
        examples = cleaned.loc[leases["lease_years"].isna(), "remaining_lease"].head(5).tolist()
        raise ValueError(f"Unrecognized remaining-lease values: {examples}")
    cleaned["remaining_lease_years"] = leases["lease_years"].astype("int64")
    cleaned["remaining_lease_extra_months"] = (
        leases["lease_months"].fillna("0").astype("int64")
    )
    if (cleaned["remaining_lease_extra_months"] > 11).any():
        raise ValueError("Remaining-lease month component exceeds 11")
    cleaned["remaining_lease_months"] = (
        cleaned["remaining_lease_years"] * 12
        + cleaned["remaining_lease_extra_months"]
    )

    cleaned["address_key"] = [
        address_key(block, street)
        for block, street in zip(cleaned["block"], cleaned["street_name"])
    ]
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["possible_duplicate"] = duplicate_mask
    cleaned["duplicate_group_size"] = duplicate_sizes.astype("int64")

    destination.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(destination, index=False)

    return {
        "source_rows": len(raw),
        "output_rows": len(cleaned),
        "exact_duplicate_rows_flagged": int(duplicate_mask.sum()),
        "rows_removed": 0,
        "unique_addresses": int(cleaned["address_key"].nunique()),
        "month_min": cleaned["month"].min(),
        "month_max": cleaned["month"].max(),
    }


def clean_property(source: Path, destination: Path) -> dict[str, Any]:
    raw = pd.read_csv(source, dtype={"blk_no": "string"}, low_memory=False)
    required = [
        "blk_no",
        "street",
        *PROPERTY_FLAG_COLUMNS,
        "bldg_contract_town",
        *PROPERTY_INTEGER_COLUMNS,
    ]
    _require_columns(raw, required, "HDB property data")

    cleaned = raw.copy()
    for column in ["blk_no", "street", "bldg_contract_town"]:
        cleaned[column] = _normalize_series(cleaned[column])

    for column in PROPERTY_FLAG_COLUMNS:
        normalized = _normalize_series(cleaned[column])
        unexpected = sorted(set(normalized.dropna()) - {"Y", "N"})
        if unexpected:
            raise ValueError(f"Unexpected values in {column}: {unexpected}")
        cleaned[column] = normalized.map({"Y": True, "N": False}).astype("boolean")

    for column in PROPERTY_INTEGER_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").astype("Int64")
        if cleaned[column].isna().any() or (cleaned[column] < 0).any():
            raise ValueError(f"{column} contains missing, invalid, or negative values")

    cleaned["address_key"] = [
        address_key(block, street)
        for block, street in zip(cleaned["blk_no"], cleaned["street"])
    ]
    if cleaned["address_key"].duplicated().any():
        examples = cleaned.loc[
            cleaned["address_key"].duplicated(keep=False), "address_key"
        ].head(5).tolist()
        raise ValueError(f"Duplicate HDB property address keys: {examples}")

    cleaned.insert(0, "property_row_id", range(1, len(cleaned) + 1))
    destination.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(destination, index=False)

    return {
        "source_rows": len(raw),
        "output_rows": len(cleaned),
        "rows_removed": 0,
        "unique_addresses": int(cleaned["address_key"].nunique()),
        "duplicate_address_keys": 0,
    }


def preprocess_hdb(raw_dir: Path, output_dir: Path) -> dict[str, Any]:
    resale_report = clean_resale(
        raw_dir / "hdb_resale.csv", output_dir / "hdb_resale_clean.csv"
    )
    property_report = clean_property(
        raw_dir / "hdb_property.csv", output_dir / "hdb_property_clean.csv"
    )

    resale_keys = set(
        pd.read_csv(output_dir / "hdb_resale_clean.csv", usecols=["address_key"])[
            "address_key"
        ]
    )
    property_keys = set(
        pd.read_csv(output_dir / "hdb_property_clean.csv", usecols=["address_key"])[
            "address_key"
        ]
    )
    missing_keys = sorted(resale_keys - property_keys)
    resale_report["unmatched_unique_property_addresses"] = len(missing_keys)
    resale_report["unmatched_address_keys"] = missing_keys

    return {"hdb_resale": resale_report, "hdb_property": property_report}

