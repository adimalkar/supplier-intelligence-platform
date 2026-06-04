from dataclasses import dataclass
from typing import List, Tuple
import torch
import io
from PIL import Image

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

@dataclass
class Detection:
    class_name: str          # e.g., "scratch", "misalignment", "missing_component"
    confidence: float        # 0.0 - 1.0
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)

class DefectDetector:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        
    def load_model(self):
        if YOLO is None:
            raise ImportError("ultralytics is not installed. Please install the cv dependencies.")
        # Load a pretrained YOLO model (recommended for training)
        self.model = YOLO(self.model_path)

    def detect(self, image_bytes: bytes) -> List[Detection]:
        if self.model is None:
            self.load_model()
        
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid image format: {e}")

        results = self.model.predict(source=image, verbose=False)
        detections = []
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls_idx = int(box.cls[0])
                class_name = self.model.names[cls_idx]
                detections.append(Detection(class_name=class_name, confidence=conf, bbox=(x1, y1, x2, y2)))
        return detections

    def detect_batch(self, images: List[bytes]) -> List[List[Detection]]:
        if self.model is None:
            self.load_model()

        batch_images = []
        for image_bytes in images:
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                batch_images.append(img)
            except Exception as e:
                # If an image is invalid, we will append None and handle it
                batch_images.append(None)
                
        valid_indices = [i for i, img in enumerate(batch_images) if img is not None]
        valid_images = [batch_images[i] for i in valid_indices]
        
        batch_detections = [[] for _ in range(len(images))]
        
        if valid_images:
            results = self.model.predict(source=valid_images, verbose=False)
            
            for result_idx, result in enumerate(results):
                original_idx = valid_indices[result_idx]
                boxes = result.boxes
                for i in range(len(boxes)):
                    box = boxes[i]
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_idx = int(box.cls[0])
                    class_name = self.model.names[cls_idx]
                    batch_detections[original_idx].append(Detection(class_name=class_name, confidence=conf, bbox=(x1, y1, x2, y2)))
                    
        return batch_detections
