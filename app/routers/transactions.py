from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.schemas import FinanceSummary, Transaction, TransactionCreate, TransactionUpdate
from app.store import TransactionStore

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_store() -> TransactionStore:
    from app.main import store

    return store


@router.get("", response_model=list[Transaction])
def list_transactions(transaction_store: TransactionStore = Depends(get_store)) -> list[Transaction]:
    return transaction_store.list()


@router.post("", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    transaction_store: TransactionStore = Depends(get_store),
) -> Transaction:
    return transaction_store.create(payload)


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: UUID, transaction_store: TransactionStore = Depends(get_store)) -> Transaction:
    transaction = transaction_store.get(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdate,
    transaction_store: TransactionStore = Depends(get_store),
) -> Transaction:
    transaction = transaction_store.update(transaction_id, payload)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: UUID, transaction_store: TransactionStore = Depends(get_store)) -> Response:
    deleted = transaction_store.delete(transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/summary/overview", response_model=FinanceSummary)
def get_summary(transaction_store: TransactionStore = Depends(get_store)) -> FinanceSummary:
    return transaction_store.summary()
