"""OCR adapter. EasyOCR is optional; fallback is explicit DEMO mode."""
class PlateOCR:
    def __init__(self):
        self.reader = None
        try:
            import easyocr
            self.reader = easyocr.Reader(["en"], gpu=False)
        except Exception:
            pass

    def read(self, crop):
        if self.reader is None:
            return {"plate": None, "confidence": 0.0, "mode": "DEMO"}
        results = self.reader.readtext(crop)
        if not results:
            return {"plate": None, "confidence": 0.0, "mode": "OCR"}
        text, confidence = max(((r[1], float(r[2])) for r in results), key=lambda x: x[1])
        return {"plate": text.upper().replace(" ", ""), "confidence": confidence, "mode": "OCR"}

def read_plate(crop):
    return PlateOCR().read(crop)
