"""Run profiling and preprocessing for the two HDB project datasets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# When this file is launched directly (for example with VS Code's Run button),
# Python adds src/ rather than the project root to sys.path. Add the project
# root so the src package can still be imported. Module execution with
# `python -m src.run_preprocessing` does not need this fallback.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import write_json
from src.ingestion.preprocess_hdb import preprocess_hdb
from src.profiling.profile_datasets import build_profile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root containing data/raw and data/processed",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory; defaults to PROJECT_ROOT/data/processed",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    raw_dir = project_root / "data" / "raw"
    output_dir = (args.output_dir or project_root / "data" / "processed").resolve()

    profile = build_profile(project_root, output_dir)
    hdb_report = preprocess_hdb(raw_dir, output_dir)

    validation_report = {
        "profile": profile,
        "preprocessing": hdb_report,
    }
    write_json(output_dir / "validation_report.json", validation_report)

    print("Preprocessing completed")
    print(f"Outputs: {output_dir}")
    print(
        "Resale rows: "
        f"{hdb_report['hdb_resale']['output_rows']:,}; "
        f"property rows: {hdb_report['hdb_property']['output_rows']:,}"
    )
    print(f"Unmatched HDB addresses: {hdb_report['hdb_resale']['unmatched_unique_property_addresses']}")


if __name__ == "__main__":
    main()
