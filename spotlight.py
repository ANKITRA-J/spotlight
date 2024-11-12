# windows/spotlight.py
import cv2
import mediapipe as mp
import numpy as np
import pyvirtualcam


class Spotlight:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    def start_camera(self):
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                cx, cy = x + w // 2, y + h // 2
                crop_size = int(max(w, h) * 1.8)
                x1, y1 = max(cx - crop_size // 2, 0), max(cy - crop_size // 2, 0)
                x2, y2 = min(cx + crop_size // 2, iw), min(cy + crop_size // 2, ih)

                cropped_frame = frame[y1:y2, x1:x2]
                if cropped_frame.size > 0:
                    frame = cv2.resize(cropped_frame, (iw, ih))

        return frame

    def release(self):
        self.cap.release()
