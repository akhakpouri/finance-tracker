from dataclasses import dataclass

from src.app.models.base import Base

@dataclass
class User(Base):
    name: str
    email: str
    first_name: str
    last_name: str
    is_active: bool