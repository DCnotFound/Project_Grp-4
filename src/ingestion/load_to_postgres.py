"""Create the database structure and load processed project data into PostgreSQL."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql


PROJECT_SQL_FILES = [
    "sql/schema/02_create_schemas.sql",
    "sql/staging/01_create_staging_tables.sql",
    "sql/schema/03_create_core_tables.sql",
    "sql/schema/04_create_indexes.sql",
]

TRANSFORMATION_SQL_FILES = [
    "sql/transformations/00_reset_core.sql",
    "sql/transformations/01_populate_dimensions.sql",
    "sql/transformations/02_populate_blocks.sql",
    "sql/transformations/03_populate_transactions.sql",
    "sql/views/01_resale_enriched.sql",
]

CSV_LOADS = [
    (
        "hdb_resale_clean.csv",
        "staging",
        "hdb_resale",
        [
            "source_row_id", "month", "town", "flat_type", "block",
            "street_name", "storey_range", "floor_area_sqm", "flat_model",
            "lease_commence_date", "remaining_lease", "resale_price",
            "storey_lower", "storey_upper", "storey_midpoint",
            "remaining_lease_years", "remaining_lease_extra_months",
            "remaining_lease_months", "address_key", "possible_duplicate",
            "duplicate_group_size",
        ],
    ),
    (
        "hdb_property_clean.csv",
        "staging",
        "hdb_property",
        [
            "property_row_id", "blk_no", "street", "max_floor_lvl",
            "year_completed", "residential", "commercial", "market_hawker",
            "miscellaneous", "multistorey_carpark", "precinct_pavilion",
            "bldg_contract_town", "total_dwelling_units", "1room_sold",
            "2room_sold", "3room_sold", "4room_sold", "5room_sold",
            "exec_sold", "multigen_sold", "studio_apartment_sold",
            "1room_rental", "2room_rental", "3room_rental",
            "other_room_rental", "address_key",
        ],
    ),
]


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE settings without adding another dependency."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def connection_parameters() -> dict[str, Any]:
    required = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing database settings: " + ", ".join(missing) +
            ". Copy .env.example to .env and set a local password."
        )
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
    }


def execute_sql_file(connection: psycopg.Connection[Any], path: Path) -> None:
    statement = path.read_text(encoding="utf-8")
    connection.execute(statement, prepare=False)


def copy_csv(
    connection: psycopg.Connection[Any],
    csv_path: Path,
    schema_name: str,
    table_name: str,
    columns: list[str],
) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"Required processed file not found: {csv_path}")

    copy_statement = sql.SQL("COPY {}.{} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)").format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
    )
    with connection.cursor() as cursor:
        with cursor.copy(copy_statement) as copy:
            with csv_path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    copy.write(chunk)


def scalar(connection: psycopg.Connection[Any], query: str) -> int:
    row = connection.execute(query).fetchone()
    if row is None:
        raise RuntimeError(f"Validation query returned no row: {query}")
    return int(row[0])


def validate_database(connection: psycopg.Connection[Any]) -> dict[str, Any]:
    counts = {
        "staging_resale": scalar(connection, "SELECT COUNT(*) FROM staging.hdb_resale"),
        "staging_property": scalar(connection, "SELECT COUNT(*) FROM staging.hdb_property"),
        "core_transactions": scalar(connection, "SELECT COUNT(*) FROM core.resale_transaction"),
        "core_blocks": scalar(connection, "SELECT COUNT(*) FROM core.hdb_block"),
        "analytics_rows": scalar(connection, "SELECT COUNT(*) FROM analytics.resale_enriched"),
        "blocks_without_property": scalar(
            connection, "SELECT COUNT(*) FROM core.hdb_block WHERE NOT has_property_record"
        ),
    }
    if counts["staging_resale"] != counts["core_transactions"]:
        raise RuntimeError("Core transaction count does not match staging")
    if counts["core_transactions"] != counts["analytics_rows"]:
        raise RuntimeError("Analytics view count does not match core transactions")
    return counts


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Project directory containing sql and data/processed",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    load_env_file(project_root / ".env")

    started_at = datetime.now(timezone.utc)
    parameters = connection_parameters()
    processed_dir = project_root / "data" / "processed"

    with psycopg.connect(**parameters) as connection:
        for relative_path in PROJECT_SQL_FILES:
            execute_sql_file(connection, project_root / relative_path)

        connection.execute(
            "TRUNCATE TABLE staging.hdb_resale, staging.hdb_property"
        )
        for filename, schema_name, table_name, columns in CSV_LOADS:
            copy_csv(
                connection,
                processed_dir / filename,
                schema_name,
                table_name,
                columns,
            )

        for relative_path in TRANSFORMATION_SQL_FILES:
            execute_sql_file(connection, project_root / relative_path)

        counts = validate_database(connection)
        completed_at = datetime.now(timezone.utc)
        details = {
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "status": "COMPLETED",
            "counts": counts,
        }
        connection.execute(
            """
            INSERT INTO staging.load_audit (
                started_at, completed_at, status,
                resale_rows, property_rows, details
            ) VALUES (%s, %s, 'COMPLETED', %s, %s, %s::jsonb)
            """,
            (
                started_at,
                completed_at,
                counts["staging_resale"],
                counts["staging_property"],
                json.dumps(details),
            ),
        )

    report_path = processed_dir / "database_load_report.json"
    write_report(report_path, details)
    print("Database load completed")
    for name, value in counts.items():
        print(f"{name}: {value:,}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
