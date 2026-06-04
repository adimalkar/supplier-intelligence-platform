import os
import cv2
import numpy as np
import random
import yaml
from pathlib import Path

def generate_synthetic_dataset(output_dir: str = "data/synthetic", num_images: int = 100):
    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, "images")
    labels_dir = os.path.join(output_dir, "labels")
    
    for split in ['train', 'val']:
        os.makedirs(os.path.join(images_dir, split), exist_ok=True)
        os.makedirs(os.path.join(labels_dir, split), exist_ok=True)
        
    classes = ["scratch", "discoloration", "misalignment"]
    
    for i in range(num_images):
        split = 'train' if random.random() < 0.8 else 'val'
        
        # Base image: grey background
        img = np.ones((256, 256, 3), dtype=np.uint8) * 128
        
        # Component: white square
        cv2.rectangle(img, (64, 64), (192, 192), (255, 255, 255), -1)
        
        labels = []
        
        # Add random defects
        num_defects = random.randint(1, 3)
        for _ in range(num_defects):
            defect_type = random.choice(classes)
            class_id = classes.index(defect_type)
            
            bx1, by1, bx2, by2 = 0, 0, 0, 0
            
            if defect_type == "scratch":
                x1, y1 = random.randint(80, 160), random.randint(80, 160)
                x2, y2 = x1 + random.randint(10, 30), y1 + random.randint(10, 30)
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
                
                bx1, by1 = min(x1, x2)-2, min(y1, y2)-2
                bx2, by2 = max(x1, x2)+2, max(y1, y2)+2
                
            elif defect_type == "discoloration":
                cx, cy = random.randint(80, 170), random.randint(80, 170)
                r = random.randint(10, 20)
                cv2.circle(img, (cx, cy), r, (0, 100, 200), -1)
                
                bx1, by1 = cx - r, cy - r
                bx2, by2 = cx + r, cy + r
                
            elif defect_type == "misalignment":
                x1, y1 = random.randint(64, 150), random.randint(64, 150)
                x2, y2 = x1 + 40, y1 + 40
                cv2.rectangle(img, (x1, y1), (x2, y2), (100, 100, 100), -1)
                
                bx1, by1 = x1, y1
                bx2, by2 = x2, y2
                
            # YOLO format: class_id center_x center_y width height (normalized)
            cx_n = ((bx1 + bx2) / 2) / 256.0
            cy_n = ((by1 + by2) / 2) / 256.0
            w_n = max(1, bx2 - bx1) / 256.0
            h_n = max(1, by2 - by1) / 256.0
            labels.append(f"{class_id} {cx_n:.6f} {cy_n:.6f} {w_n:.6f} {h_n:.6f}")
            
        # Save image and label
        img_name = f"img_{i:04d}.jpg"
        cv2.imwrite(os.path.join(images_dir, split, img_name), img)
        
        with open(os.path.join(labels_dir, split, img_name.replace('.jpg', '.txt')), 'w') as f:
            f.write('\n'.join(labels))
            
    # Write yaml file
    yaml_content = {
        'path': os.path.abspath(output_dir),
        'train': 'images/train',
        'val': 'images/val',
        'names': {i: c for i, c in enumerate(classes)}
    }
    
    with open(os.path.join(output_dir, 'dataset.yaml'), 'w') as f:
        yaml.dump(yaml_content, f)
        
    print(f"Dataset generated at {output_dir}")

if __name__ == "__main__":
    generate_synthetic_dataset("data/synthetic", 100)
