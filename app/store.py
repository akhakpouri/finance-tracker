from decimal import Decimal
from threading import Lock
from uuid import UUID

from app.schemas import FinanceSummary, Transaction, TransactionCreate, TransactionUpdate, TransactionType


class TransactionStore:
    def __init__(self) -> None:
        self._transactions: dict[UUID, Transaction] = {}
        self._lock = Lock()

    def list(self) -> list[Transaction]:
        with self._lock:
            return sorted(self._transactions.values(), key=lambda item: item.date, reverse=True)

    def get(self, transaction_id: UUID) -> Transaction | None:
        with self._lock:
            return self._transactions.get(transaction_id)

    def create(self, payload: TransactionCreate) -> Transaction:
        transaction = Transaction(**payload.model_dump())
        with self._lock:
            self._transactions[transaction.id] = transaction
        return transaction

    def update(self, transaction_id: UUID, payload: TransactionUpdate) -> Transaction | None:
        with self._lock:
            existing = self._transactions.get(transaction_id)
            if existing is None:
                return None
            updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
            self._transactions[transaction_id] = updated
            return updated

    def delete(self, transaction_id: UUID) -> bool:
        with self._lock:
            return self._transactions.pop(transaction_id, None) is not None

    def summary(self) -> FinanceSummary:
        with self._lock:
            income = sum(
                (item.amount for item in self._transactions.values() if item.type == TransactionType.INCOME),
                start=Decimal("0"),
            )
            expense = sum(
                (item.amount for item in self._transactions.values() if item.type == TransactionType.EXPENSE),
                start=Decimal("0"),
            )
        return FinanceSummary(income=income, expense=expense, balance=income - expense)
