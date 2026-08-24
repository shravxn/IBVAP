from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "IBVAP"
    database_url: str = "sqlite:///./ibvap.db"
    jwt_secret: str = "change-this-secret"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ibvap
      POSTGRES_USER: ibvap
      POSTGRES_PASSWORD: ibvap
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    environment:
      DATABASE_URL: postgresql+psycopg://ibvap:ibvap@db:5432/ibvap
      JWT_SECRET: change-this-secret
      CORS_ORIGINS: http://localhost:5173
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  pgdata:
EVENTS
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
