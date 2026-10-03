from app.executor import ExecutionError, execute
from app.models import QueryResponse
from app.ollama_client import ollama_chat
from app.prompt import build_messages, build_retry_messages
from app.schema import get_schema_context
from app.sql_guard import GuardError, validate_readonly

MAX_ATTEMPTS = 2


def run_query(question: str) -> QueryResponse:
    """
    Orchestrate the full NL -> SQL -> rows flow.
    Retries once (max 2 attempts total): on a guard or execution failure,
    the error is fed back to the LLM and it is asked to regenerate.
    Raises GuardError or ExecutionError if the second attempt also fails.
    """
    schema = get_schema_context()
    messages = build_messages(schema, question)

    sql = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        raw = ollama_chat(messages)

        try:
            sql = validate_readonly(raw)
            columns, rows = execute(sql)
        except (GuardError, ExecutionError) as exc:
            if attempt == MAX_ATTEMPTS:
                raise
            messages = build_retry_messages(messages, raw, str(exc))
            continue

        return QueryResponse(
            question=question,
            sql=sql,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            attempts=attempt,
        )

    # Unreachable: the loop either returns or raises on the final attempt.
    raise ExecutionError("Query failed after all retry attempts.")
