# Customer RESTful API (FastAPI)

A minimal RESTful API for managing customers, built with FastAPI, SQLAlchemy, and SQLite.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open docs: http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc

## Endpoints
- `GET /status` → service status.
- `POST /customers/` → create customer (201).
- `GET /customers/` → list customers with optional `query`, `phone`, `limit`, `offset`. Pagination returned via headers `X-Total-Count`, `X-Limit`, `X-Offset`.
- `GET /customers/{id}` → retrieve one.
- `PATCH /customers/{id}` → update (partial).
- `DELETE /customers/{id}` → delete.

## Request examples
```bash
# Create
curl -X POST http://localhost:8000/customers/   -H "Content-Type: application/json"   -d '{"full_name":"Ada Lovelace","email":"ada@example.com","phone":"+31201234567","address":"Koningslaan 1, Amsterdam"}'

# List
curl "http://localhost:8000/customers?limit=10&offset=0"

# Search by query (name/email)
curl "http://localhost:8000/customers?query=ada"

# Search by phone (partial)
curl "http://localhost:8000/customers?phone=1234"

# Retrieve by id
curl http://localhost:8000/customers/1

# --- AI Helpers ---

# Sentiment
curl -X POST http://localhost:8000/ai/sentiment   -H "Content-Type: application/json"   -d '{"text":"Great service, thank you!"}'

# Subject line
curl -X POST http://localhost:8000/ai/subject   -H "Content-Type: application/json"   -d '{"body":"Customer is interested in premium plan; follow up next Tuesday."}'
```

## Data model
`Customer`: `id`, `full_name`, `email` (unique), `phone` (unique, optional), `address`, `created_at`, `updated_at`.

## Error semantics
- 404 if resource not found
- 409 on unique collisions (email/phone)
- 422 on validation errors (FastAPI/Pydantic)

## Testing
```bash
pytest -q
```

## Notes on privacy & future work
- Avoid logging PII; if enabling logging, mask phone/email.
- Future: normalize phone to E.164, add proper auth (API key/JWT), rate limiting, migrations (Alembic), Dockerfile.

## Optional AI Helpers
Two tiny, dependency-free helpers are exposed under `/ai`:
- `POST /ai/sentiment` → `{"text": "..."}` → classifies feedback as `positive|neutral|negative`.
- `POST /ai/subject` → `{"body": "..."}` → suggests a concise email subject line (≤ 70 chars).

These are rule-based and fast; you can later replace them with a model or external API.

## AI usage log
This project was developed with occasional assistance from ChatGPT.  
AI was used in the following ways:

- Debugging Pydantic v2 migration issues (e.g., replacing `Config` with `ConfigDict`).  
- Suggesting fixes for serialization errors (e.g., handling `datetime` fields).  
- Helping polish project structure (e.g., separating `routers`, `crud`, `schemas`, and `util`).  
- Writing clear error responses and consistent `responses={}` metadata in routers.  
- Drafting README structure and usage examples.  
- Adding optional lightweight AI helper endpoints (`/ai/sentiment`, `/ai/subject`) with tests.  

All code was reviewed, tested, and adapted manually before inclusion.
