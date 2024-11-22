from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RegisterUserModel(BaseModel):
    full_name: str
    dob: str
    address: str
    phone_number: str


class UpdateUserModel(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

class SearchUserModel(BaseModel):
    user_id: int
    full_name: str
    dob: datetime
    address: str
    phone_number: str