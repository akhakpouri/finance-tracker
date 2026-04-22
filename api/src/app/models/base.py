from datetime import datetime
from abc import ABC
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_date: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_date: Mapped[datetime] = mapped_column(default=datetime.now)
