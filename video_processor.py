"""Optional real-video pipeline. Uses OpenCV and a YOLO adapter when installed."""
from pathlib import Path
import cv2
from .detection.detector import YOLODetector

class VideoProcessor:
    def __init__(self, video_path: str, model_path: str = "models/yolo11n.pt"):
        self.video_path = Path(video_path)
        self.detector = YOLODetector(model_path)

    def frames(self):
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {self.video_path}")
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                detections = self.detector.detect(frame)
                annotated = self.detector.annotate(frame, detections)
                ok, jpg = cv2.imencode(".jpg", annotated)
                if ok:
                    yield jpg.tobytes()
        finally:
            cap.release()
