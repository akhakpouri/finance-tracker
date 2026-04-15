# finance-tracker

Production-style REST API built with FastAPI (Python) for tracking personal finances.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

- `GET /health`
- `GET /api/v1/transactions`
- `POST /api/v1/transactions`
- `GET /api/v1/transactions/{transaction_id}`
- `PATCH /api/v1/transactions/{transaction_id}`
- `DELETE /api/v1/transactions/{transaction_id}`
- `GET /api/v1/transactions/summary/overview`
