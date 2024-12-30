# Left Turn Box Detection Project

This project aims to detect left turn boxes in intersections using satellite imagery from Google Maps. The system uses YOLOv11 for object detection and provides a web interface for visualization.

## Project Structure

```
.
├── crawler.py                 # Google Maps image crawler
├── training/                  # Model training code
├── inferencing/              # Model inference code
├── DeployCode/              # Web deployment code (all points)
└── DeployHsinChuDist/       # Web deployment code (Hsinchu specific)
```

## 1. Data Collection (Crawler)

The `crawler.py` script downloads satellite images from Google Maps based on provided coordinates. It supports downloading multiple images per location with different viewing angles.

### Prerequisites
- Google Maps API key (set in `.env` file)
- Coordinate data in CSV format
- API usage limit: ~20,000 images per day/per API key

### Image Parameters
- viewpoint: Latitude and longitude coordinates
- heading: 0-360 degrees (0 = North, clockwise rotation)
- pitch: -90 to 90 degrees (0 = horizontal)
- fov (Field of View): 10-100 degrees (default: 90)

### Usage
1. Copy `.env.example` to `.env` and set your Google Maps API key as `GCP_MAP_API_KEY`
2. Prepare coordinate CSV files in the format found in `public_railway/` and `public_HsinChu/`
3. Run the crawler:
```bash
python crawler.py
```

The script will:
- Download 5 images per location (at different angles)
- Add random delays between requests (1-3 seconds)
- Save images to `HighSpeedRailwayCollection` directory

## 2. Model Training

The training process uses YOLOv11 to detect left turn boxes in intersection images. The model is optimized for small object detection in satellite imagery.

### Training Configuration
- Base model: YOLOv11x
- Image size: 800x800
- Batch size: 64
- Epochs: 300
- Learning rate: 1e-3 to 1e-6
- Data augmentation:
  - Mosaic probability: 0.5
  - Rotation: ±5 degrees
  - HSV augmentation
  - No mixup

### Training Data Preparation
1. Use `split_images.py` to prepare the dataset:
```bash
python split_images.py
```

2. Training process is managed by `training/training.py`:
```bash
python training/training.py
```

### Monitoring
- GPU usage can be monitored using:
```bash
python GPU_util_tracer.py
```
- Training metrics are saved every 10 epochs
- Early stopping patience: 50 epochs

## 3. Model Inference

The trained model can be used for inference on new images, particularly tested on the Hsinchu High Speed Rail Station area. The inference script supports GPU acceleration and provides detailed detection results.

### Inference Features
- GPU acceleration support
- Configurable confidence threshold (recommended: 0.3-0.7)
- Natural sorting of image files
- Separate storage for labeled and unlabeled results
- YOLO format annotation output

### Output Organization
- labeled_image_dir: Images with detected left turn boxes
- labeled_txt_dir: YOLO format annotations
- unlabeled_image_dir: Images without detections
- unlabeled_txt_dir: Empty annotation files

### Running Inference
```bash
python inferencing/inference.py
```

The script will:
1. Prompt for confidence threshold
2. Process images sequentially
3. Display detection results
4. Generate statistics on detection rate

## 4. Web Deployment

The project includes two deployment versions:

### All Points Version (DeployCode/)
```bash
cd DeployCode
docker build -t leftbox-detector .
docker run -p 8080:8080 leftbox-detector
```

### Hsinchu-Specific Version (DeployHsinChuDist/)
```bash
cd DeployHsinChuDist
docker build -t hsinchu-detector .
docker run -p 8080:8080 hsinchu-detector
```

Both versions provide a web interface for visualizing detection results.

## Data Files

- `public_HsinChu/`: Coordinate data for Hsinchu City districts
- `public_railway/`: Coordinate data for High Speed Rail Station area
- `annotation.zip`: Annotated training images
- `labeled_HsinChu.zip`: Labeled images for Hsinchu area
- `training_dataset.zip`: Complete training dataset

## Environment Setup

1. Create a virtual environment (recommended)
2. Install dependencies
3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Set required API keys and configurations

## Notes

- The system is optimized for detecting left turn boxes in intersection satellite imagery
- Training data includes various intersection types from different areas
- The web interface provides an intuitive way to visualize detection results
- Docker deployment ensures consistent environment across different platforms
