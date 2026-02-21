# Tennis Ball Tracker

YOLO-based tennis ball detection from TrackNet dataset.

## Kaggle API Setup

1. Go to https://www.kaggle.com/settings
2. Click "Generate New Token" under "API" section
3. Save the token to `~/.kaggle/access_token`:

   ```bash
   mkdir -p ~/.kaggle
   # Copy the token (starts with KGAT_...) from Kaggle settings page
   echo "your_token_here" > ~/.kaggle/access_token
   chmod 600 ~/.kaggle/access_token
   ```

## Training Data Preparation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
# kagglehub: for downloading dataset from Kaggle (required)
# ultralytics: only needed for training, not data preparation
pip install kagglehub

# Convert TrackNet to YOLO format
# This automatically downloads the dataset from Kaggle
# Output goes to data/tennis_yolo/
python3 convert_tracknet_to_yolo.py
```

Dataset: https://www.kaggle.com/datasets/sofuskonglevull/tracknet-tennis

## Cloud Sharing

```bash
# Zip the data folder
zip -r data.zip data/
```

## Training

```bash
# Train YOLO11s
yolo detect train data=data/tennis_yolo/data.yaml model=yolo11s.pt epochs=100 imgsz=1280
```

## Project Structure

```
tennis-tracker/
├── convert_tracknet_to_yolo.py  # Dataset conversion script
├── data/
│   └── tennis_yolo/             # YOLO format dataset
│       ├── data.yaml
│       ├── images/train/
│       ├── images/val/
│       ├── labels/train/
│       └── labels/val/
└── models/                       # Trained models
```

## Notes

- Images are 1280x720 (720p)
- Bounding box: 20x20 pixels around ball center
- 80/20 train/val split by clip

## Cleanup

```bash
# Remove cached Kaggle dataset (~2.4GB)
rm -rf ~/.cache/kagglehub/datasets/sofuskonglevoll/
```
