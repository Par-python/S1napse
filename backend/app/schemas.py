from pydantic import BaseModel

class SessionCreate(BaseModel):
    driver_name: str
    car: str
    track: str
    duration: float
