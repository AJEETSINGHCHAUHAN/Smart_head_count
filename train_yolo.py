from ultralytics import YOLO

model = YOLO('yolov8s.pt')  # Using small model for accuracy/speed balance

model.train(
    data='people_dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=8,
    name='people_counting_only_humans',
    pretrained=True
)
