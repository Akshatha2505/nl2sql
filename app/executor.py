import decimal
from datetime import date, datetime
from typing import Any

import psycopg
import psycopg.rows

from app.config import settings


class ExecutionError(RuntimeError):
    """Raised when the SELECT query fails at the database level."""


def execute(sql: str) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Run sql inside a read-only transaction.
    Returns (columns, rows) where every value is JSON-serializable.
    Raises ExecutionError on any DB-level failure.
    """
    try:
        with psycopg.connect(
            settings.database_url,
            connect_timeout=5,
            row_factory=psycopg.rows.dict_row,
        ) as conn:
            conn.execute("SET TRANSACTION READ ONLY")
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    prepare=False,
                )
                raw_rows = cur.fetchmany(settings.query_max_rows)
                columns = [desc.name for desc in cur.description] if cur.description else []

    except psycopg.Error as exc:
        raise ExecutionError(str(exc)) from exc

    rows = [_serialize_row(row) for row in raw_rows]
    return columns, rows


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert DB types that are not JSON-serializable to safe equivalents."""
    return {key: _serialize_value(value) for key, value in row.items()}


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (bytes, memoryview)):
        return None
    return value
