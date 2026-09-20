"""Create a reproducible quality profile for the two HDB source datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.common import address_key, write_json


def _csv_profile(path: Path, identifier_columns: dict[str, str] | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = pd.read_csv(path, dtype=identifier_columns or {}, low_memory=False)
    return frame, {
        "file": path.name,
        "rows": len(frame),
        "columns": len(frame.columns),
        "column_names": list(frame.columns),
        "data_types": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "missing_values": {column: int(value) for column, value in frame.isna().sum().items()},
        "exact_duplicate_rows": int(frame.duplicated().sum()),
    }


def build_profile(project_root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    raw_dir = project_root / "data" / "raw"
    output_dir = output_dir or project_root / "data" / "processed"

    resale, resale_profile = _csv_profile(
        raw_dir / "hdb_resale.csv", {"block": "string"}
    )
    property_data, property_profile = _csv_profile(
        raw_dir / "hdb_property.csv", {"blk_no": "string"}
    )

    resale["address_key"] = [
        address_key(block, street)
        for block, street in zip(resale["block"], resale["street_name"])
    ]
    property_data["address_key"] = [
        address_key(block, street)
        for block, street in zip(property_data["blk_no"], property_data["street"])
    ]
    property_keys = set(property_data["address_key"])
    matched = resale["address_key"].isin(property_keys)

    resale_profile.update(
        {
            "month_min": str(resale["month"].min()),
            "month_max": str(resale["month"].max()),
            "unique_addresses": int(resale["address_key"].nunique()),
            "property_matched_rows": int(matched.sum()),
            "property_match_rate": float(matched.mean()),
            "unmatched_rows": int((~matched).sum()),
            "unmatched_address_keys": sorted(resale.loc[~matched, "address_key"].unique()),
        }
    )
    property_profile.update(
        {
            "unique_addresses": int(property_data["address_key"].nunique()),
            "duplicate_address_keys": int(property_data["address_key"].duplicated().sum()),
        }
    )

    profile = {
        "hdb_resale": resale_profile,
        "hdb_property": property_profile,
    }
    write_json(output_dir / "profile_report.json", profile)
    return profile
