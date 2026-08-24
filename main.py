from pathlib import Path
import asyncio
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database.db import Base, engine, get_db
from models.models import Camera, Event, Alert, ANPRRecord
from models.schemas import CameraCreate, CameraOut, EventOut
from services.event_service import create_event
from config import settings
from auth.routes import router as auth_router

Base.metadata.create_all(engine)
app = FastAPI(title="IBVAP API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(',')], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)
clients: set[WebSocket] = set()

def broadcast(payload):
    for ws in list(clients):
        asyncio.create_task(ws.send_json(payload))

@app.get('/api/health')
def health(): return {"status":"ok", "ai_mode":"DEMO", "service":"ibvap-backend"}

@app.get('/api/cameras', response_model=list[CameraOut])
def cameras(db: Session=Depends(get_db)): return db.scalars(select(Camera).order_by(Camera.camera_id)).all()

@app.post('/api/cameras', response_model=CameraOut)
def add_camera(payload: CameraCreate, db: Session=Depends(get_db)):
    if db.scalar(select(Camera).where(Camera.camera_id==payload.camera_id)): raise HTTPException(409, 'Camera ID already exists')
    cam=Camera(**payload.model_dump()); db.add(cam); db.commit(); db.refresh(cam); return cam

@app.delete('/api/cameras/{camera_id}')
def delete_camera(camera_id: str, db: Session=Depends(get_db)):
    cam=db.scalar(select(Camera).where(Camera.camera_id==camera_id))
    if not cam: raise HTTPException(404,'Camera not found')
    db.delete(cam); db.commit(); return {"status":"deleted"}

@app.get('/api/events', response_model=list[EventOut])
def events(db: Session=Depends(get_db)): return db.scalars(select(Event).order_by(Event.created_at.desc()).limit(200)).all()

@app.post('/api/events/{event_id}/acknowledge')
def ack(event_id:int, db:Session=Depends(get_db)):
    e=db.get(Event,event_id)
    if not e: raise HTTPException(404,'Event not found')
    e.status='ACKNOWLEDGED'; db.commit(); return {"status":"acknowledged"}

@app.get('/api/alerts')
def alerts(db:Session=Depends(get_db)): return db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(100)).all()

@app.post('/api/alerts/{alert_id}/resolve')
def resolve(alert_id:int, db:Session=Depends(get_db)):
    a=db.get(Alert,alert_id)
    if not a: raise HTTPException(404,'Alert not found')
    a.status='RESOLVED'; db.commit(); return {"status":"resolved"}

@app.get('/api/analytics')
def analytics(db:Session=Depends(get_db)):
    rows=db.execute(select(Event.event_type, func.count(Event.id)).group_by(Event.event_type)).all()
    return {"events_by_type":dict(rows),"total_events":db.scalar(select(func.count(Event.id))) or 0}

@app.post('/api/anpr/process')
def anpr_process(payload:dict, db:Session=Depends(get_db)):
    plate=payload.get('plate','DEMO-PLATE')
    rec=ANPRRecord(plate_number=plate, camera_id=payload.get('camera_id','BOP-03'), vehicle_type=payload.get('vehicle_type','Jeep'), ocr_confidence=float(payload.get('confidence',0.91)), watchlist_status=payload.get('watchlist_status','NORMAL'))
    db.add(rec); db.commit(); db.refresh(rec)
    return {"id":rec.id,"mode":"DEMO","plate":rec.plate_number,"ocr_confidence":rec.ocr_confidence}

@app.post('/api/demo/start')
def demo_start(db:Session=Depends(get_db)):
    cam=db.scalar(select(Camera).where(Camera.camera_id=='BOP-03'))
    if not cam:
        cam=Camera(camera_id='BOP-03',name='BOP-03 Demo Camera',location='Border Road Sector A',status='ONLINE',stream_url='demo://jeep')
        db.add(cam); db.commit(); db.refresh(cam)
    create_event(db,broadcast,event_type='VEHICLE_DETECTED',camera_id='BOP-03',object_type='Jeep',track_id='04',confidence=.92,priority='LOW',reason='Vehicle detected; AI MODE: DEMO')
    create_event(db,broadcast,event_type='ANPR_EVENT',camera_id='BOP-03',object_type='Jeep',track_id='04',confidence=.91,priority='MEDIUM',reason='Plate OCR processed; AI MODE: DEMO')
    create_event(db,broadcast,event_type='INTRUSION',camera_id='BOP-03',object_type='Jeep',track_id='04',confidence=.94,priority='CRITICAL',reason='Vehicle entered configured restricted polygon; AI MODE: DEMO')
    return {"status":"started","camera_id":"BOP-03","ai_mode":"DEMO"}

@app.post('/api/demo/stop')
def demo_stop(): return {"status":"stopped"}

@app.get('/api/video/stream')
def video_stream():
    videos=list(Path('videos').glob('*.mp4'))+list(Path('videos').glob('*.avi'))
    if not videos: raise HTTPException(404,'Put an MP4/AVI file in videos/ first')
    from ai.video_processor import VideoProcessor
    def gen():
        for frame in VideoProcessor(str(videos[0])).frames():
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+frame+b'\r\n'
    return StreamingResponse(gen(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.websocket('/ws/events')
async def ws_events(ws:WebSocket):
    await ws.accept(); clients.add(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: clients.discard(ws)
