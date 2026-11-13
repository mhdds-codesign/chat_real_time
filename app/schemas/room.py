from typing import Optional

from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    password: Optional[str] = None

class RoomOut(BaseModel):
    name: str
    private: bool

class RoomInfo(BaseModel):
    name: str
    private: bool
    users: int

class RoomVerify(BaseModel):
    name: str
    password: Optional[str] = None
    username: Optional[str] = None
