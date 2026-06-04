import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

class ModelRegistry:
    def __init__(self, registry_dir: str = "models/registry"):
        self.registry_dir = registry_dir
        os.makedirs(self.registry_dir, exist_ok=True)
        self.metadata_file = os.path.join(self.registry_dir, "metadata.json")
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, "w") as f:
                json.dump({}, f)
                
    def _load_metadata(self) -> Dict[str, Any]:
        with open(self.metadata_file, "r") as f:
            return json.load(f)
            
    def _save_metadata(self, metadata: Dict[str, Any]):
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)

    def save_model(self, model_path: str, version: str, accuracy: float, dataset_version: str) -> str:
        """
        Saves a model to the registry with metadata.
        Returns the new path of the saved model.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        version_dir = os.path.join(self.registry_dir, version)
        os.makedirs(version_dir, exist_ok=True)
        
        new_model_path = os.path.join(version_dir, "best.pt")
        shutil.copy2(model_path, new_model_path)
        
        metadata = self._load_metadata()
        metadata[version] = {
            "version": version,
            "accuracy": accuracy,
            "training_date": datetime.utcnow().isoformat(),
            "dataset_version": dataset_version,
            "model_path": new_model_path
        }
        self._save_metadata(metadata)
        
        return new_model_path

    def load_model(self, version: str) -> Optional[Dict[str, Any]]:
        """
        Loads model metadata for a specific version.
        """
        metadata = self._load_metadata()
        return metadata.get(version)

    def get_latest_model(self) -> Optional[Dict[str, Any]]:
        """
        Returns metadata for the most recently trained model based on training_date.
        """
        metadata = self._load_metadata()
        if not metadata:
            return None
            
        return max(metadata.values(), key=lambda x: x["training_date"])
