import os
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
from src.cv_module.model_registry import ModelRegistry

def train_model(data_yaml_path: str, epochs: int = 20):
    if YOLO is None:
        raise ImportError("ultralytics is not installed.")
        
    model = YOLO("yolov8n.yaml")  # initialize from scratch

    # Train the model
    # Using more epochs to get > 0.5 mAP on simple synthetic data
    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=256,
        project="runs",
        name="defect_detector",
        exist_ok=True,
        device="cpu",
        verbose=False
    )

    # ultralytics saves to {project}/{name}
    best_model_path = "runs/defect_detector/weights/best.pt"
    if getattr(model.trainer, "save_dir", None):
        best_model_path = os.path.join(model.trainer.save_dir, "weights/best.pt")
    elif not os.path.exists(best_model_path):
        best_model_path = "runs/detect/runs/defect_detector/weights/best.pt"
        if not os.path.exists(best_model_path):
            # Fallback search
            for root, dirs, files in os.walk("runs"):
                if "best.pt" in files:
                    best_model_path = os.path.join(root, "best.pt")
                    break
    
    metrics = model.val()
    accuracy = metrics.box.map50
    
    registry = ModelRegistry("models/registry")
    if os.path.exists("models/registry/metadata.json"):
        import json
        with open("models/registry/metadata.json") as f:
            meta = json.load(f)
            num_existing = len(meta)
    else:
        num_existing = 0
    
    version = f"v1.{num_existing}"
    
    saved_path = registry.save_model(
        model_path=best_model_path,
        version=version,
        accuracy=accuracy,
        dataset_version="synthetic_v1"
    )
    
    print(f"Training complete. Model registered at {saved_path} with mAP50: {accuracy:.4f}")

if __name__ == "__main__":
    train_model("data/synthetic/dataset.yaml", epochs=20)
