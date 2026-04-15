from datetime import date as DateType
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    date: DateType


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0)
    type: TransactionType | None = None
    category: str | None = Field(None, min_length=1, max_length=100)
    date: DateType | None = None


class Transaction(TransactionBase):
    id: UUID = Field(default_factory=uuid4)

    model_config = ConfigDict(from_attributes=True)


class FinanceSummary(BaseModel):
    income: Decimal
    expense: Decimal
    balance: Decimal
