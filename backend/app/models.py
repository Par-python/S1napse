from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    driver_name: str
    car: str
    track: str
    duration: float
    upload_time: datetime = Field(default_factory=datetime.utcnow)
