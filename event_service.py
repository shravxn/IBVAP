from pathlib import Path
from models.models import Event, Alert

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

def create_event(db, broadcaster, **data):
    event = Event(**data)
    db.add(event); db.commit(); db.refresh(event)
    alert = Alert(event_id=event.id, priority=event.priority,
                  message=f"{event.event_type} detected on {event.camera_id}")
    db.add(alert); db.commit(); db.refresh(alert)
    payload = {"type":"security_event", "event_id":event.id, "event_type":event.event_type,
               "camera_id":event.camera_id, "object_type":event.object_type,
               "track_id":event.track_id, "confidence":event.confidence,
               "priority":event.priority, "reason":event.reason}
    broadcaster(payload)
    return event
