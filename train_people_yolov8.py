# train_people_yolov8.py

from ultralytics import YOLO

# Load the pre-trained YOLOv8n model
model = YOLO('yolov8s.pt')  # You can also try 'yolov8s.pt' for better accuracy

# Train on your custom dataset
model.train(
    data='people_dataset/data.yaml',  # Path to your dataset config
    epochs=50,                        # You can increase for better results
    imgsz=640,                        # Image size (can be adjusted)
    batch=16,                         # You can tune this based on your GPU
    project='runs',                   # Folder to save results
    name='people_train',              # Subfolder name
    verbose=True
)
