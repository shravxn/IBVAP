class SimpleTracker:
    """Minimal stable-ID placeholder; replace with ByteTrack/DeepSORT when required."""
    def __init__(self): self.next_id=1
    def update(self, detections):
        return [{**d, 'track_id': d.get('track_id', str(self.next_id))} for d in detections]
