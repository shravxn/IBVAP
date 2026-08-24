# IBVAP — Intelligent Border Video Analytics Platform

A modular, software-defined AI surveillance research/demo prototype.

## Core flow
`Video → Detection → Tracking → Virtual Fence → Alert → Evidence → Dashboard → Event Log`

This prototype follows the supplied specification: React + TypeScript + Tailwind frontend, Python + FastAPI + WebSocket backend, OpenCV/YOLO/OCR-ready AI modules, SQLite locally with a PostgreSQL-compatible database layer, evidence storage, demo mode, event history, camera health and role-based authentication.

## Project structure
```text
ibvap/
├── frontend/              # React + TypeScript + Tailwind dashboard
├── backend/               # FastAPI REST + WebSocket + DB
├── ai/                    # Detection/tracking/ANPR/face/behaviour modules
├── videos/                # Put demo CCTV videos here
├── evidence/              # Event snapshots/clips
├── models/                # Optional YOLO/OCR model weights
├── docker-compose.yml
└── .env.example
```

## Run backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The dashboard uses `http://localhost:8000` by default.

## Demo
The dashboard can start/stop a simulated CCTV feed and create deterministic demo events. Real YOLO inference is optional; the backend marks simulated events as `AI MODE: DEMO` so fake results are never presented as real inference.

To use a real video, place an MP4 in `videos/` and connect it through the demo/camera layer. For YOLO, install the optional packages and place model weights under `models/`.

## Environment
Copy `.env.example` to `.env` and change secrets before deployment.

## API
- `GET /api/health`
- `GET /api/cameras`
- `POST /api/cameras`
- `GET /api/events`
- `POST /api/events/{id}/acknowledge`
- `GET /api/alerts`
- `POST /api/alerts/{id}/resolve`
- `GET /api/analytics`
- `POST /api/anpr/process`
- `POST /api/demo/start`
- `POST /api/demo/stop`
- `WS /ws/events`

## Security
JWT authentication, password hashing, role checks, environment variables and API validation are included in the scaffold. Replace demo credentials and secret keys before any real deployment.

## Important
This is a security surveillance research/demo prototype, not an autonomous law-enforcement decision system. Advanced capabilities must be clearly labeled as demo simulation when real inference dependencies/models are unavailable.


## Demo login
- ADMIN: `admin` / `admin123`
- OPERATOR: `operator` / `operator123`
- ANALYST: `analyst` / `analyst123`

Change these demo credentials before any deployment.

## Real MP4 video
Put a `.mp4` or `.avi` file in `videos/`. The backend exposes `GET /api/video/stream` as an MJPEG stream. If `ultralytics` and a model file are available, frames are passed through YOLO before being displayed. Otherwise the UI explicitly remains in DEMO mode.

## Real ANPR
The OCR adapter supports EasyOCR when installed. Plate detection/cropping should be connected to the vehicle detector output before treating OCR output as production inference.
