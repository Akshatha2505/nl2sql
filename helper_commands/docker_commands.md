# Docker / PostgreSQL helper commands

| Setting | Value |
|---------|-------|
| Database | `nl2sql` |
| User | `db_user` |
| Host port | `5434` |

> **Note:** Run these from any directory. Ensure `docker compose up` is running first.
>
> If you see `bash: exec: -T: invalid option`, you ran a `$COMPOSE ...` command **without setting `COMPOSE` first**. Bash then treats `exec` as the shell builtin, not `docker compose exec`.

## Access DB

**List all tables**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml exec -T db psql -U db_user -d nl2sql -c "\dt"
```

**Interactive psql session** (exit with `\q`)

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml exec db psql -U db_user -d nl2sql
```

## Query data

**All customers**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml exec -T db psql -U db_user -d nl2sql -c "SELECT * FROM customers ORDER BY customer_id;"
```

**Customer count**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml exec -T db psql -U db_user -d nl2sql -c "SELECT COUNT(*) FROM customers;"
```

**Customers: name, city, country only**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml exec -T db psql -U db_user -d nl2sql -c "SELECT full_name, city, country FROM customers ORDER BY customer_id;"
```

## Reset DB

Re-runs `001_schema.sql` then `002_seed.sql` from `db/init/` (only on empty volume).

**Stop containers and delete pgdata volume** (wipes all data)

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml down -v
```

**Start fresh**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml up
```

Detached mode:

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml up -d
```

## Optional shortcut (per terminal session)

Set this once, then use `dc` instead of the long compose path:

```bash
dc() { docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml "$@"; }
dc exec -T db psql -U db_user -d nl2sql -c "\dt"
```

## Full stack (db + nl2sql API)

Uses host Ollama on port `11434` (existing `ollama` container — not managed by this compose file).

**Build and start**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml up --build -d
```

**Health checks** (default API port from `.env`: `8001`)

```bash
curl http://localhost:8001/health
curl http://localhost:8001/health/db
curl http://localhost:8001/health/ollama
```

**Logs**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml logs -f nl2sql
```

**Stop**

```bash
docker compose -f /home/akshatha/Personal/gen_ai/nl2sql/docker-compose.yml down
```

## Ollama (host container)
docker exec ollama ollama pull qwen2.5-coder:7b # install new model

docker exec ollama ollama list # check progress

docker exec ollama ollama rm qwen2.5-coder:7b # removed installed model