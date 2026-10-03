from app.config import settings

_SYSTEM_TEMPLATE = """\
You are a PostgreSQL expert. Your only job is to write a single valid SELECT statement.

Rules:
- Output ONLY the raw SQL query — no markdown, no explanation, no code fences.
- Use only the tables and columns listed in the schema below. Do not invent names.
- Always include LIMIT {max_rows} unless the question implies a smaller count.
- Use explicit JOIN ... ON ... syntax. Avoid subqueries when a JOIN works.
- Never use INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE, or any DDL/DML.
- End with a semicolon.

Schema:
{schema}
"""

_RETRY_SUFFIX = """\

The previous SQL you generated failed with this error:
  SQL: {sql}
  Error: {error}

Rewrite the query to fix the error. Output only the corrected SQL statement.
"""


def build_messages(schema: str, question: str) -> list[dict]:
    """Build the initial chat message list for a new question."""
    system = _SYSTEM_TEMPLATE.format(
        max_rows=settings.query_max_rows,
        schema=schema,
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]


def build_retry_messages(
    messages: list[dict],
    failed_sql: str,
    error: str,
) -> list[dict]:
    """Append the failed SQL + error to messages so the LLM can self-correct."""
    retry_msg = _RETRY_SUFFIX.format(sql=failed_sql, error=error)
    return messages + [
        {"role": "assistant", "content": failed_sql},
        {"role": "user", "content": retry_msg},
    ]
