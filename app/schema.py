import re
import time
from dataclasses import dataclass

import psycopg

from app.config import settings

COLUMNS_SQL = """
SELECT table_name, column_name, data_type, is_nullable, ordinal_position
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position
"""

PRIMARY_KEYS_SQL = """
SELECT tc.table_name, kcu.column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'PRIMARY KEY'
ORDER BY tc.table_name, kcu.ordinal_position
"""

FOREIGN_KEYS_SQL = """
SELECT
  kcu.table_name AS source_table,
  kcu.column_name AS source_column,
  ccu.table_name AS target_table
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON tc.constraint_name = ccu.constraint_name
 AND tc.table_schema = ccu.table_schema
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY kcu.table_name, kcu.ordinal_position
"""

CHECK_CONSTRAINTS_SQL = """
SELECT
  conrelid::regclass::text AS table_name,
  pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE contype = 'c'
  AND connamespace = 'public'::regnamespace
"""

# Matches CHECK ((column = ANY (ARRAY['a'::text, 'b'::text, ...]))) style
# constraints, which is how Postgres normalizes a `column IN (...)` check.
_ENUM_CHECK_RE = re.compile(
    r"\(?\s*(\w+)\s*=\s*ANY\s*\(\s*ARRAY\[(.*?)\]", re.IGNORECASE
)


@dataclass
class _SchemaCache:
    expires_at: float
    context: str


_cache: _SchemaCache | None = None


def get_schema_context() -> str:
    """Return compact schema text for LLM prompts, cached for SCHEMA_CACHE_TTL_SEC."""
    global _cache

    now = time.monotonic()
    if _cache is not None and now < _cache.expires_at:
        return _cache.context

    context = _load_schema_context()
    _cache = _SchemaCache(
        expires_at=now + settings.schema_cache_ttl_sec,
        context=context,
    )
    return context


def _load_schema_context() -> str:
    with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(COLUMNS_SQL)
            columns = cur.fetchall()
            cur.execute(PRIMARY_KEYS_SQL)
            primary_keys = cur.fetchall()
            cur.execute(FOREIGN_KEYS_SQL)
            foreign_keys = cur.fetchall()
            cur.execute(CHECK_CONSTRAINTS_SQL)
            check_constraints = cur.fetchall()

    enum_values = _parse_enum_checks(check_constraints)
    return _format_schema(columns, primary_keys, foreign_keys, enum_values)


def _parse_enum_checks(
    check_constraints: list[tuple],
) -> dict[tuple[str, str], list[str]]:
    """
    Extract allowed values from `column IN (...)` style CHECK constraints
    (Postgres normalizes these to `column = ANY (ARRAY[...])`).
    Returns {(table_name, column_name): [value, ...]}.
    """
    enum_values: dict[tuple[str, str], list[str]] = {}
    for table_name, definition in check_constraints:
        match = _ENUM_CHECK_RE.search(definition)
        if not match:
            continue
        column_name, array_body = match.groups()
        values = re.findall(r"'([^']*)'", array_body)
        if values:
            enum_values[(table_name, column_name)] = values
    return enum_values


def _format_schema(
    columns: list[tuple],
    primary_keys: list[tuple],
    foreign_keys: list[tuple],
    enum_values: dict[tuple[str, str], list[str]],
) -> str:
    pk_by_table: dict[str, set[str]] = {}
    for table_name, column_name in primary_keys:
        pk_by_table.setdefault(table_name, set()).add(column_name)

    fk_by_table: dict[str, dict[str, str]] = {}
    for source_table, source_column, target_table in foreign_keys:
        fk_by_table.setdefault(source_table, {})[source_column] = target_table

    tables: dict[str, list[str]] = {}
    for table_name, column_name, data_type, is_nullable, _ordinal in columns:
        parts = [column_name, data_type.upper()]
        if column_name in pk_by_table.get(table_name, set()):
            parts.append("PK")
        if source_col := fk_by_table.get(table_name, {}).get(column_name):
            parts.append(f"FK->{source_col}")
        if is_nullable == "NO":
            parts.append("NOT NULL")
        if values := enum_values.get((table_name, column_name)):
            parts.append(f"VALUES[{','.join(values)}]")
        tables.setdefault(table_name, []).append(" ".join(parts))

    lines = [
        f"{table_name}({', '.join(col_defs)})"
        for table_name, col_defs in sorted(tables.items())
    ]
    return "\n".join(lines)
