#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from sqlalchemy import UniqueConstraint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base
from app.db.session import init_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export the current SQLAlchemy schema to a Mermaid ER diagram. "
            "Optionally render it to an image when Mermaid CLI is installed."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/db_schema.mmd"),
        help="Path to the Mermaid output file.",
    )
    parser.add_argument(
        "--image",
        choices=["png", "svg", "jpg", "jpeg"],
        default=None,
        help="Optional image format to render with Mermaid CLI (mmdc).",
    )
    parser.add_argument(
        "--image-output",
        type=Path,
        default=None,
        help="Optional explicit path for the rendered image.",
    )
    return parser.parse_args()


def collect_table_unique_columns(table) -> set[str]:
    unique_columns = {
        column.name
        for column in table.columns
        if column.unique
    }
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint) and len(constraint.columns) == 1:
            unique_columns.update(column.name for column in constraint.columns)
    return unique_columns


def mermaid_type(column) -> str:
    python_type = getattr(column.type, "python_type", None)
    if python_type is int:
        return "int"
    if python_type is float:
        return "float"
    if python_type is bool:
        return "boolean"
    if python_type is dict:
        return "json"
    if python_type is list:
        return "json"
    return "string"


def build_mermaid() -> str:
    init_db()

    lines = [
        "---",
        "title: Apartment Price Service Database Schema",
        "---",
        "erDiagram",
    ]

    sorted_tables = sorted(Base.metadata.tables.values(), key=lambda table: table.name)

    for table in sorted_tables:
        unique_columns = collect_table_unique_columns(table)
        lines.append(f"    {table.name.upper()} {{")
        for column in table.columns:
            markers: list[str] = []
            if column.primary_key:
                markers.append("PK")
            if column.foreign_keys:
                markers.append("FK")
            if column.name in unique_columns and not column.primary_key:
                markers.append("UK")
            if not column.nullable:
                markers.append("NOT NULL")

            marker_text = f' "{", ".join(markers)}"' if markers else ""
            lines.append(
                f"        {mermaid_type(column)} {column.name}{marker_text}"
            )
        lines.append("    }")

    lines.append("")

    for table in sorted_tables:
        for column in table.columns:
            for foreign_key in column.foreign_keys:
                source = table.name.upper()
                target = foreign_key.column.table.name.upper()
                relation = "||--||" if column.unique else "}o--||"
                label = column.name
                lines.append(f"    {target} {relation} {source} : \"{label}\"")

    return "\n".join(lines) + "\n"


def render_image(source_path: Path, image_path: Path) -> None:
    mermaid_cli = shutil.which("mmdc")
    if mermaid_cli is None:
        raise RuntimeError(
            "Mermaid CLI (mmdc) is not installed. "
            "Install it first, for example: npm install -g @mermaid-js/mermaid-cli"
        )

    subprocess.run(
        [mermaid_cli, "-i", str(source_path), "-o", str(image_path)],
        check=True,
    )


def main() -> None:
    args = parse_args()
    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_mermaid(), encoding="utf-8")
    print(f"Mermaid schema exported to: {output_path}")

    if args.image:
        suffix = ".jpg" if args.image == "jpeg" else f".{args.image}"
        image_path = args.image_output or output_path.with_suffix(suffix)
        render_image(output_path, image_path)
        print(f"Rendered image exported to: {image_path}")


if __name__ == "__main__":
    main()
