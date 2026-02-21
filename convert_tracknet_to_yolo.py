#!/usr/bin/env python3
"""
Convert TrackNet tennis ball dataset to YOLO format.
Creates normalized bounding boxes from ball center coordinates.
"""

import os
import csv
import shutil
from pathlib import Path

# Install kagglehub if needed: pip install kagglehub
import kagglehub

# Download TrackNet dataset from Kaggle
# https://www.kaggle.com/datasets/sofuskonglevoll/tracknet-tennis
# Uses cached version if already downloaded (no re-download)
DATASET_DIR = Path(kagglehub.dataset_download("sofuskonglevoll/tracknet-tennis"))

# Output directory (current directory)
OUTPUT_DIR = Path(__file__).parent / "data" / "tennis_yolo"

# YOLO class: 0 = ball
CLASS_ID = 0

# Known image dimensions from TrackNet dataset (1280x720)
IMG_WIDTH = 1280
IMG_HEIGHT = 720

# Ball bounding box size (in pixels)
BALL_WIDTH = 20
BALL_HEIGHT = 20

def convert_tracknet_to_yolo(csv_path, images_dir, output_images_dir, output_labels_dir, prefix):
    """Convert a single TrackNet Label.csv to YOLO format."""
    converted_count = 0
    
    img_width = IMG_WIDTH
    img_height = IMG_HEIGHT
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row['file name']
            visibility = int(row['visibility'])
            
            # Skip frames where ball is not visible
            if visibility != 1:
                continue
            
            x_center = int(row['x-coordinate'])
            y_center = int(row['y-coordinate'])
            
            # Convert to YOLO format (normalized coordinates)
            x_center_norm = x_center / img_width
            y_center_norm = y_center / img_height
            width_norm = BALL_WIDTH / img_width
            height_norm = BALL_HEIGHT / img_height
            
            # Create UNIQUE filename to avoid collisions
            # Use prefix (e.g., "game1_Clip1_") to make unique
            unique_name = f"{prefix}_{Path(filename).stem}"
            
            # Create YOLO label file
            label_filename = unique_name + ".txt"
            label_path = output_labels_dir / label_filename
            
            with open(label_path, 'w') as label_file:
                label_file.write(f"{CLASS_ID} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}\n")
            
            # Copy image with unique name
            src_image = images_dir / filename
            if src_image.exists():
                dst_image = output_images_dir / (unique_name + ".jpg")
                if not dst_image.exists():
                    shutil.copy2(src_image, dst_image)
                converted_count += 1
    
    return converted_count

def main():
    print(f"TrackNet → YOLO Converter (Fixed)")
    print(f"=" * 40)
    print(f"Input:  {DATASET_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Create output directories
    (OUTPUT_DIR / "images" / "train").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "images" / "val").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
    # Find all Label.csv files
    label_files = sorted(DATASET_DIR.glob("**/Label.csv"))
    print(f"Found {len(label_files)} Label.csv files")
    print()
    
    total_converted = 0
    
    # Process each clip - use unique prefix for each
    for i, label_file in enumerate(label_files):
        clip_dir = label_file.parent
        images_dir = clip_dir
        game_name = clip_dir.parent.name
        clip_name = clip_dir.name
        
        # Create unique prefix from game and clip name
        prefix = f"{game_name}_{clip_name}"
        print(f"Processing: {prefix}...")
        
        # Split: 80% train, 20% val (by game to avoid data leakage)
        is_train = i % 5 != 0  # 4/5 = 80% train
        split = "train" if is_train else "val"
        
        output_images_dir = OUTPUT_DIR / "images" / split
        output_labels_dir = OUTPUT_DIR / "labels" / split
        
        count = convert_tracknet_to_yolo(
            label_file, 
            images_dir, 
            output_images_dir, 
            output_labels_dir,
            prefix
        )
        total_converted += count
        print(f"  Converted {count} annotations ({split})")
    
    print()
    print(f"=" * 40)
    print(f"Total: {total_converted} ball annotations converted")
    print()
    
    # Create data.yaml for YOLO training
    yaml_content = f"""# Tennis Ball Detection Dataset
# Converted from TrackNet Tennisi

path: {OUTPUT_DIR}
train: images/train
val: images/val

# Classes
names:
  0: ball

# Number of classes
nc: 1
"""
    
    yaml_path = OUTPUT_DIR / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Created: {yaml_path}")
    print()
    print("Now images have unique names like: game1_Clip1_0000.jpg")

if __name__ == "__main__":
    main()
