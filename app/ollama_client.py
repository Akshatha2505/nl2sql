import re

import httpx

from app.config import settings


def ollama_chat(messages: list[dict]) -> str:
    """
    Call Ollama /api/chat with the given messages.
    Returns the assistant reply with markdown fences and extra whitespace stripped.
    """
    url = f"{settings.ollama_host.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
    }

    with httpx.Client(timeout=settings.query_timeout_sec) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()

    raw = response.json()["message"]["content"]
    return _clean(raw)


def _clean(raw: str) -> str:
    """Strip markdown code fences, leading/trailing whitespace, and trailing semicolons."""
    # Remove ```sql ... ``` or ``` ... ``` fences
    cleaned = re.sub(r"```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "")
    return cleaned.strip().rstrip(";").strip()
