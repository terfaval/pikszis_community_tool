from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str


class UserDB(UserOut):
    password_hash: str
    created_at: datetime | None = None