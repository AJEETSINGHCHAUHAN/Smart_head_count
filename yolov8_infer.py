from ultralytics import YOLO
import cv2

# Load YOLOv8n model
model = YOLO("yolov8s.pt")

PERSON_CLASS_ID = 0

def detect_persons(frame):
    results = model.predict(source=frame, imgsz=640, conf=0.5, verbose=False)
    boxes = results[0].boxes

    count = 0
    for box in boxes:
        cls_id = int(box.cls.item())
        conf = float(box.conf.item())

        if cls_id == PERSON_CLASS_ID and conf > 0.5:
            count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(frame, f"Persons: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return count, frame

def get_person_count(frame):
    count, _ = detect_persons(frame)
    return count
