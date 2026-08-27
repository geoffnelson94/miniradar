from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Type system
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TypeInfo:
    python_type: str
    cpp_type: str
    size: int
    alignment: int


TYPE_MAP: dict[str, TypeInfo] = {
    "uint8": TypeInfo(
        python_type="int",
        cpp_type="std::uint8_t",
        size=1,
        alignment=1,
    ),
    "uint16": TypeInfo(
        python_type="int",
        cpp_type="std::uint16_t",
        size=2,
        alignment=2,
    ),
    "uint32": TypeInfo(
        python_type="int",
        cpp_type="std::uint32_t",
        size=4,
        alignment=4,
    ),
    "uint64": TypeInfo(
        python_type="int",
        cpp_type="std::uint64_t",
        size=8,
        alignment=8,
    ),
    "float32": TypeInfo(
        python_type="float",
        cpp_type="float",
        size=4,
        alignment=4,
    ),
    "float64": TypeInfo(
        python_type="float",
        cpp_type="double",
        size=8,
        alignment=8,
    ),
}


# ---------------------------------------------------------------------------
# Parsing / validation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Field:
    name: str
    type_name: str
    count: int
    units: str
    description: str
    valid_range: tuple[float, float] | None


@dataclass(frozen=True)
class Schema:
    name: str
    namespace: str
    version: str
    description: str
    alignment: int
    fields: list[Field]


def load_schema(path: Path) -> Schema:
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML object must be a mapping")

    schema_data = data.get("schema")
    fields_data = data.get("fields")

    if not isinstance(schema_data, dict):
        raise ValueError(f"{path}: missing 'schema' mapping")

    if not isinstance(fields_data, list):
        raise ValueError(f"{path}: missing 'fields' list")

    name = schema_data.get("name")
    namespace = schema_data.get("namespace", "radar")
    version = str(schema_data.get("version", "1.0"))
    description = str(schema_data.get("description", ""))

    cpp_config = schema_data.get("cpp", {})
    alignment = int(cpp_config.get("alignment", 64))

    if alignment <= 0 or alignment & (alignment - 1):
        raise ValueError(
            f"{path}: C++ alignment must be a positive power of two"
        )

    if not name:
        raise ValueError(f"{path}: schema.name is required")

    fields: list[Field] = []

    for index, raw_field in enumerate(fields_data):
        if not isinstance(raw_field, dict):
            raise ValueError(f"{path}: field {index} must be a mapping")

        field_name = raw_field.get("name")
        type_name = raw_field.get("type")
        count = int(raw_field.get("count", 1))
        units = str(raw_field.get("units", "none"))
        description = str(raw_field.get("description", ""))

        if not field_name:
            raise ValueError(f"{path}: field {index} has no name")

        if type_name not in TYPE_MAP:
            raise ValueError(
                f"{path}: unsupported type '{type_name}' "
                f"for field '{field_name}'"
            )

        if count <= 0:
            raise ValueError(
                f"{path}: count for '{field_name}' must be > 0"
            )

        valid_range_raw = raw_field.get("valid_range")
        valid_range = None

        if valid_range_raw is not None:
            if (
                not isinstance(valid_range_raw, list)
                or len(valid_range_raw) != 2
            ):
                raise ValueError(
                    f"{path}: valid_range for '{field_name}' "
                    "must contain exactly two values"
                )

            valid_range = (
                float(valid_range_raw[0]),
                float(valid_range_raw[1]),
            )

        fields.append(
            Field(
                name=field_name,
                type_name=type_name,
                count=count,
                units=units,
                description=description,
                valid_range=valid_range,
            )
        )

    validate_schema(fields, path)

    return Schema(
        name=name,
        namespace=namespace,
        version=version,
        description=description.strip(),
        alignment=alignment,
        fields=fields,
    )


def validate_schema(fields: list[Field], path: Path) -> None:
    names: set[str] = set()

    for field in fields:
        if field.name in names:
            raise ValueError(
                f"{path}: duplicate field '{field.name}'"
            )

        names.add(field.name)

        if field.valid_range:
            low, high = field.valid_range

            if low > high:
                raise ValueError(
                    f"{path}: invalid range for '{field.name}'"
                )


# ---------------------------------------------------------------------------
# C++ layout calculation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LayoutField:
    field: Field
    offset: int
    size: int
    padding_before: int


