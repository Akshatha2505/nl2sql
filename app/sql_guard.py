import re

import sqlparse

from app.config import settings


class GuardError(ValueError):
    """Raised when generated SQL fails read-only validation."""


_BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|COPY|EXECUTE|CALL)\b",
    re.IGNORECASE,
)

_BLOCKED_CLAUSES = re.compile(
    r"\bSELECT\b.+\bINTO\b|\bFOR\s+(UPDATE|SHARE)\b",
    re.IGNORECASE | re.DOTALL,
)

_LIMIT_RE = re.compile(r"\bLIMIT\s+\d+\b", re.IGNORECASE)


def validate_readonly(sql: str) -> str:
    """
    Validate that sql is a safe read-only SELECT.
    Returns the (possibly LIMIT-injected) SQL on success.
    Raises GuardError on any violation.
    """
    stripped = _strip_comments(sql).strip()

    if not stripped:
        raise GuardError("LLM returned empty SQL.")

    # 1. Multiple statements
    statements = [s for s in sqlparse.split(stripped) if s.strip()]
    if len(statements) > 1:
        raise GuardError("Multiple SQL statements are not allowed.")

    # 2. Must start with SELECT
    first_token = stripped.split()[0].upper()
    if first_token != "SELECT":
        raise GuardError(
            f"Only SELECT queries are allowed. Got: {first_token!r}"
        )

    # 3. Blocked keywords
    match = _BLOCKED_KEYWORDS.search(stripped)
    if match:
        raise GuardError(
            f"Blocked keyword detected: {match.group(0).upper()!r}"
        )

    # 4. SELECT INTO / FOR UPDATE / FOR SHARE
    if _BLOCKED_CLAUSES.search(stripped):
        raise GuardError(
            "SELECT INTO and FOR UPDATE/SHARE clauses are not allowed."
        )

    # 5. Enforce LIMIT cap
    if not _LIMIT_RE.search(stripped):
        stripped = f"{stripped} LIMIT {settings.query_max_rows}"

    return stripped


def _strip_comments(sql: str) -> str:
    """Remove SQL comments (-- line and /* block */) using sqlparse."""
    parsed = sqlparse.parse(sql)
    if not parsed:
        return sql
    tokens = [
        str(t)
        for t in parsed[0].flatten()
        if t.ttype not in (
            sqlparse.tokens.Comment.Single,
            sqlparse.tokens.Comment.Multiline,
        )
    ]
    return "".join(tokens)
