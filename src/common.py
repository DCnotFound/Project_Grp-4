"""Shared helpers for deterministic dataset preprocessing."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


WHITESPACE = re.compile(r"\s+")


def normalize_text(value: Any) -> str:
    """Return an uppercase, whitespace-normalized string."""
    if value is None:
        return ""
    return WHITESPACE.sub(" ", str(value)).strip().upper()


def address_key(block: Any, street: Any) -> str:
    """Build the shared HDB address key used across the two HDB files."""
    return f"{normalize_text(block)}|{normalize_text(street)}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