def align_up(value: int, alignment: int) -> int:
    return ((value + alignment - 1) // alignment) * alignment


def calculate_cpp_layout(schema: Schema) -> tuple[list[LayoutField], int]:
    offset = 0
    result: list[LayoutField] = []

    for field in schema.fields:
        info = TYPE_MAP[field.type_name]

        field_alignment = info.alignment

        aligned_offset = align_up(offset, field_alignment)
        padding_before = aligned_offset - offset

        field_size = info.size * field.count

        result.append(
            LayoutField(
                field=field,
                offset=aligned_offset,
                size=field_size,
                padding_before=padding_before,
            )
        )

        offset = aligned_offset + field_size

    total_size = align_up(offset, schema.alignment)

    return result, total_size


# ---------------------------------------------------------------------------
# Python generation
# ---------------------------------------------------------------------------

def generate_python(schema: Schema) -> str:
    lines: list[str] = []

    lines.extend(
        [
            '"""GENERATED FILE -- DO NOT EDIT.',
            "",
            f"Source schema: {schema.name}.yaml",
            f"Interface version: {schema.version}",
            '"""',
            "",
            "from dataclasses import dataclass",
            "",
            "",
        ]
    )

    lines.append("@dataclass(frozen=True)")
    lines.append(f"class {schema.name}:")

    if not schema.fields:
        lines.append("    pass")
        return "\n".join(lines) + "\n"

    for field in schema.fields:
        if field.count == 1:
            python_type = TYPE_MAP[field.type_name].python_type
        else:
            python_type = f"tuple[{TYPE_MAP[field.type_name].python_type}, ...]"

        lines.append(
            f"    {field.name}: {python_type}"
        )

    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# C++ generation
# ---------------------------------------------------------------------------

def cpp_member_declaration(field: Field) -> str:
    info = TYPE_MAP[field.type_name]

    if field.count == 1:
        return f"{info.cpp_type} {field.name};"

    return f"{info.cpp_type} {field.name}[{field.count}];"


def generate_cpp(schema: Schema) -> str:
    layout, total_size = calculate_cpp_layout(schema)

    ns = schema.namespace

    lines: list[str] = [
        "// GENERATED FILE -- DO NOT EDIT.",
        "",
        f"// Source schema: {schema.name}.yaml",
        f"// Interface version: {schema.version}",
        "",
        "#pragma once",
        "",
        "#include <cstddef>",
        "#include <cstdint>",
        "#include <type_traits>",
        "",
        f"namespace {ns} {{",
        "",
        f"// {schema.description.replace(chr(10), ' ')}",
        "",
        f"struct alignas({schema.alignment}) {schema.name} {{",
    ]

    previous_end = 0
    padding_index = 0

    for layout_field in layout:
        if layout_field.padding_before > 0:
            lines.extend(
                [
                    "",
                    (
                        f"    std::byte _padding_{padding_index}"
                        f"[{layout_field.padding_before}];"
                    ),
                ]
            )
            padding_index += 1

        lines.append("")
        lines.append(
            f"    {cpp_member_declaration(layout_field.field)}"
            f"  // offset {layout_field.offset}, "
            f"{layout_field.field.units}"
        )

        previous_end = layout_field.offset + layout_field.size

    final_padding = total_size - previous_end

    if final_padding > 0:
        lines.extend(
            [
                "",
                (
                    f"    std::byte _padding_{padding_index}"
                    f"[{final_padding}];"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "};",
            "",
            f"static_assert("
            f"alignof({schema.name}) == {schema.alignment}, "
            f'"unexpected alignment for {schema.name}");',
            "",
            f"static_assert("
            f"sizeof({schema.name}) == {total_size}, "
            f'"unexpected size for {schema.name}");',
        ]
    )

    for layout_field in layout:
        field_name = layout_field.field.name
        lines.append(
            f"static_assert("
            f"offsetof({schema.name}, {field_name}) == "
            f"{layout_field.offset}, "
            f'"unexpected offset for {schema.name}::{field_name}");'
        )

    lines.extend(
        [
            "",
            f"static_assert("
            f"std::is_trivially_copyable_v<{schema.name}>, "
            f'"interface type must be trivially copyable");',
            "",
            f"}} // namespace {ns}",
            "",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def generate_markdown(schema: Schema) -> str:
    layout, total_size = calculate_cpp_layout(schema)

    lines: list[str] = [
        f"# {schema.name}",
        "",
        f"**Version:** {schema.version}",
        "",
        f"**Namespace:** `{schema.namespace}`",
        "",
        f"**C++ alignment:** `{schema.alignment} bytes`",
        "",
        f"**Generated C++ size:** `{total_size} bytes`",
        "",
        schema.description,
        "",
        "## Fields",
        "",
        "| Offset | Field | Type | Count | Size | Units | Description |",
        "|---:|---|---|---:|---:|---|---|",
    ]

    for item in layout:
        info = TYPE_MAP[item.field.type_name]

        lines.append(
            f"| {item.offset} "
            f"| `{item.field.name}` "
            f"| `{item.field.type_name}` "
            f"| {item.field.count} "
            f"| {item.size} "
            f"| {item.field.units} "
            f"| {item.field.description} |"
        )

    lines.extend(
        [
            "",
            "## Memory Layout",
            "",
            f"The generated C++ structure is aligned to "
            f"**{schema.alignment} bytes**.",
            "",
            "Natural field alignment is preserved and explicit padding "
            "is inserted between fields and at the end of the structure "
            "when required.",
            "",
            "The generated C++ header contains `static_assert` checks "
            "for structure size, alignment, and field offsets.",
            "",
            "## Validation",
            "",
        ]
    )

    for field in schema.fields:
        if field.valid_range:
            low, high = field.valid_range
            lines.append(
                f"- `{field.name}`: valid range `{low}` to `{high}`"
            )

    lines.extend(
        [
            "",
            "## Generated Artifacts",
            "",
            f"- `generated/python/{snake_case(schema.name)}.py`",
            f"- `generated/cpp/{snake_case(schema.name)}.hpp`",
            f"- `generated/docs/{snake_case(schema.name)}.md`",
            "",
            "> This file is generated from the YAML schema. "
            "> Do not edit manually.",
            "",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def snake_case(value: str) -> str:
    result = []

    for index, char in enumerate(value):
        if char.isupper() and index > 0:
            result.append("_")

        result.append(char.lower())

    return "".join(result)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_schema(
    schema_path: Path,
    output_root: Path,
) -> None:
    schema = load_schema(schema_path)
    stem = snake_case(schema.name)

    python_path = output_root / "python" / f"{stem}.py"
    cpp_path = output_root / "cpp" / f"{stem}.hpp"
    docs_path = output_root / "docs" / f"{stem}.md"

    write_file(python_path, generate_python(schema))
    write_file(cpp_path, generate_cpp(schema))
    write_file(docs_path, generate_markdown(schema))

    print(f"Generated {schema.name}:")
    print(f"  Python : {python_path}")
    print(f"  C++    : {cpp_path}")
    print(f"  Docs   : {docs_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Python, C++, and Markdown artifacts "
            "from radar message YAML schemas."
        )
    )

    parser.add_argument(
        "schemas",
        nargs="*",
        type=Path,
        help="Specific YAML schema files to process.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate artifacts for every YAML schema under schemas/.",
    )

    parser.add_argument(
        "--schema-root",
        type=Path,
        default=Path("schemas"),
        help="Root directory containing schemas (default: schemas).",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("generated"),
        help="Output directory (default: generated).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.all and args.schemas:
        raise ValueError(
            "Do not specify individual schemas together with --all."
        )

    if args.all:
        schema_paths = sorted(args.schema_root.rglob("*.yaml"))
    else:
        schema_paths = args.schemas

    if not schema_paths:
        raise ValueError(
            "Specify one or more schema files, or use --all."
        )

    # Normalize and deduplicate paths while preserving order.
    unique_paths: list[Path] = []
    seen: set[Path] = set()

    for path in schema_paths:
        path = path.resolve()

        if path in seen:
            continue

        seen.add(path)
        unique_paths.append(path)

    for schema_path in unique_paths:
        if not schema_path.exists():
            raise FileNotFoundError(
                f"Schema file does not exist: {schema_path}"
            )

        if schema_path.suffix.lower() not in {".yaml", ".yml"}:
            raise ValueError(
                f"Unsupported schema format: {schema_path}"
            )

        generate_schema(schema_path, args.output)

if __name__ == "__main__":
    main()