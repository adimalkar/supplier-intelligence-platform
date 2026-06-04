"""Image Generator."""
import time
import cv2
import numpy as np
from typing import Dict, Any, Optional

from src.edge_simulator.config import SupplierProfile, EquipmentProfile, ProductLineProfile

class InspectionImageGenerator:
    """Generates synthetic component images with configurable defects."""

    def __init__(self, profile: SupplierProfile, product_line: ProductLineProfile, equipment: EquipmentProfile):
        """Initialize image generator."""
        self.profile = profile
        self.product_line = product_line
        self.equipment = equipment
        self.width = 256
        self.height = 256
        
    def generate(self, defect_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate one inspection image event."""
        # Create base image (e.g. a component on a background)
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 200 # light gray background
        
        # Draw a "component" in the middle
        center_x, center_y = self.width // 2, self.height // 2
        w, h = 150, 100
        color = (100, 100, 100) # dark gray
        
        if defect_type == "misalignment":
            center_x += np.random.randint(10, 30)
            center_y -= np.random.randint(10, 30)
            
        cv2.rectangle(img, (center_x - w//2, center_y - h//2), (center_x + w//2, center_y + h//2), color, -1)
        
        if defect_type == "discoloration":
            # Add a brownish spot
            spot_x = np.random.randint(center_x - w//4, center_x + w//4)
            spot_y = np.random.randint(center_y - h//4, center_y + h//4)
            cv2.circle(img, (spot_x, spot_y), 20, (50, 100, 150), -1)
            
        elif defect_type == "scratch":
            # Draw a white line
            x1 = np.random.randint(center_x - w//2, center_x)
            y1 = np.random.randint(center_y - h//2, center_y)
            x2 = np.random.randint(center_x, center_x + w//2)
            y2 = np.random.randint(center_y, center_y + h//2)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
        # Encode to JPEG bytes
        success, encoded_image = cv2.imencode('.jpg', img)
        image_bytes = encoded_image.tobytes() if success else b""
        
        return {
            "supplier_code": self.profile.supplier_code,
            "equipment_code": self.equipment.equipment_code,
            "timestamp_ms": int(time.time() * 1000),
            "image_data": image_bytes,
            "image_format": "jpeg",
            "inspection_type": "visual"
        }
