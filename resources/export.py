import sys
from ultralytics import YOLO

# Download pretrained models from https://github.com/ultralytics/ultralytics
# Load a pretrained model from Segmentation 
model = YOLO(sys.argv[1])

# Use the model, exporting the .pt pretrained model to ONNX format
model.export(format="onnx", imgsz=640)

# Run script with example: python export.py yolov8n-seg.pt
# To generate yolov8n-seg.onnx
# Note: 8n is the smallled size for performance considerations
# See for more info: https://docs.ultralytics.com/usage/python/