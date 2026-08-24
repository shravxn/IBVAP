from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CameraCreate(BaseModel):
    camera_id: str
    name: str
    location: str = "Demo Border Sector"
    stream_url: str | None = None
    status: str = "ONLINE"
    fps: float = 25
    resolution: str = "1920x1080"

class CameraOut(CameraCreate):
    id: int
    enabled: bool
    last_heartbeat: datetime
    model_config = ConfigDict(from_attributes=True)

class EventOut(BaseModel):
    id: int
    event_type: str
    camera_id: str
    object_type: str
    track_id: str | None
    confidence: float
    priority: str
    status: str
    reason: str
    evidence_path: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
