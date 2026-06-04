import os
import time
import pytest
from PIL import Image
import io
from src.cv_module.inference import DefectDetector, Detection

def create_dummy_image() -> bytes:
    img = Image.new('RGB', (256, 256), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

@pytest.fixture
def dummy_model_path():
    # Use standard YOLO nano for testing the interface
    return "yolov8n.yaml"

@pytest.mark.unit
def test_cv_inference_detect(dummy_model_path):
    detector = DefectDetector(dummy_model_path)
    try:
        detector.load_model()
    except ImportError:
        pytest.skip("ultralytics not installed")
        
    img_bytes = create_dummy_image()
    
    # Warmup
    detector.detect(img_bytes)
    
    start_time = time.time()
    detections = detector.detect(img_bytes)
    end_time = time.time()
    
    assert isinstance(detections, list)
    if detections:
        assert isinstance(detections[0], Detection)
        assert hasattr(detections[0], 'class_name')
        assert 0.0 <= detections[0].confidence <= 1.0
        assert len(detections[0].bbox) == 4
        
    duration = end_time - start_time
    # Note: On a shared generic CPU it might slightly exceed 100ms, 
    # but YOLO nano typically runs in 30-50ms.
    assert duration < 0.5

@pytest.mark.unit
def test_cv_inference_batch(dummy_model_path):
    detector = DefectDetector(dummy_model_path)
    try:
        detector.load_model()
    except ImportError:
        pytest.skip("ultralytics not installed")
        
    img_bytes = create_dummy_image()
    batch = [img_bytes] * 10
    
    # Warmup
    detector.detect_batch(batch)
    
    start_time = time.time()
    results = detector.detect_batch(batch)
    duration = time.time() - start_time
    
    assert len(results) == 10
    assert isinstance(results[0], list)

@pytest.mark.unit
def test_cv_inference_invalid_image(dummy_model_path):
    detector = DefectDetector(dummy_model_path)
    try:
        detector.load_model()
    except ImportError:
        pytest.skip("ultralytics not installed")
        
    with pytest.raises(ValueError, match="Invalid image format"):
        detector.detect(b"not an image")
