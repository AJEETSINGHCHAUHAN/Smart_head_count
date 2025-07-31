import cv2
from yolov8_infer import detect_persons

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        # Optional: To record
        self.writer = cv2.VideoWriter('output.avi',
                                      cv2.VideoWriter_fourcc(*'XVID'),
                                      20.0,
                                      (640, 480))

    def __del__(self):
        self.video.release()
        self.writer.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None, 0

        count, frame = detect_persons(frame)
        self.writer.write(frame)  # Optional recording
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), count
