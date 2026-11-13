from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    username: str
    message: str
    timestamp: datetime