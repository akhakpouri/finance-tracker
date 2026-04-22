from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.app.models.base import Base


class User(Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(75), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)