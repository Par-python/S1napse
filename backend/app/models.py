from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    driver_name: str
    car: str
    track: str
    duration: float
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to telemetry samples
    telemetry_samples: list["TelemetrySample"] = Relationship(back_populates="session")

class TelemetrySample(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="session.id")
    
    # Source and metadata
    source: str  # e.g., "SIM"
    car: str
    track: str
    lap: int
    segment: str
    sector: int
    position_m: float
    
    # Timing data
    lap_time_s: float
    sector_time_s: float
    best_lap_time_s: Optional[float] = None
    best_sector_1_s: Optional[float] = None
    best_sector_2_s: Optional[float] = None
    best_sector_3_s: Optional[float] = None
    
    # Vehicle telemetry
    speed: float  # km/h
    rpm: int
    throttle: float  # percentage
    brake: float  # percentage
    gear: int
    steer: float  # steering input
    
    # Track state
    in_pitlane: bool
    is_curve: bool
    
    # Timestamp
    ts: float  # Unix timestamp
    
    # Relationship back to session
    session: Session = Relationship(back_populates="telemetry_samples")
