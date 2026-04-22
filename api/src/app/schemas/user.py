from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

class UserPriver(User):
    hashed_password: str