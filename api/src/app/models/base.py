from dataclasses import dataclass
from datetime import datetime
from abc import ABC

@dataclass
class Base(ABC):
    id: int
    created_date: datetime
    updated_date: datetime
