import httpx
import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.executor import ExecutionError
from app.models import QueryRequest, QueryResponse
from app.pipeline import run_query
from app.sql_guard import GuardError

app = FastAPI(title="nl2sql")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"database unavailable: {exc}"
        ) from exc

    return {"status": "ok", "database": "connected"}


@app.get("/health/ollama")
def health_ollama():
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{settings.ollama_host.rstrip('/')}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            names = [model.get("name", "") for model in models]

            if not any(settings.ollama_model in name for name in names):
                raise HTTPException(
                    status_code=503,
                    detail=(
                        f"model {settings.ollama_model!r} not found; "
                        f"available: {names}"
                    ),
                )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"ollama unavailable: {exc}"
        ) from exc

    return {"status": "ok", "ollama": "reachable", "model": settings.ollama_model}


@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest) -> QueryResponse:
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    try:
        return run_query(question)
    except GuardError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ExecutionError as exc:
        raise HTTPException(status_code=503, detail=f"database error: {exc}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"ollama unavailable: {exc}") from exc
