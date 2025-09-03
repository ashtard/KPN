# Customer RESTful API (FastAPI)
A minimal RESTful API for managing customers, built with FastAPI, SQLAlchemy, and SQLite.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open docs: http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc

## Endpoints
- `GET /health` → service status.
- `POST /customers/` → create customer (201).
- `GET /customers/` → list customers with optional `query`, `phone`, `limit`, `offset`. Pagination returned via headers `X-Total-Count`, `X-Limit`, `X-Offset`.
- `GET /customers/{id}` → retrieve one.
- `PATCH /customers/{id}` → update (partial).
- `DELETE /customers/{id}` → delete.

### Request examples
```bash
# Create
curl -X POST http://localhost:8000/customers/ \
-H "Content-Type: application/json" \
-d '{"full_name":"Ada Lovelace","email":"ada@example.com","phone":"+31201234567","address":"Koningslaan 1, Amsterdam"}'

# List
curl "http://localhost:8000/customers?limit=10&offset=0"

# Search by query (name/email)
curl "http://localhost:8000/customers?query=ada"

# Search by phone (partial)
curl "http://localhost:8000/customers?phone=1234"

# Retrieve by id
curl http://localhost:8000/customers/1
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

## AI usage log
List any prompts or tools you used to assist during implementation.\n