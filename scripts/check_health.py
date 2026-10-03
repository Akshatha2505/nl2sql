"""Verify db + Ollama connectivity using app settings (no server required)."""

import sys
from pathlib import Path

# Allow `python scripts/check_health.py` from project root without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
import psycopg

from app.config import settings


def check_db() -> None:
    with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    print("db: ok")


def check_ollama() -> None:
    url = f"{settings.ollama_host.rstrip('/')}/api/tags"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        models = response.json().get("models", [])
        names = [m.get("name", "") for m in models]

    if not any(settings.ollama_model in name for name in names):
        print(f"ollama: reachable but model {settings.ollama_model!r} not in {names}")
        sys.exit(1)

    print(f"ollama: ok (model {settings.ollama_model!r} found)")


def main() -> None:
    print(f"DATABASE_URL host: {settings.database_url.split('@')[-1]}")
    print(f"OLLAMA_HOST: {settings.ollama_host}")
    check_db()
    check_ollama()


if __name__ == "__main__":
    main()
