import cv2
import numpy as np
from src.edge_simulator.config import get_supplier_profile
from src.edge_simulator.generators.image import InspectionImageGenerator

def test_image_generation():
    profile = get_supplier_profile("PREC_MOTORS")
    pl = profile.product_lines[0]
    eq = pl.equipment[0]
    
    generator = InspectionImageGenerator(profile, pl, eq)
    data = generator.generate()
    
    assert data["supplier_code"] == "PREC_MOTORS"
    assert data["equipment_code"] == eq.equipment_code
    assert data["image_format"] == "jpeg"
    assert "image_data" in data
    
    img_array = np.frombuffer(data["image_data"], dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    assert img.shape == (256, 256, 3)

def test_defect_presence():
    profile = get_supplier_profile("PREC_MOTORS")
    pl = profile.product_lines[0]
    eq = pl.equipment[0]
    
    generator = InspectionImageGenerator(profile, pl, eq)
    
    normal_data = generator.generate()
    normal_img = cv2.imdecode(np.frombuffer(normal_data["image_data"], dtype=np.uint8), cv2.IMREAD_COLOR)
    
    defect_data = generator.generate(defect_type="scratch")
    defect_img = cv2.imdecode(np.frombuffer(defect_data["image_data"], dtype=np.uint8), cv2.IMREAD_COLOR)
    
    assert not np.array_equal(normal_img, defect_img)
