from fastapi import FastAPI

from app.routers.transactions import router as transaction_router
from app.store import TransactionStore

store = TransactionStore()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Finance Tracker API",
        description="Production-style REST API for tracking personal finances.",
        version="1.0.0",
    )

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(transaction_router, prefix="/api/v1")
    return app


app = create_app()
